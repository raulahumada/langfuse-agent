"""Agente LangChain que consume dos MCP: el propio (Langfuse) y el oficial de GitHub."""

from __future__ import annotations

import sys
from typing import Any

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from .settings import AgentSettings

SYSTEM_PROMPT = """Sos un agente de operaciones (SRE) para una app observada con Langfuse.
- Para diagnosticar usá el MCP de Langfuse: get_health, get_metrics, diagnose_errors (primero para errores), list_logs, get_trace_logs.
- Para errores usá diagnose_errors y presentá cada incidente así: **Qué falla** (operación + mensaje + tipo de excepción),
  **Dónde** (archivo:línea), **Impacto** (conteo, trazas, % de error, desde/hasta), **Causa probable**, **Ejemplo** (input y trace id) y **Fix sugerido**.
  Ordená por impacto y distinguí bugs de código (KeyError, etc.) de errores esperables de negocio (sin stock).
- Formateá SIEMPRE las respuestas en Markdown: títulos (##), listas, tablas para métricas, `código inline`,
  y bloques de código con lenguaje (```python, ```diff) para cualquier fragmento de código o cambio propuesto.
  Para cambios usá ```diff con las líneas -/+ y mencioná el archivo.
- Las tools de Langfuse miran una ventana de tiempo (since_minutes, por defecto 60). Si el usuario no indica
  período, usá get_overview con since_minutes=10080 (7 días), igual que el dashboard, y decí siempre qué ventana usaste.
  Si el usuario pide un período explícito (última hora, 24 h, etc.), usá EXACTAMENTE ese período, hacé una sola
  llamada y respondé con eso, aunque dé 0: decí "en ese período no hubo actividad" y ofrecé ampliarlo, sin ampliarlo vos.
  Nunca repitas la misma tool con ventanas distintas en una misma respuesta salvo que el usuario lo pida.
- Respondé en español, conciso, con números concretos (conteos, latencias, costos).
- Si detectás un fallo con causa en el código, leé el repo con las tools de GitHub (solo el repo {repo}),
  y si el arreglo es claro, creá una rama, commit y un Pull Request que cite la evidencia (trace ids, conteos).
- Nunca hagas merge ni pushees a la rama principal. Antes de abrir un PR, explicá brevemente qué vas a cambiar."""


# Guardrail duro: el agente puede proponer PRs pero no mergear ni borrar.
BLOCKED_TOOLS = {"merge_pull_request", "delete_file", "create_repository", "fork_repository"}


def build_connections(s: AgentSettings) -> dict[str, Any]:
    """Define los dos servidores MCP a los que se conecta el agente (Langfuse por stdio, GitHub por HTTP)."""
    return {
        # MCP propio, por stdio (hereda el entorno para leer LANGFUSE_*)
        "langfuse": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "mcp_langfuse"],
        },
        # MCP externo (oficial de GitHub, remoto)
        "github": {
            "transport": "streamable_http",
            "url": s.github_mcp_url,
            "headers": {
                "Authorization": f"Bearer {s.github_personal_access_token.get_secret_value()}",
                "X-MCP-Toolsets": "repos,pull_requests",
            },
        },
    }


async def build_agent(s: AgentSettings | None = None):
    """Conecta los MCP, filtra tools bloqueadas y devuelve (agente LangChain, lista de tools)."""
    s = s or AgentSettings()  # type: ignore[call-arg]
    client = MultiServerMCPClient(build_connections(s))
    tools = [t for t in await client.get_tools() if t.name not in BLOCKED_TOOLS]
    model = ChatOpenAI(model=s.openai_model, api_key=s.openai_api_key)
    return create_agent(model, tools, system_prompt=SYSTEM_PROMPT.format(repo=s.github_repo or "(sin configurar)")), tools
