import json
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

from .agent import build_agent  # noqa: E402
from .costs import TurnMeter  # noqa: E402
from .dashboard import to_openui  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from mcp_langfuse.client import LangfuseClient, LangfuseError  # noqa: E402
from mcp_langfuse.config import Settings  # noqa: E402
from mcp_langfuse.overview import overview  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Al arrancar la API construye el agente y sus tools una sola vez."""
    app.state.agent, app.state.tools = await build_agent()
    yield


app = FastAPI(title="langfuse-ops", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("WEB_ORIGIN", "http://localhost:3001").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    """Un mensaje del historial de chat (role: user/assistant)."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Cuerpo de POST /chat: historial completo de la conversación."""

    messages: list[Message]


@app.get("/dashboard")
async def dashboard(since_minutes: int = 60):
    """Dashboard de Langfuse como OpenUI Lang, armado con la misma lógica que la tool MCP `get_overview`."""
    since_minutes = max(1, min(since_minutes, 60 * 24 * 14))
    lf = LangfuseClient(Settings())  # type: ignore[call-arg]
    try:
        data = await overview(lf, since_minutes)
    except LangfuseError as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)
    finally:
        await lf.aclose()
    return {"openui": to_openui(data), "since_minutes": since_minutes}


@app.get("/tools")
async def tools():
    """Lista los nombres de las tools MCP disponibles para el agente."""
    return [t.name for t in app.state.tools]


def _text(content) -> str:
    """Aplana el contenido de un ToolMessage (puede ser lista de bloques) a texto."""
    if isinstance(content, list):
        return "".join(
            (b.get("text", "") if b.get("type", "text") == "text" else "") if isinstance(b, dict) else str(b)
            for b in content
        )
    return str(content)


def _sse(event: str, data: dict) -> str:
    """Formatea un evento Server-Sent Events (event + data JSON)."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat")
async def chat(req: ChatRequest):
    """Ejecuta el agente y transmite por SSE las tool calls, resultados, uso de tokens y respuesta final."""
    async def stream():
        """Generador SSE: traduce cada paso del agente a eventos para el front."""
        meter = TurnMeter()
        started: dict[str, float] = {}
        try:
            async for chunk in app.state.agent.astream(
                {"messages": [m.model_dump() for m in req.messages]}, stream_mode="updates"
            ):
                for node in chunk.values():
                    for msg in (node or {}).get("messages", []):
                        if msg.type == "ai":
                            um = getattr(msg, "usage_metadata", None) or {}
                            calls = [(tc.get("id") or tc["name"], tc["name"]) for tc in msg.tool_calls]
                            for u in meter.on_ai_step(um.get("input_tokens", 0), um.get("output_tokens", 0), calls):
                                yield _sse("tool_usage", u)
                            yield _sse("usage", {
                                "input_tokens": um.get("input_tokens", 0),
                                "output_tokens": um.get("output_tokens", 0),
                                "cost": meter.prices.cost(um.get("input_tokens", 0), um.get("output_tokens", 0)),
                            })
                            for tc in msg.tool_calls:
                                cid = tc.get("id") or tc["name"]
                                started[cid] = time.monotonic()
                                yield _sse("tool_call", {"id": cid, "name": tc["name"], "args": tc["args"]})
                            answer = _text(msg.content)
                            if answer.strip() and not msg.tool_calls:
                                yield _sse("message", {"content": answer})
                        elif msg.type == "tool":
                            cid = getattr(msg, "tool_call_id", None) or msg.name
                            text = _text(msg.content)
                            ms = round((time.monotonic() - started.get(cid, time.monotonic())) * 1000)
                            meter.record_result(cid, len(text), ms)
                            yield _sse("tool_result", {"id": cid, "name": msg.name, "content": text[:6000], "duration_ms": ms})
            for u in meter.flush():
                yield _sse("tool_usage", u)
        except Exception as exc:  # noqa: BLE001
            yield _sse("error", {"message": repr(exc)})
        yield _sse("turn_usage", meter.summary())
        yield _sse("done", {})

    return StreamingResponse(stream(), media_type="text/event-stream")
