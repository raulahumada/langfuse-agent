# MCP en este proyecto

## ¿Qué es MCP?

**Model Context Protocol** es un estándar abierto para que aplicaciones de IA se conecten a sistemas externos de forma uniforme. Un **servidor MCP** publica:

- **Tools**: funciones que el modelo puede invocar, con nombre, descripción y *JSON Schema* de argumentos.
- **Resources** y **Prompts** (no se usan acá).

Un **cliente MCP** (nuestro agente) descubre las tools en tiempo de ejecución y las ofrece al modelo. Es "USB-C para herramientas de IA": en vez de integrar cada API a mano, el agente habla un solo protocolo.

**Transportes:**
- `stdio`: el cliente lanza el servidor como subproceso. Es el que usa el MCP propio dentro de la API.
- `streamable HTTP`: servidor remoto por HTTP. Es el que usa el MCP de GitHub (y el propio con `--transport http`).

## ¿Por qué FastMCP?

[FastMCP](https://gofastmcp.com) es el framework de alto nivel para escribir servidores MCP en Python:

- Una función con *type hints* + docstring se convierte en tool; el schema se genera solo.
- Validación con Pydantic (`Literal`, `Field(ge=1, le=100)`): argumentos inválidos se rechazan antes de ejecutar.
- Anotaciones como `readOnlyHint`.
- Cliente en memoria (`fastmcp.Client(server)`) para tests sin red ni subprocesos.
- Múltiples transportes con un parámetro.

> Se usa el paquete `fastmcp` (3.x), no el `FastMCP` embebido en el SDK `mcp`. Se fija `fastmcp>=3,<4` y `mcp<2` porque `fastmcp` 4 exige `mcp` 2, que `langchain-mcp-adapters` aún no soporta.

---

## MCP propio: `mcp_langfuse`

### Estructura

```
mcp_langfuse/
├── config.py       # Settings (pydantic-settings, prefijo LANGFUSE_)
├── client.py       # LangfuseClient: httpx async tipado sobre la API pública v4
├── diagnostics.py  # group_errors(): lógica pura de agrupación (sin red)
├── server.py       # build_server(): define las tools con FastMCP
└── __main__.py     # CLI: --transport stdio|http, --host, --port
```

| Capa | Responsabilidad | Depende de |
|---|---|---|
| `config` | Variables de entorno, secretos como `SecretStr` | — |
| `client` | HTTP, auth básica, errores legibles (`LangfuseError`) | `config` |
| `diagnostics` | Colapsar spans por trace, agrupar, formatear incidentes | — |
| `server` | Exponer tools, mapear errores a `{"error": ...}` | `client`, `diagnostics` |

### Tools (todas de solo lectura)

| Tool | Para qué sirve | Endpoint de Langfuse |
|---|---|---|
| `get_health` | Liveness y readiness de la instancia | `/health`, `/ready` |
| `get_metrics` | Volumen, latencia p50/p95, costo y tokens agrupados por `name`, `level`, `providedModelName` o `environment` | `/v2/metrics` |
| `diagnose_errors` | **Informe de errores listo para diagnosticar** (ver abajo) | `/v2/observations` + `/v2/metrics` |
| `get_error_summary` | Conteo de errores por observación y trace | `/v2/metrics` |
| `list_logs` | Observaciones recientes filtrables por `level`, `name`, ventana | `/v2/observations` |
| `get_trace_logs` | Todas las observaciones de un trace | `/v2/observations` |

Argumentos comunes: `since_minutes` (1 a 20160), `limit` (1 a 100).

### `diagnose_errors` en detalle

Es la tool pensada para el agente: en vez de volcar observaciones crudas, devuelve un informe accionable.

```json
{
  "failed_traces": 31,
  "observations_in_window": 402,
  "incidents": [
    {
      "operation": "checkout",
      "message": "Cupón 'vip20' no válido. Cupones válidos: WELCOME10, VIP20 (la búsqueda distingue mayúsculas y minúsculas)",
      "count": 9,
      "error_code": "INVALID_COUPON",
      "exception_type": "InvalidCoupon",
      "context": {"coupon": "vip20", "valid": ["WELCOME10", "VIP20"]},
      "location": "pricing.py:14 en apply_discount",
      "stacktrace": "Traceback ...",
      "first_seen": "...", "last_seen": "...",
      "sample_input": {"args": [{"sku-tee": 1}, "vip20"], "kwargs": {}},
      "sample_trace_ids": ["...", "...", "..."]
    }
  ]
}
```

Qué hace `group_errors` (`diagnostics.py`):

1. **Colapsa por trace.** Una falla sube por todos los spans padres (`reserve_stock` → `checkout`). Se cuenta una vez por trace, quedándose con el span que tiene más contexto (el que trae metadata `error.*`).
2. **Agrupa** por `(operación, error.code)`; si no hay código, por mensaje. Así "cupón inválido" es un incidente aunque cambie el valor del cupón.
3. **Ordena** por frecuencia.
4. **Recorta** inputs de ejemplo a 400 caracteres.

### Contrato con la app instrumentada

El MCP lee metadata con prefijo `error.`, que la app publica con `report_error()`:

| Clave | Ejemplo |
|---|---|
| `error.code` | `INVALID_COUPON`, `OUT_OF_STOCK`, `UNEXPECTED` |
| `error.type` | `InvalidCoupon` |
| `error.location` | `pricing.py:14 en apply_discount` |
| `error.stacktrace` | Traceback (últimos 1500 caracteres) |
| `error.context` | JSON con los datos del fallo |

Una app que no publique esa metadata sigue funcionando, con menos detalle.

### Manejo de errores

El servidor nunca lanza excepciones por fallos de Langfuse: devuelve `{"error": "Langfuse respondió 500 en /v2/metrics: ..."}`. El agente puede leerlo y explicárselo al usuario. Los argumentos inválidos sí se rechazan por validación.

### Testing

- `tests/test_server.py`: lista de tools, health, filtro `level=ERROR`, error 500 devuelto (no lanzado), rechazo de argumentos inválidos. Usa `fastmcp.Client` en memoria + `httpx.MockTransport`.
- `tests/test_diagnostics.py`: agrupación, ranking y colapso de spans anidados.

```bash
.venv/bin/python -m pytest -q      # 7 tests
```

### Ejecutarlo solo

```bash
.venv/bin/python -m mcp_langfuse                                  # stdio
.venv/bin/python -m mcp_langfuse --transport http --port 8765     # HTTP
```

Para inspeccionarlo desde código:

```python
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

async with Client(StdioTransport(command=".venv/bin/python", args=["-m", "mcp_langfuse"])) as c:
    print(await c.list_tools())
    print((await c.call_tool("diagnose_errors", {"since_minutes": 60})).data)
```

---

## MCP externo: GitHub

Servidor **oficial y remoto** de GitHub: `https://api.githubcopilot.com/mcp/` (transporte *streamable HTTP*).

### Conexión

```python
"github": {
    "transport": "streamable_http",
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": {
        "Authorization": "Bearer <GITHUB_PERSONAL_ACCESS_TOKEN>",
        "X-MCP-Toolsets": "repos,pull_requests",
    },
}
```

`X-MCP-Toolsets` limita las tools publicadas a los grupos `repos` y `pull_requests`, lo que da unas **16 tools**: `get_file_contents`, `list_branches`, `create_branch`, `create_or_update_file`, `push_files`, `list_commits`, `create_pull_request`, `pull_request_read`, `update_pull_request`, `search_pull_requests`, entre otras.

### Guardrails

Aunque el token pueda escribir, el agente **no recibe** estas tools (se filtran en `api/agent.py`):

```python
BLOCKED_TOOLS = {"merge_pull_request", "delete_file", "create_repository", "fork_repository"}
```

### Permisos del token

Token *fine-grained* sobre el repo del producto: `Contents: Read and write`, `Pull requests: Read and write`, `Metadata: Read-only`. Con solo lectura, `create_branch` devuelve 403 y el agente solo puede sugerir el cambio en el chat.

---

## Cómo se combinan

`MultiServerMCPClient` (de `langchain-mcp-adapters`) abre ambas conexiones, descubre las tools y las convierte en tools de LangChain. El agente ve **una sola lista** (~23 tools) sin saber de qué servidor viene cada una:

```python
client = MultiServerMCPClient({
    "langfuse": {"transport": "stdio", "command": sys.executable, "args": ["-m", "mcp_langfuse"]},
    "github":   {"transport": "streamable_http", "url": ..., "headers": ...},
})
tools = [t for t in await client.get_tools() if t.name not in BLOCKED_TOOLS]
```

---

## Autenticación

| Transporte | Cómo se autentica |
|---|---|
| **stdio** (local) | Con **credenciales del entorno**: el cliente lanza el proceso y le pasa variables. La spec de MCP indica no seguir su flujo de autorización en stdio y leerlas del entorno |
| **HTTP** (estándar) | **OAuth 2.1**: el servidor actúa como *resource server*, el cliente como cliente OAuth; el usuario autoriza y el cliente recibe un token de acceso |
| **HTTP** (simple) | **Token o API key** en la cabecera: `Authorization: Bearer ...` (lo más común en la práctica) |

Autenticación dice *quién sos*; la **autorización** (los permisos del token) dice *qué podés hacer*. Reglas: mínimo privilegio, tokens revocables y secretos fuera del código y de los logs.

**En este proyecto**

| Conexión | Mecanismo | Credencial |
|---|---|---|
| Agente → OpenAI | API key | `OPENAI_API_KEY` |
| Agente → MCP propio (stdio) | Entorno heredado por el subproceso | `LANGFUSE_*` en el `.env` de la API |
| MCP propio → Langfuse | HTTP Basic (public + secret key) | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` |
| Agente → MCP de GitHub (HTTP) | `Authorization: Bearer` con token fine-grained | `GITHUB_PERSONAL_ACCESS_TOKEN` |
| Front → API | Sin autenticación (demo local); solo CORS | `WEB_ORIGIN` |

Para producción: OAuth o tokens por usuario en el MCP propio por HTTP, y autenticar también la API del agente.

---

## Tools de lectura, escritura o ambas

| Tipo | Qué hace | Ejemplo |
|---|---|---|
| **Solo lectura** | Consulta sin cambiar nada | `get_metrics`, `get_file_contents` |
| **Escritura** | Cambia el estado, a veces de forma irreversible | `create_branch`, `create_pull_request` |
| **Ambas** | Un servidor con tools de los dos tipos, o una tool que según el parámetro lee o escribe | El MCP de GitHub |

La spec define **anotaciones** para que el cliente lo sepa:

| Anotación | Significa |
|---|---|
| `readOnlyHint` | La tool no modifica su entorno |
| `destructiveHint` | Puede hacer cambios destructivos, no solo agregar |
| `idempotentHint` | Repetirla con los mismos argumentos no cambia nada más |
| `openWorldHint` | Interactúa con un mundo abierto (internet, terceros) |

Son **pistas para el cliente, no garantías**: el control real está en el código y en los permisos.

**En este proyecto**

| Servidor | Solo lectura | Escritura | Bloqueadas |
|---|---|---|---|
| MCP propio (7) | `get_health`, `get_metrics`, `diagnose_errors`, `get_error_summary`, `list_logs`, `get_trace_logs`, `get_overview` | Ninguna (todas con `readOnlyHint`) | — |
| MCP GitHub (16 tras filtrar) | `get_file_contents`, `list_branches`, `list_commits`, `get_commit`, `list_pull_requests`, `pull_request_read`, `search_commits`, `search_pull_requests` | `create_branch`, `create_or_update_file`, `push_files`, `create_pull_request`, `update_pull_request`, `update_pull_request_branch`, `add_reply_to_pull_request_comment`, `pull_request_review_write` | `merge_pull_request`, `delete_file`, `create_repository`, `fork_repository` |

El agente **lee** con los dos MCP y **escribe** solo por GitHub, sobre ramas y PRs.

## `get_overview` (dashboard)

Séptima tool, también de solo lectura: devuelve en una llamada salud, volumen, errores por nivel, operaciones (latencia p50/p95, costo, tokens), serie temporal e incidentes agrupados (`mcp_langfuse/overview.py`). La usan el agente y el endpoint `/dashboard`.
