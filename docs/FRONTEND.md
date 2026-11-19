# Frontend (`web/`)

Chat agéntico en **Next.js 16** (App Router, Turbopack) con **Tailwind v4**, **shadcn/ui** y **AI Elements**.

URL: **http://localhost:3001** (el 3000 es de Langfuse). Un solo endpoint de UI: `/`.

## Componentes

| Origen | Componentes |
|---|---|
| **AI Elements** (`components/ai-elements/`) | `Conversation`, `Message` + `MessageResponse`, `PromptInput`, `Tool`, `Suggestion`, `CodeBlock` |
| **shadcn/ui** (`components/ui/`) | `Button`, `Badge`, `Collapsible`, `Select`, `Tooltip`, `Textarea`, etc. (base-ui) |
| Propios | `ThemeToggle` (claro/oscuro), `app/page.tsx` (el chat) |

[AI Elements](https://ui.shadcn.com/docs/ai-elements) es una librería de componentes para interfaces de IA que se instalan como código fuente en el repo (`pnpm dlx ai-elements@latest add <componente>`).

## Cómo funciona el chat (`app/page.tsx`)

- **No usa `useChat`** del AI SDK porque la API emite eventos SSE propios. Un lector de `fetch` + `TextDecoderStream` parsea los eventos `tool_call`, `tool_result`, `message`, `error`.
- Cada mensaje del asistente es una lista de *partes*: texto (renderizado como Markdown con Streamdown) o tool (bloque desplegable con parámetros y resultado JSON).
- Cada tool muestra una etiqueta de origen: **MCP Langfuse** o **MCP GitHub**.
- El historial se envía completo en cada `POST /chat`.
- Sugerencias de arranque y estado "Trabajando…" en el header.

## Tema

Colores de Humai (naranja `#F59410` sobre `#0b0c10`), claro y oscuro. Variables CSS de shadcn en `app/globals.css` (colores `oklch`, acento naranja hue ≈ 65). El tema se guarda en `localStorage` y se aplica con un script inline para evitar el parpadeo. Por defecto: oscuro.

Notas técnicas:
- Tailwind no escanea `node_modules`: `globals.css` declara `@source` para Streamdown, que si no queda sin estilos.
- El bloque de código usa el token `sidebar`, que el tema debe definir.
- `prompt-input.tsx` lleva `// @ts-nocheck` por una discrepancia de tipos con base-ui.

## Configuración

| Variable | Default |
|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` |

## Consumo en vivo

Panel lateral (`CostPanel`) con costo y tokens acumulados de la sesión y un desglose por tool (llamadas, tokens, costo, tiempo). Cada bloque de tool muestra además sus tokens, costo y duración. Los datos vienen de los eventos `usage` y `tool_usage` de la API.

## Dashboard (OpenUI)

Pestaña **Dashboard** (y ruta `/dashboard`). Usa `@openuidev/dashboard-library` + `Renderer` de `@openuidev/react-lang`, sin OpenUI Cloud ni modelo: la API arma el dashboard como **OpenUI Lang** de forma determinista y el front lo dibuja.

- `GET /dashboard?since_minutes=N` (API) → `{openui, since_minutes}`. Usa `mcp_langfuse.overview`, la misma lógica que la tool MCP `get_overview`.
- Secciones: KPIs (salud, observaciones, errores, tasa, traces fallidos), tendencia (volumen vs errores), operaciones (latencia p95, volumen, tabla p50/p95/tokens) e incidentes agrupados.
- Un segundo `Renderer` arma en el navegador el dashboard de **consumo del agente** (costo y tokens por tool) con los eventos `usage` / `tool_usage` de la sesión.
- Ventanas: 1 h, 24 h, 3 y 7 días. Sigue el tema claro/oscuro.
