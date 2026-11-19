# Tecnologías

| Área | Tecnología | Versión (aprox.) | Por qué |
|---|---|---|---|
| Protocolo agente↔herramientas | **MCP** | spec actual | Estándar abierto; desacopla agente de sistemas externos |
| Framework MCP | **FastMCP** | 3.x | Tools desde funciones tipadas, validación Pydantic, cliente en memoria para tests |
| SDK MCP | `mcp` | 1.x | Base de FastMCP y de `langchain-mcp-adapters` |
| Cliente MCP en LangChain | **langchain-mcp-adapters** | 0.3 | `MultiServerMCPClient`: varios servidores como una lista de tools |
| Orquestación de agente | **LangChain** (`create_agent`) + **LangGraph** | 1.x | Loop de tool-calling y streaming de actualizaciones |
| LLM | **OpenAI** (`langchain-openai`) | modelo por `OPENAI_MODEL` | Proveedor elegido |
| API | **FastAPI** + **Uvicorn** | 0.1xx | Async, SSE, CORS |
| Validación/config | **Pydantic v2**, **pydantic-settings** | 2.x | Settings tipados, `SecretStr` |
| HTTP | **httpx** (async) | 0.27+ | Cliente de Langfuse; `MockTransport` en tests |
| Observabilidad | **Langfuse** v4 (autoalojado) | 4.82 | Trazas, métricas, costos; API pública REST |
| Instrumentación | **langfuse** SDK Python | 5.x | `@observe`, OpenTelemetry |
| Contenedores | **Kiri** (CLI compatible con Docker) + Compose | Compose 5.x | Runtime disponible en la máquina |
| Frontend | **Next.js** | 16 (App Router, Turbopack) | |
| UI | **React** | 19 | |
| Estilos | **Tailwind CSS** | 4 | |
| Componentes | **shadcn/ui** (base-ui) + **AI Elements** | — | UI de chat agéntico lista y composable |
| Markdown/código | **Streamdown**, **Shiki** | 2.x / 4.x | Render de Markdown en streaming y resaltado de código |
| Iconos | **lucide-react** | | |
| Gestores | **uv** (Python), **pnpm** (Node) | | |
| Tests | **pytest**, **pytest-asyncio**, **respx** | | |
| Control de versiones/PRs | **GitHub** (MCP oficial) | | El agente propone los cambios |

## Langfuse (infraestructura)

El compose oficial levanta: `langfuse-web`, `langfuse-worker`, `postgres`, `clickhouse`, `redis`, `minio` (S3) y `ai-gateway`. Las variables `LANGFUSE_INIT_*` crean organización, proyecto, API keys y usuario al arrancar, sin pasar por la UI.

**Langfuse v4 / events_only.** Los endpoints v1 (`/traces`, `/observations`, `/metrics/daily`, `/scores`) no están disponibles. Disponibles: `/health`, `/ready`, `/v2/observations`, `/v2/metrics` (con `view`, `metrics`, `dimensions`, `filters`, rango temporal) y envío de trazas por OTLP. El MCP está construido sobre esos endpoints.

## Producto observado: `humai-business-app`

E-commerce demo en Python (carrito, cupones, stock, pago simulado).

```
shop/
├── catalog.py    # productos y stock
├── pricing.py    # apply_discount (con el bug intencional de mayúsculas)
├── checkout.py   # reserve_stock → apply_discount → charge_payment
└── errors.py     # ShopError, OutOfStock, InvalidCoupon, report_error()
traffic.py        # tráfico sintético: N checkouts con carritos y cupones al azar
tests/test_pricing.py
```

- Cada paso lleva `@observe`; `charge_payment` se registra como *generation* (simula una pasarela).
- Los errores de dominio tienen **código estable** y **contexto estructurado**, y se publican como metadata `error.*`.
- Errores generados:

| Código | Causa | Tipo |
|---|---|---|
| `INVALID_COUPON` | Cupón en minúscula (`welcome10`) | **Bug de código**: candidato a PR |
| `OUT_OF_STOCK` | Buzo con stock 0 o cantidad mayor al stock | Error de negocio esperado |
