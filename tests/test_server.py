import httpx
import pytest
from fastmcp import Client
from pydantic import SecretStr

from mcp_langfuse.client import LangfuseClient
from mcp_langfuse.config import Settings
from mcp_langfuse.server import build_server


# Helper: cliente de Langfuse falso que responde con `handler`, sin red.
def make_client(handler) -> LangfuseClient:
    settings = Settings(public_key="pk", secret_key=SecretStr("sk"))
    return LangfuseClient(settings, transport=httpx.MockTransport(handler))


async def test_lists_expected_tools():
    """El servidor MCP expone exactamente las 7 tools esperadas."""
    server = build_server(make_client(lambda r: httpx.Response(200, json={})))
    async with Client(server) as c:
        names = {t.name for t in await c.list_tools()}
    assert names == {"get_health", "list_logs", "get_trace_logs", "get_metrics", "get_error_summary", "diagnose_errors", "get_overview"}


async def test_get_health_ok():
    """get_health devuelve ok=True cuando Langfuse responde 200."""
    server = build_server(make_client(lambda r: httpx.Response(200, json={"status": "OK"})))
    async with Client(server) as c:
        res = await c.call_tool("get_health", {})
    assert res.data["ok"] is True


async def test_list_logs_filters_by_level():
    """list_logs envía el filtro de nivel a la API de Langfuse."""
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen.update(req.url.params)
        return httpx.Response(200, json={"data": []})

    async with Client(build_server(make_client(handler))) as c:
        await c.call_tool("list_logs", {"level": "ERROR"})
    assert seen["level"] == "ERROR"


async def test_api_error_is_returned_not_raised():
    """Un error HTTP de Langfuse vuelve como {'error': ...} en vez de romper la tool."""
    server = build_server(make_client(lambda r: httpx.Response(500, text="boom")))
    async with Client(server) as c:
        res = await c.call_tool("get_metrics", {})
    assert "500" in res.data["error"]


async def test_invalid_args_rejected():
    """Argumentos fuera del esquema (nivel inválido) son rechazados."""
    server = build_server(make_client(lambda r: httpx.Response(200, json={})))
    async with Client(server) as c:
        with pytest.raises(Exception):
            await c.call_tool("list_logs", {"level": "NOPE"})
