# Langfuse Ops Agent

Un **agente de operaciones (SRE)** que observa una aplicación a través de **Langfuse**, diagnostica sus errores y, cuando el arreglo es claro, **propone un Pull Request** en GitHub.

Lo central del proyecto son los **dos MCP** que usa el agente:

| MCP | Tipo | Qué hace |
|---|---|---|
| `mcp_langfuse` | **Propio**, hecho con FastMCP | Expone salud, logs, métricas y diagnóstico de errores de Langfuse como *tools* de solo lectura |
| GitHub MCP | **Externo**, oficial y remoto | Leer código, crear ramas, commits y PRs |

```
Next.js (:3001) ──SSE──▶ FastAPI (:8000) ──▶ Agente LangChain (OpenAI)
                                                ├─ MCP propio "langfuse" (stdio) ──▶ Langfuse (:3000)
                                                └─ MCP GitHub (HTTP remoto)       ──▶ GitHub

humai-business-app (e-commerce demo) ──trazas @observe──▶ Langfuse (:3000)
```

> Documentación detallada en [`docs/`](docs/): [Arquitectura](docs/ARCHITECTURE.md) · [MCP](docs/MCP.md) · [Agente y API](docs/AGENT.md) · [Frontend](docs/FRONTEND.md) · [Tecnologías](docs/STACK.md) · [Guía para la presentación](docs/PRESENTATION.md)

---

## Qué hay en este repo

```
langfuse-ops/
├── mcp_langfuse/      # MCP propio (FastMCP): config, cliente HTTP, diagnóstico, server
├── api/               # FastAPI + agente LangChain (consume ambos MCP)
├── web/               # Next.js + shadcn/ui + AI Elements (chat agéntico)
├── infra/             # docker compose oficial de Langfuse v4
├── tests/             # tests del MCP (en memoria, sin red)
├── docs/              # documentación
└── .env.example
```

