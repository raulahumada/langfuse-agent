"""Cliente HTTP mínimo y tipado sobre la API pública de Langfuse (v4)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from .config import Settings


class LangfuseError(RuntimeError):
    """Error legible de la API de Langfuse (se muestra tal cual al agente)."""


def _iso(dt: datetime) -> str:
    """Convierte un datetime a ISO-8601 UTC con milisegundos y sufijo Z (formato que pide Langfuse)."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class LangfuseClient:
    """Cliente async de la API pública de Langfuse: salud, observaciones (logs) y métricas."""

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self._http = httpx.AsyncClient(
            base_url=settings.host.rstrip("/") + "/api/public",
            auth=(settings.public_key, settings.secret_key.get_secret_value()),
            timeout=settings.timeout_s,
            transport=transport,
        )

    async def aclose(self) -> None:
        """Cierra la conexión HTTP subyacente."""
        await self._http.aclose()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET autenticado: descarta params nulos y convierte fallos de red/HTTP en LangfuseError."""
        try:
            resp = await self._http.get(path, params={k: v for k, v in (params or {}).items() if v is not None})
        except httpx.HTTPError as exc:
            raise LangfuseError(f"No se pudo conectar a Langfuse: {exc!r}") from exc
        if resp.status_code >= 400:
            raise LangfuseError(f"Langfuse respondió {resp.status_code} en {path}: {resp.text[:300]}")
        return resp.json()

    async def health(self) -> dict[str, Any]:
        """Liveness (`health`) + readiness (`ready`) de la instancia."""
        out: dict[str, Any] = {}
        for name in ("health", "ready"):
            try:
                resp = await self._http.get(f"/{name}")
                out[name] = {"status_code": resp.status_code, "body": resp.json() if resp.content else None}
            except httpx.HTTPError as exc:
                out[name] = {"status_code": None, "error": repr(exc)}
        out["ok"] = all(v.get("status_code") == 200 for v in out.values() if isinstance(v, dict))
        return out

    async def observations(
        self,
        *,
        level: str | None = None,
        name: str | None = None,
        trace_id: str | None = None,
        since_minutes: int = 60,
        limit: int = 50,
        cursor: str | None = None,
        fields: str = "core,basic,time,io,usage",
    ) -> dict[str, Any]:
        """Lista observaciones (spans/generations/eventos) de la ventana, filtrando por nivel, nombre o trace."""
        now = datetime.now(timezone.utc)
        return await self._get(
            "/v2/observations",
            {
                "fromStartTime": _iso(now - timedelta(minutes=since_minutes)),
                "level": level,
                "name": name,
                "traceId": trace_id,
                "limit": limit,
                "cursor": cursor,
                "fields": fields,
            },
        )

    async def metrics(
        self,
        *,
        metrics: list[dict[str, str]],
        dimensions: list[str] | None = None,
        filters: list[dict[str, Any]] | None = None,
        since_minutes: int = 60,
        view: str = "observations",
        time_granularity: str | None = None,
    ) -> dict[str, Any]:
        """Consulta agregada (/v2/metrics): conteo, latencia, costo, tokens, agrupable por dimensiones."""
        now = datetime.now(timezone.utc)
        query: dict[str, Any] = {
            "view": view,
            "metrics": metrics,
            "dimensions": [{"field": d} for d in dimensions or []],
            "filters": filters or [],
            "fromTimestamp": _iso(now - timedelta(minutes=since_minutes)),
            "toTimestamp": _iso(now),
        }
        if time_granularity:
            query["timeDimension"] = {"granularity": time_granularity}
        return await self._get("/v2/metrics", {"query": json.dumps(query)})
