# Agente y API

## Agente (`api/agent.py`)

Se construye con `langchain.agents.create_agent` (LangChain 1.x, ejecutado sobre LangGraph):

```python
model = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)
agent = create_agent(model, tools, system_prompt=SYSTEM_PROMPT)
```

- **Proveedor:** OpenAI vía `langchain-openai`; el modelo sale de `OPENAI_MODEL` (default `gpt-4.1`).
- **Tools:** las de los dos MCP, menos las bloqueadas.
- **Patrón:** *tool-calling loop*. El modelo decide qué tool llamar, recibe el resultado y repite hasta responder.

### Prompt del sistema (resumen)

- Rol: agente SRE de una app observada con Langfuse.
- Para errores, usar **`diagnose_errors` primero** y presentar cada incidente como: *Qué falla · Dónde · Impacto · Causa probable · Ejemplo · Fix sugerido*.
- Ordenar por impacto y **distinguir bugs de código** (cupón en minúscula) **de errores de negocio esperables** (sin stock).
- Responder siempre en **Markdown**, con tablas para métricas y bloques ` ```diff ` para cambios.
- Si la causa está en el código: leer el repo `GITHUB_REPO` con GitHub MCP y, si el fix es claro, crear rama, commit y **Pull Request** citando trace ids y conteos.
- **Nunca** mergear ni pushear a la rama principal; explicar el cambio antes de abrir el PR.

### Guardrails (defensa en capas)

| Capa | Mecanismo |
|---|---|
| Código | `BLOCKED_TOOLS` quita `merge_pull_request`, `delete_file`, `create_repository`, `fork_repository` |
| Protocolo | `X-MCP-Toolsets: repos,pull_requests` limita lo que GitHub publica |
| Permisos | Token fine-grained de un solo repo |
| Prompt | Solo el repo configurado; sin push a `main` |
| Proceso | El merge lo hace una persona |

### Configuración (`api/settings.py`)

| Variable | Uso |
|---|---|
| `OPENAI_API_KEY` | Clave del modelo (`SecretStr`) |
| `OPENAI_MODEL` | Modelo, default `gpt-4.1` |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Autenticación contra el MCP de GitHub |
| `GITHUB_REPO` | `owner/repo` donde puede proponer PRs |
| `LANGFUSE_*` | Las lee el subproceso del MCP propio (hereda el entorno) |
| `WEB_ORIGIN` | Orígenes CORS permitidos (default `http://localhost:3001`) |

---

## API (`api/main.py`, FastAPI)

El agente y las conexiones MCP se inicializan **una vez** en el `lifespan` y se guardan en `app.state`.

### `GET /tools`
Lista los nombres de las tools cargadas. Sirve de *healthcheck* de ambos MCP.

### `POST /chat`

Request:
```json
{ "messages": [ { "role": "user", "content": "¿Qué errores hubo?" } ] }
```

Response: `text/event-stream` (SSE). El front envía el historial completo en cada turno.

| Evento | Payload | Cuándo |
|---|---|---|
| `tool_call` | `{name, args}` | El modelo decide llamar una tool |
| `tool_result` | `{name, content}` | La tool respondió (texto aplanado, hasta 6000 caracteres) |
| `message` | `{content}` | Respuesta final del modelo (Markdown) |
| `error` | `{message}` | Excepción durante la ejecución |
| `usage` | `{input_tokens, output_tokens, cost}` | Tokens y costo de cada paso del modelo |
| `tool_usage` | `{id, name, input_tokens, output_tokens, cost, duration_ms}` | Consumo atribuido a una tool (llega en el paso siguiente) |
| `turn_usage` | `{input_tokens, output_tokens, cost, base_*, tools[]}` | Resumen del turno |
| `done` | `{}` | Fin del stream |

Se usa `agent.astream(..., stream_mode="updates")`: cada actualización del grafo se traduce a un evento.

Ejemplo:
```bash
curl -N localhost:8000/chat -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"¿Cómo está Langfuse?"}]}'
```

### Consumo y costo (`api/costs.py`)

Las tools no cuestan por sí mismas; cuestan los tokens del modelo. `TurnMeter` lee `usage_metadata` de cada respuesta y estima el consumo por tool:

- **Salida:** los tokens con que el modelo decidió llamar a la tool (repartidos entre las llamadas del paso).
- **Entrada:** el resultado de la tool que el modelo relee en el paso siguiente, ≈ `input_siguiente − input_anterior − output_anterior`, repartido por tamaño de resultado.
- Lo no atribuido (prompt, historial, respuesta final) es el *contexto base*.

El costo usa `OPENAI_PRICE_IN_PER_M` y `OPENAI_PRICE_OUT_PER_M` (USD por millón de tokens). Sin ellos solo se muestran tokens. Es una estimación, no una factura. Los eventos `tool_call` y `tool_result` ahora llevan `id`, así que el front empareja llamadas paralelas sin cruzarlas.
