"""Agrupa observaciones con error en incidentes accionables (lógica pura, sin red)."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

MAX_SAMPLE_CHARS = 400
APP_META_PREFIX = "error."  # metadata que la app instrumentada agrega: error.type, error.file, ...


def _short(value: Any) -> Any:
    """Parsea JSON si puede y recorta el valor a MAX_SAMPLE_CHARS para no inflar la respuesta al agente."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            pass
    text = json.dumps(value, ensure_ascii=False, default=str)
    return value if len(text) <= MAX_SAMPLE_CHARS else text[:MAX_SAMPLE_CHARS] + "…"


def _loads(v: Any) -> Any:
    """json.loads tolerante: si no es un JSON válido devuelve el valor original."""
    try:
        return json.loads(v) if isinstance(v, str) else v
    except ValueError:
        return v


def _app_meta(obs: dict[str, Any]) -> dict[str, Any]:
    """Extrae la metadata `error.*` que agrega la app instrumentada (sin el prefijo)."""
    meta = obs.get("metadata") or {}
    return {k.removeprefix(APP_META_PREFIX): v for k, v in meta.items() if k.startswith(APP_META_PREFIX)}


def group_errors(observations: list[dict[str, Any]], total_observations: int | None = None) -> dict[str, Any]:
    """Devuelve incidentes ordenados por frecuencia, con causa, ubicación, ejemplos e impacto."""
    # Una falla se propaga por los spans padres: contamos una vez por trace, con el span más informativo.
    by_trace: dict[str, dict[str, Any]] = {}
    for o in observations:
        tid = o.get("traceId") or o.get("id")
        best = by_trace.get(tid)
        if best is None or (bool(_app_meta(o)), o.get("startTime") or "") > (bool(_app_meta(best)), best.get("startTime") or ""):
            by_trace[tid] = o
    observations = list(by_trace.values())

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for o in observations:
        groups[(o.get("name") or "?", _app_meta(o).get("code") or o.get("statusMessage") or "(sin mensaje)")].append(o)

    incidents = []
    for (name, message), items in groups.items():
        items.sort(key=lambda o: o.get("startTime") or "")
        meta = next((m for m in map(_app_meta, items) if m), {})
        incidents.append(
            {
                "operation": name,
                "message": items[-1].get("statusMessage") or message,
                "distinct_contexts": sorted({str(_app_meta(o).get("context")) for o in items if _app_meta(o).get("context")})[:5],
                "count": len(items),
                                "first_seen": items[0].get("startTime"),
                "last_seen": items[-1].get("startTime"),
                "error_code": meta.get("code"),
                "exception_type": meta.get("type"),
                "context": _loads(meta.get("context")),
                "location": meta.get("location"),  # "archivo:línea en función"
                "stacktrace": meta.get("stacktrace"),
                "sample_input": _short(items[-1].get("input")),
                "sample_trace_ids": [o.get("traceId") for o in items[-3:]],
            }
        )
    incidents.sort(key=lambda i: i["count"], reverse=True)
    return {
        "failed_traces": len(observations),
        "observations_in_window": total_observations,
        "incidents": incidents,
    }