El **producto observado** vive en un repo aparte: [`raulahumada/humai-business-app`](https://github.com/raulahumada/humai-business-app) (local: `../../humai-business-app`). Es un e-commerce demo en Python instrumentado con Langfuse.

---

## Requisitos

- **Python ≥ 3.11** y [`uv`](https://docs.astral.sh/uv/)
- **Node.js** (probado con v24) y **pnpm**
- **Un runtime de contenedores** para Langfuse. En esta máquina se usa **Kiri** (`/Applications/Kiri.app`), cuyo CLI es compatible con Docker: se usa `kiri` en lugar de `docker`. Con Docker Desktop, OrbStack o Colima, reemplazá `kiri` por `docker`.
- **Clave de OpenAI**
- **Token de GitHub fine-grained** sobre el repo del producto (permisos abajo)

---

## Puesta en marcha (de cero)

Se necesitan **4 piezas**. Abrí una terminal por cada servicio que queda corriendo.

### 1. Langfuse (puerto 3000)

```bash
cd langfuse-ops/infra
cp .env.example .env          # crea org/proyecto/keys/usuario automáticamente
K=/Applications/Kiri.app/Contents/MacOS/kiri
$K compose -f langfuse-compose.yml --env-file .env up -d
```

La primera vez corre migraciones (1–2 min). Verificá:

```bash
curl http://localhost:3000/api/public/health      # {"status":"OK","version":"4.x"}
```

UI: http://localhost:3000 — usuario `admin@local.dev` / `admin12345`.
Servicios que levanta: `langfuse-web`, `langfuse-worker`, `postgres`, `clickhouse`, `redis`, `minio`, `ai-gateway`.

### 2. Variables de entorno de la API

```bash
cd langfuse-ops
cp .env.example .env
# editar: OPENAI_API_KEY, OPENAI_MODEL, GITHUB_PERSONAL_ACCESS_TOKEN, GITHUB_REPO
```

**Permisos del token de GitHub** (fine-grained, repo `humai-business-app`):
`Contents: Read and write` · `Pull requests: Read and write` · `Metadata: Read-only`.
Sin escritura el agente puede *leer* el repo pero **no** crear ramas ni PRs (GitHub devuelve 403).

### 3. API + agente (puerto 8000)

```bash
cd langfuse-ops
uv sync
.venv/bin/uvicorn api.main:app --port 8000
```

Al arrancar, la API lanza el MCP propio como subproceso (stdio), se conecta al MCP de GitHub y carga las tools. Verificá:

```bash
curl http://localhost:8000/tools     # 7 tools de Langfuse y ~16 de GitHub
```

### 4. Frontend (puerto 3001)

```bash
cd langfuse-ops/web
pnpm install
pnpm dev                              # http://localhost:3001
```

Abrí http://localhost:3001. Si la API no está en `localhost:8000`, definí `NEXT_PUBLIC_API_URL`.

### 5. Generar tráfico (el producto observado)

Las trazas **no se generan solas**: las produce `humai-business-app` cuando se ejecuta. Sin tráfico nuevo, el agente solo ve lo que ya está guardado dentro de la ventana de tiempo que le pidas.

```bash
cd humai-business-app
uv sync
LANGFUSE_HOST=http://localhost:3000 \
LANGFUSE_PUBLIC_KEY=pk-lf-local-demo \
LANGFUSE_SECRET_KEY=sk-lf-local-demo \
uv run python traffic.py 40           # 40 checkouts sintéticos
```

---

## Cómo probarlo

En el chat (http://localhost:3001) probá, en este orden:

1. `¿Cómo está la salud de Langfuse?` → tool `get_health`
2. `Resumen de métricas de la última hora` → tool `get_metrics`
3. `¿Qué errores hubo? Mostrame los logs` → tool `diagnose_errors`
4. `Revisá los errores y proponé un PR si el fix es claro` → tools de GitHub (lee código, crea rama, commit y PR)

Cada llamada a una tool aparece en el chat con su origen (**MCP Langfuse** / **MCP GitHub**), parámetros y resultado.

### El bug a propósito

`humai-business-app` tiene un bug intencional: los cupones en minúscula (`welcome10`, `vip20`) fallan con `InvalidCoupon`, porque `COUPONS[coupon]` distingue mayúsculas. El agente debería detectarlo, ubicarlo en `pricing.py` y proponer un PR (por ejemplo normalizar con `coupon.upper()` y agregar un test). El `OutOfStock` del buzo (stock 0) es un error de negocio esperado; el agente debe distinguirlo.

---

## Comandos útiles

```bash
# tests del MCP
cd langfuse-ops && .venv/bin/python -m pytest -q

# correr el MCP solo, por stdio o por HTTP
.venv/bin/python -m mcp_langfuse
.venv/bin/python -m mcp_langfuse --transport http --port 8765

# estado de Langfuse
$K compose -f infra/langfuse-compose.yml --env-file infra/.env ps

# liberar la API si quedó colgada
pkill -f "uvicorn api.main"
```

## Troubleshooting

| Síntoma | Causa / solución |
|---|---|
| El chat dice que no puede crear ramas o PRs | Token de GitHub sin `Contents: write` / `Pull requests: write` (403). Ver "Permisos del token" |
| `/tools` no responde | La API no está corriendo o falló al conectar el MCP de GitHub; revisar el log de uvicorn |
| El agente no ve errores recientes | No hay tráfico nuevo: correr `traffic.py`. Las trazas tardan unos segundos en aparecer |
| El front se ve sin estilos | Reiniciar `pnpm dev` y recargar con Cmd+Shift+R |
| Langfuse responde "not available in v4 events_only mode" | Es esperado: v4 no tiene `/traces`; el MCP usa `v2/observations` y `v2/metrics` |
| Procesos que "se caen" | Si se lanzan desde un comando que termina, mueren con él. Usar una terminal dedicada por servicio |

## Seguridad

- El MCP propio es **solo lectura** (`readOnlyHint`).
- El agente tiene **bloqueadas en código** estas tools de GitHub: `merge_pull_request`, `delete_file`, `create_repository`, `fork_repository`. Propone PRs; **el merge lo hace una persona**.
- El prompt restringe al agente al repo de `GITHUB_REPO` y le prohíbe pushear a la rama principal.
- Los toolsets del MCP de GitHub se limitan a `repos` y `pull_requests`.
- `.env` está fuera del control de versiones; los secretos son `SecretStr` y no se loguean.
