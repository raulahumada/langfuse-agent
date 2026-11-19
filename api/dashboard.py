"""Convierte el resumen de Langfuse (`mcp_langfuse.overview`) en OpenUI Lang.

El dashboard se arma de forma determinista, sin modelo: el front lo dibuja con
`@openuidev/dashboard-library` y `Renderer` de `@openuidev/react-lang`.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def _j(v: Any) -> str:
    """Serializa a JSON (sin escapar tildes) para incrustarlo en el código OpenUI Lang."""
    return json.dumps(v, ensure_ascii=False)


def _label(ts: str, granularity: str) -> str:
    """Etiqueta del eje X: día/mes o hora:minuto según la granularidad."""
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.strftime("%d/%m") if granularity == "day" else dt.strftime("%H:%M")


def _window(minutes: int) -> str:
    """Texto legible de la ventana de tiempo ('última hora', 'últimos 7 días'...)."""
    if minutes % 1440 == 0:
        return f"últimos {minutes // 1440} días" if minutes > 1440 else "últimas 24 h"
    if minutes % 60 == 0:
        return f"última hora" if minutes == 60 else f"últimas {minutes // 60} h"
    return f"últimos {minutes} min"


def to_openui(o: dict[str, Any]) -> str:
    """Genera el dashboard (KPIs, tendencia, operaciones, incidentes) a partir del resumen de Langfuse."""
    total = o["total_observations"]
    errors = o["error_observations"]
    ops = o["operations"]
    incidents = o["incidents"]
    ok = bool(o["health"].get("ok"))
    rate = round(errors / total * 100, 1) if total else 0
    failed = sum(i["count"] for i in incidents)

    kpis = [
        f'Kpi("Salud de Langfuse", {_j("Operativo" if ok else "Caído")}, null, null, null, null, null, {_j("good" if ok else "bad")})',
        f'Kpi("Observaciones", {total}, "number")',
        f'Kpi("Con error", {errors}, "number", null, "down", null, null, {_j("bad" if errors else "good")})',
        f'Kpi("Tasa de error", {rate}, "percent", null, "down")',
        f'Kpi("Traces fallidos", {failed}, "number", null, "down")',
    ]
    sections = [f'Section("", [Kpis([{", ".join(kpis)}])])']

    tl = o["timeline"]
    if tl:
        labels = [_label(p["t"], o["granularity"]) for p in tl]
        card = (
            f'Card("Volumen y errores", [TimeSeries({_j(labels)}, ['
            f'Series("Total", {_j([p["total"] for p in tl])}, null, "area"), '
            f'Series("Errores", {_j([p["errors"] for p in tl])}, null, "bar")'
            f'], "line", "number")], "full", {_j("Observaciones por " + ("hora" if o["granularity"] == "hour" else "día"))})'
        )
        sections.append(f'Section("Tendencia", [Row([{card}], 320)])')

    if ops:
        names = [x["name"] for x in ops]
        lat = (
            f'Card("Latencia p95", [Bars({_j(names)}, [Series("p95", {_j([round(x["p95_ms"], 1) for x in ops])})], '
            f'"ms", "horizontal")], "half", "Milisegundos por operación")'
        )
        vol = (
            f'Card("Volumen por operación", [Donut({_j(names)}, {_j([x["count"] for x in ops])}, "number", '
            f'"Observaciones")], "half")'
        )
        table = (
            'Card("Detalle por operación", [Table(['
            f'Column("Operación", {_j(names)}, "primary"), '
            f'Column("Llamadas", {_j([x["count"] for x in ops])}, "bar", "number"), '
            f'Column("p50", {_j([round(x["p50_ms"], 1) for x in ops])}, "number", "ms"), '
            f'Column("p95", {_j([round(x["p95_ms"], 1) for x in ops])}, "number", "ms"), '
            f'Column("Tokens", {_j([x["tokens"] for x in ops])}, "number", "number")'
            '])], "full")'
        )
        sections.append(f'Section("Operaciones", [Row([{lat}, {vol}], 320), Row([{table}])])')

    if incidents:
        inc = (
            'Card("Errores agrupados", [Table(['
            f'Column("Operación", {_j([i["operation"] for i in incidents])}, "primary"), '
            f'Column("Código", {_j([i.get("error_code") or i.get("exception_type") or "—" for i in incidents])}, "badge", null, '
            '{"INVALID_COUPON": "bad", "OUT_OF_STOCK": "warning"}), '
            f'Column("Veces", {_j([i["count"] for i in incidents])}, "bar", "number"), '
            f'Column("Dónde", {_j([i.get("location") or "—" for i in incidents])}, "text"), '
            f'Column("Mensaje", {_j([i["message"] for i in incidents])}, "text")'
            '])], "full", "Una fila por tipo de error, ordenadas por frecuencia")'
        )
        sections.append(f'Section("Incidentes", [Row([{inc}])])')

    return f"root = Dashboard([{', '.join(sections)}])\n"
