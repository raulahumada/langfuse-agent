# Arquitectura

## Objetivo

Que un agente de IA pueda **observar** una aplicación real (salud, logs, métricas), **diagnosticar** fallos y **actuar** (proponer un PR), usando **MCP** como contrato estándar entre el agente y cada sistema externo.

## Vista general

```mermaid
flowchart LR
  subgraph Producto["Producto observado"]
    APP["humai-business-app<br/>(e-commerce, Python)<br/>@observe"]
  end
  subgraph Obs["Observabilidad"]
    LF["Langfuse v4<br/>:3000<br/>(Docker/Kiri)"]
  end
  subgraph Ops["langfuse-ops"]
    WEB["Next.js :3001<br/>shadcn + AI Elements"]
    API["FastAPI :8000<br/>POST /chat (SSE)"]
    AG["Agente LangChain<br/>create_agent + OpenAI"]
    MCPL["MCP propio<br/>mcp_langfuse (FastMCP)"]
  end
  GHMCP["MCP GitHub<br/>(oficial, remoto)"]
  GH["GitHub<br/>humai-business-app"]

  APP -- "trazas OTel" --> LF
  WEB -- "HTTP + SSE" --> API
  API --> AG
  AG -- "stdio" --> MCPL
  AG -- "streamable HTTP" --> GHMCP
  MCPL -- "API pública REST" --> LF
  GHMCP --> GH
```

## Capas

| # | Capa | Carpeta / repo | Responsabilidad |
|---|---|---|---|
| 1 | Producto observado | `humai-business-app` | Genera trazas, spans y errores reales con el SDK de Langfuse |
| 2 | Observabilidad | `infra/` | Langfuse v4 autoalojado: recibe, almacena y expone las trazas |
| 3 | **MCP propio** | `mcp_langfuse/` | Traduce la API de Langfuse a *tools* que un agente entiende |
| 4 | **MCP externo** | GitHub (remoto) | Acciones sobre el repo: leer código, ramas, commits, PRs |
| 5 | Agente | `api/agent.py` | Razona, decide qué tools llamar, redacta el diagnóstico |
| 6 | API | `api/main.py` | Expone el agente por HTTP con streaming de eventos |
| 7 | Frontend | `web/` | Chat agéntico que muestra respuestas y llamadas a tools |

## Flujo de una consulta

```mermaid
sequenceDiagram
  actor U as Usuario
  participant W as Next.js
  participant A as FastAPI
  participant G as Agente (OpenAI)
  participant L as MCP Langfuse
  participant H as MCP GitHub
  U->>W: "Revisá los errores y proponé un PR"
  W->>A: POST /chat {messages}
  A->>G: astream(messages)
  G->>L: diagnose_errors(since_minutes=60)
  L-->>G: incidentes agrupados (código, ubicación, contexto)
  A-->>W: SSE tool_call / tool_result
  G->>H: get_file_contents(pricing.py)
  H-->>G: código fuente
  G->>H: create_branch → create_or_update_file → create_pull_request
  H-->>G: URL del PR
  A-->>W: SSE message (markdown con diff)
  W-->>U: respuesta + PR propuesto
```

## Del error al PR (end to end)

1. `traffic.py` simula compras. `checkout()` falla con `InvalidCoupon` si el cupón viene en minúscula.
2. `report_error()` marca el span con `level=ERROR` y metadata: `error.code`, `error.type`, `error.location`, `error.stacktrace`, `error.context`.
3. Langfuse guarda la observación.
4. `diagnose_errors` (MCP propio) lee los errores, **colapsa** los spans anidados de un mismo trace y **agrupa** por operación + código. Devuelve conteo, ubicación `pricing.py:14 en apply_discount`, contexto y trace ids de ejemplo.
5. El agente lee `pricing.py` con el MCP de GitHub, propone el fix y abre un PR citando la evidencia.
6. Una persona revisa y hace el merge.

## Decisiones de diseño

- **MCP como frontera.** El agente no conoce la API de Langfuse ni la de GitHub: solo ve tools con schema. Cambiar de backend de observabilidad implica reescribir solo `mcp_langfuse`.
- **Propio + externo.** Lo propio donde no existe un MCP (Langfuse v4); lo externo donde ya hay uno oficial (GitHub).
- **Solo lectura en el MCP propio.** El agente observa; las escrituras pasan por GitHub y bajo guardrails.
- **Capas limpias en el MCP:** `config` → `client` → `diagnostics` → `server`. La lógica de negocio (`diagnostics.py`) es pura y testeable sin red.
- **Inyección de dependencias.** `build_server(client)` acepta un cliente falso, así los tests corren en memoria.
- **Human in the loop.** El agente propone, la persona aprueba el merge.
- **Streaming por SSE.** El front muestra cada tool call en vivo.

## Puertos

| Servicio | Puerto |
|---|---|
| Langfuse | 3000 |
| Frontend Next.js | 3001 |
| API FastAPI | 8000 |
| MCP propio por HTTP (opcional) | 8765 |

## Límites conocidos

- Langfuse v4 corre en modo *events_only*: no existen `/traces`, `/observations` ni `/metrics/daily` v1. Se usan `v2/observations` y `v2/metrics`.
- Los `tool_call` del stream no llevan id; el front empareja resultados por nombre de tool (puede cruzarse con llamadas paralelas a la misma tool).
- El agente no tiene memoria entre sesiones; el historial lo mantiene el front.
