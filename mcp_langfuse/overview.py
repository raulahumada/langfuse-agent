"""Resumen único de Langfuse (salud + volumen + errores + serie temporal) para dashboards.

Lo usan la tool MCP `get_overview` y el endpoint `/dashboard` de la API: una sola fuente de verdad.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from .client import LangfuseClient
from .diagnostics import group_errors

METRICS = [
    {"measure": "count", "aggregation": "count"},
    {"measure": "latency", "aggregation": "p50"},
    {"measure": "latency", "aggregation": "p95"},
    {"measure": "totalCost", "aggregation": "sum"},
    {"measure": "totalTokens", "aggregation": "sum"},
]


def _rows(resp: dict[str, Any]) -> list[dict[str, Any]]:
    """Devuelve las filas `data` de una respuesta de métricas (lista vacía si no hay)."""
    return resp.get("data") or []


async def overview(lf: LangfuseClient, since_minutes: int = 60) -> dict[str, Any]:
    """Arma el resumen: lanza en paralelo salud, métricas por operación/nivel, serie temporal y errores."""
    granularity = "hour" if since_minutes <= 60 * 48 else "day"
    health, by_name, by_level, series, errors = await asyncio.gather(
        lf.health(),
        lf.metrics(metrics=METRICS, dimensions=["name"], since_minutes=since_minutes),
        lf.metrics(metrics=METRICS[:1], dimensions=["level"], since_minutes=since_minutes),
        lf.metrics(
            metrics=METRICS[:1], dimensions=["level"], since_minutes=since_minutes, time_granularity=granularity
        ),
        lf.observations(level="ERROR", since_minutes=since_minutes, limit=100, fields="core,basic,time,io,metadata"),
    )

    levels = {r.get("level") or "?": int(r.get("count_count") or 0) for r in _rows(by_level)}
    total = sum(levels.values())

    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "errors": 0})
    for r in _rows(series):
        b = buckets[r["time_dimension"]]
        n = int(r.get("count_count") or 0)
        b["total"] += n
        if r.get("level") == "ERROR":
            b["errors"] += n

    operations = sorted(
        (
            {
                "name": r.get("name") or "?",
                "count": int(r.get("count_count") or 0),
                "p50_ms": float(r.get("p50_latency") or 0),
                "p95_ms": float(r.get("p95_latency") or 0),
                "cost": float(r.get("sum_totalCost") or 0),
                "tokens": int(r.get("sum_totalTokens") or 0),
            }
            for r in _rows(by_name)
        ),
        key=lambda o: o["count"],
        reverse=True,
    )

    return {
        "since_minutes": since_minutes,
        "granularity": granularity,
        "health": health,
        "total_observations": total,
        "error_observations": levels.get("ERROR", 0),
        "levels": levels,
        "operations": operations,
        "timeline": [{"t": t, **v} for t, v in sorted(buckets.items())],
        "incidents": group_errors(errors.get("data", []), total)["incidents"],
    }
