# Guía para la presentación

La presentación está en `presentation/slides-mcp-langfuse.html` (40 slides, mismo motor y estilo que `slides-whatsapp-ia.html`). Se navega con flechas o espacio y se imprime a PDF en 1280×720.

## Mensaje central

> "Un agente de IA que **observa**, **diagnostica** y **propone el arreglo**, conectado a sus herramientas mediante **MCP**: uno que construimos nosotros y uno de terceros."

## Estructura (≈ 25–30 min)

| Parte | Slides | Contenido | Fuente en `docs/` |
|---|---|---|---|
| Apertura | 1–2 | Portada y tres preguntas: qué es MCP, qué MCP creamos y cómo encaja en una solución agéntica | — |
| **1 · La teoría** | 3–12 | Problema N×M · definición · origen (quién y cuándo) · cómo funciona (host, cliente, servidor) · cómo se conecta (transportes stdio/HTTP y tipos de MCP) · tools, resources y prompts · **tools de lectura, escritura o ambas** (anotaciones) · ventajas y desventajas (balance) · **QR y cursos de Humai (cierre de la parte 1)** | `MCP.md` |
| **2 · El MCP que creamos** | 13–22 | **Qué es Langfuse y sus piezas (trace, observation, level, métricas)** · El proyecto · producto observado (`humai-business-app`) · servidor en capas · crear una tool con FastMCP · las 7 tools · `diagnose_errors` antes y después · tests en memoria | `MCP.md`, `STACK.md` |
| **3 · Cómo encaja en una solución agéntica** | 23–33 | Solución agéntica · cómo lo integramos en 6 pasos · arquitectura · conectar ambos MCP · MCP externo de GitHub · **qué tools leen y cuáles escriben** · agente y API · qué pasa cuando preguntás · del error al PR · frontend con dashboard OpenUI · demo | `ARCHITECTURE.md`, `AGENT.md`, `FRONTEND.md`, `STACK.md` |
| **4 · Tips** | 34–40 | Diseño de tools · **autenticación** (cómo se autentica un MCP y cada pieza del proyecto) · seguridad y operación · lecciones del proyecto · próximos pasos · cierre | este documento |

El recorrido es: **primero la teoría, después lo que construimos (el MCP), y al final cómo ese MCP se integra en un agente completo**.

## Guion de la demo (5 min, slide 33)

**Antes de empezar:** Langfuse, API y front arriba; correr `traffic.py 40` para tener datos frescos; token de GitHub con escritura.

1. Mostrar la UI de Langfuse (http://localhost:3000): trazas con errores en rojo.
2. Abrir el chat (http://localhost:3001). Pulsar *"¿Cómo está la salud de Langfuse?"* → tool `get_health` con la etiqueta **MCP Langfuse**.
3. *"Resumen de métricas de la última hora"* → tabla con volumen y latencias.
4. *"¿Qué errores hubo?"* → `diagnose_errors`: dos incidentes; el agente separa **bug de código** (cupón) de **error de negocio** (stock).
5. *"Revisá los errores y proponé un PR si el fix es claro"* → tools con etiqueta **MCP GitHub**: lee `pricing.py`, crea rama, commit y PR.
6. Abrir el PR en GitHub: evidencia (trace ids, conteos) y diff.
7. Cerrar: "el agente no puede mergear; ese paso es humano".

**Plan B si falla algo en vivo:** capturas del chat, de Langfuse y del PR; y `curl localhost:8000/tools` para mostrar que ambos MCP están conectados.

## Mensajes clave

- MCP desacopla el agente de los sistemas: **cambiar de backend = reescribir un servidor, no el agente**.
- Lo valioso del MCP propio **no es exponer la API tal cual**, sino **darle al modelo datos ya procesados** (`diagnose_errors`).
- MCP es la **capa de herramientas** de un agente; el modelo, el bucle, la API y la interfaz se arman alrededor.
- Los guardrails van en **varias capas** (código, protocolo, permisos, prompt, proceso). El prompt no es un control de seguridad.
- La calidad del diagnóstico depende de la **calidad de la instrumentación**.

## Datos de la teoría a verificar antes de presentar

Confirmados contra fuentes oficiales: anuncio de Anthropic el 25/11/2024, versiones de la spec (2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25) y donación a la Agentic AI Foundation de la Linux Foundation.
Sin contrastar: la adopción por OpenAI, Google y Microsoft durante 2025 y la fecha del cambio a Streamable HTTP (marzo de 2025).

## Aprendizajes

- Langfuse v4 cambió su API (events_only): hubo que construir sobre `v2/observations` y `v2/metrics`.
- Observaciones crudas dan diagnósticos pobres; agrupar y enriquecer cambió la calidad de las respuestas.
- `fastmcp` 4 requiere `mcp` 2, que `langchain-mcp-adapters` aún no soporta: se fijó `fastmcp<4` y `mcp<2`.
- Los permisos del token de GitHub determinan si el agente puede actuar o solo sugerir.

## Próximos pasos

- Ids en los eventos `tool_call` para emparejar resultados en llamadas paralelas.
- Persistir conversaciones y memoria del agente.
- Aprobación explícita (*human-in-the-loop*) antes de crear el PR.
- Más tools: scores, prompts, datasets y evaluaciones de Langfuse.
- Alertas que disparen al agente ante picos de error.
- Evaluar al propio agente con datasets y scores en Langfuse.
- Despliegue: contenedores para API y front; MCP propio por HTTP con autenticación.
