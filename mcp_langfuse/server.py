"""Servidor MCP de Langfuse (FastMCP): tools de solo lectura para un agente de operaciones."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp import FastMCP
from pydantic import Field

from .client import LangfuseClient, LangfuseError
from .config import Settings
from .diagnostics import group_errors
from .overview import overview

Minutes = Annotated[int, Field(ge=1, le=60 * 24 * 14, description="Ventana hacia atrás en minutos")]
Limit = Annotated[int, Field(ge=1, le=100, description="Máximo de resultados")]

INSTRUCTIONS = (
    "Observabilidad de Langfuse en solo lectura. Empezá por get_health, luego get_metrics "
    "para el panorama y diagnose_errors para errores agrupados con causa, ubicación y ejemplos."
)


def build_server(client: LangfuseClient | None = None) -> FastMCP:
    """Construye el servidor. `client` es inyectable para tests; si no, se crea desde el entorno."""
    holder: dict[str, LangfuseClient] = {}
    if client:
        holder["lf"] = client

    def lf() -> LangfuseClient:
        """Devuelve el cliente de Langfuse, creándolo de forma perezosa la primera vez."""
        if "lf" not in holder:
            holder["lf"] = LangfuseClient(Settings())  # type: ignore[call-arg]
        return holder["lf"]

    mcp = FastMCP("langfuse-ops", instructions=INSTRUCTIONS)

    @mcp.tool(annotations={"readOnlyHint": True})
    async def get_health() -> dict[str, Any]:
        """Salud de la instancia de Langfuse (liveness y readiness) y su versión."""
        return await lf().health()

    @mcp.tool(annotations={"readOnlyHint": True})
    async def list_logs(
        level: Literal["DEBUG", "DEFAULT", "WARNING", "ERROR"] | None = None,
        name: str | None = None,
        since_minutes: Minutes = 60,
        limit: Limit = 25,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Lista observaciones (spans/generations/eventos) recientes; usá level=ERROR para ver fallos."""
        try:
            return await lf().observations(
                level=level, name=name, since_minutes=since_minutes, limit=limit, cursor=cursor
            )
        except LangfuseError as exc:
            return {"error": str(exc)}

    @mcp.tool(annotations={"readOnlyHint": True})
    async def get_trace_logs(trace_id: str, limit: Limit = 100) -> dict[str, Any]:
        """Todas las observaciones de un trace (para reconstruir qué falló y dónde)."""
        try:
            return await lf().observations(trace_id=trace_id, since_minutes=60 * 24 * 14, limit=limit)
        except LangfuseError as exc:
            return {"error": str(exc)}

    @mcp.tool(annotations={"readOnlyHint": True})
    async def get_metrics(
        since_minutes: Minutes = 60,
        group_by: Literal["name", "level", "providedModelName", "environment"] = "name",
    ) -> dict[str, Any]:
        """Volumen, latencia p50/p95, costo y tokens agrupados (por nombre, nivel, modelo o entorno)."""
        try:
            return await lf().metrics(
                metrics=[
                    {"measure": "count", "aggregation": "count"},
                    {"measure": "latency", "aggregation": "p50"},
                    {"measure": "latency", "aggregation": "p95"},
                    {"measure": "totalCost", "aggregation": "sum"},
                    {"measure": "totalTokens", "aggregation": "sum"},
                ],
                dimensions=[group_by],
                since_minutes=since_minutes,
            )
        except LangfuseError as exc:
            return {"error": str(exc)}

    @mcp.tool(annotations={"readOnlyHint": True})
    async def get_error_summary(since_minutes: Minutes = 60) -> dict[str, Any]:
        """Errores agrupados por observación y trace (el mensaje detallado se obtiene con list_logs)."""
        try:
            return await lf().metrics(
                metrics=[{"measure": "count", "aggregation": "count"}],
                dimensions=["name", "traceName"],
                filters=[{"column": "level", "operator": "=", "value": "ERROR", "type": "string"}],
                since_minutes=since_minutes,
            )
        except LangfuseError as exc:
            return {"error": str(exc)}

    @mcp.tool(annotations={"readOnlyHint": True})
    async def diagnose_errors(since_minutes: Minutes = 60) -> dict[str, Any]:
        """Informe de errores listo para diagnosticar: incidentes agrupados por operación y mensaje,
        con conteo, tasa de error, primera/última vez, tipo de excepción, ubicación en el código,
        stacktrace, input de ejemplo y trace ids."""
        try:
            errors = await lf().observations(
                level="ERROR", since_minutes=since_minutes, limit=100, fields="core,basic,time,io,metadata"
            )
            total = await lf().metrics(
                metrics=[{"measure": "count", "aggregation": "count"}], since_minutes=since_minutes
            )
            rows = total.get("data") or [{}]
            count = next((int(v) for k, v in rows[0].items() if k.startswith("count")), None)
            return group_errors(errors.get("data", []), count)
        except LangfuseError as exc:
            return {"error": str(exc)}

    @mcp.tool(annotations={"readOnlyHint": True})
    async def get_overview(since_minutes: Minutes = 60) -> dict[str, Any]:
        """Resumen para un dashboard: salud, volumen, errores por nivel, operaciones (latencia p50/p95,
        costo, tokens), serie temporal de errores e incidentes agrupados."""
        try:
            return await overview(lf(), since_minutes)
        except LangfuseError as exc:
            return {"error": str(exc)}

    return mcp
