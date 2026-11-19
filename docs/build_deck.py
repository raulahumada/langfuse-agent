#!/usr/bin/env python3
"""Arma slides-mcp.html reutilizando CSS y motor de slides-whatsapp-ia.html."""
import html, re

BASE = "/Users/rahumada/proyectos/humai/presentation/slides-whatsapp-ia.html"
OUT = "/Users/rahumada/proyectos/humai/presentation/slides-mcp-langfuse.html"

src = open(BASE, encoding="utf-8").read().split("\n")
head = "\n".join(src[:212])  # hasta antes de <body>
engine = "\n".join(src[1284:])  # <script>(function ... </html>
TITLE = "MCP: conectar agentes a herramientas · Humai"
head = head.replace("WhatsApp + IA desde cero · Humai", TITLE)
head = re.sub(r"(<script src=\"https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-yaml.min.js\"></script>)",
              r"\1\n<script src=\"https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-json.min.js\"></script>", head)
head = head.replace("</style>\n</head>", """
  .tbl td code{font-size:.82em;}
  .two{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:22px;}
  .pill{display:inline-block;font-family:var(--mono);font-size:12px;padding:3px 9px;border-radius:6px;
    border:1px solid var(--accent);color:var(--accent);margin-right:6px;}
  .step{display:flex;gap:16px;align-items:flex-start;}
  .step .k{font-family:var(--mono);font-size:13px;color:#0b0c10;background:var(--accent);border-radius:6px;
    padding:3px 9px;flex:none;margin-top:3px;font-weight:500;}
  .steps{display:flex;flex-direction:column;gap:13px;margin-top:24px;}
  .steps .step div{font-size:18px;line-height:1.42;color:var(--text);}
  .steps .step small{display:block;color:var(--dim);font-size:14.5px;margin-top:2px;}
</style>
</head>""", 1)

FOOT = "MCP · teoría y caso real"
QR_SLIDE = '<section class="slide acc-orange" id="s15">\n  <div class="pad" style="padding-top:52px;">\n    <p class="kicker">Por dónde seguir</p>\n    <h1 class="h">Cinco caminos que salen de acá</h1>\n    <p class="sub" style="margin-top:8px;font-size:18px;max-width:1000px;">Elegí por la pregunta que te\n      quedó dando vueltas, no por el título.</p>\n    <div class="cards c3" style="margin-top:18px;">\n      <div class="card" style="padding:13px 17px;">\n        <span class="n">Si no programás</span>\n        <h3 style="font-size:18px;margin:4px 0 6px;">Aprendé a trabajar con Claude</h3>\n        <p style="font-size:14.5px;">Pedirle bien, delegarle tareas sobre tus archivos y apps, y publicar\n          tu propia herramienta con Claude Code, sin escribir código.</p>\n        <p style="font-size:13px;"><small>4 clases · humai.lat/cursos/claude</small></p>\n      </div>\n      <div class="card" style="padding:13px 17px;border-left-color:#a78bfa;">\n        <span class="n" style="color:#a78bfa;">Agentes de IA</span>\n        <h3 style="font-size:18px;margin:4px 0 6px;">Agentes de IA: de la demo a producción</h3>\n        <p style="font-size:14.5px;">Lo que le falta a un agente como este para salir a la calle: RAG, un\n          servidor MCP propio, costo, evaluaciones y despliegue.</p>\n        <p style="font-size:13px;"><small>8 clases · humai.lat/cursos/agentes_ia</small></p>\n      </div>\n      <div class="card" style="padding:13px 17px;border-left-color:#34d399;">\n        <span class="n" style="color:#34d399;">Si querés automatizar más cosas</span>\n        <h3 style="font-size:18px;margin:4px 0 6px;">Automatización y Web Scraping</h3>\n        <p style="font-size:14.5px;">El pariente cercano de esto: sesiones, cookies y automatizar lo que\n          no te dio una API, sin que te bloqueen.</p>\n        <p style="font-size:13px;"><small>7 semanas · humai.lat/cursos/auto</small></p>\n      </div>\n    </div>\n    <div class="cards c3" style="margin-top:12px;grid-template-columns:1fr 1fr 220px;">\n      <div class="card" style="padding:13px 17px;border-left-color:#b15ad6;">\n        <span class="n" style="color:#b15ad6;">La IA que escribe el código</span>\n        <h3 style="font-size:18px;margin:4px 0 6px;">Programación Asistida con IA</h3>\n        <p style="font-size:14.5px;">Trabajar bien con agentes de programación: prompting, skills propias\n          para Claude Code, debugging y tests.</p>\n        <p style="font-size:13px;"><small>4 semanas · humai.lat/cursos/ai_assisted</small></p>\n      </div>\n      <div class="card" style="padding:13px 17px;border-left-color:#38bdf8;">\n        <span class="n" style="color:#38bdf8;">La IA que atiende</span>\n        <h3 style="font-size:18px;margin:4px 0 6px;">Ingeniería de Agentes y LLMs</h3>\n        <p style="font-size:14.5px;">Lo que sigue después del system prompt: RAG, agentes con\n          herramientas, MCP y puesta en producción.</p>\n        <p style="font-size:13px;"><small>8 semanas · humai.lat/cursos/llms</small></p>\n      </div>\n      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;">\n        <img src="qr.jpeg" alt="Código QR al catálogo de cursos de Humai"\n             style="width:190px;height:190px;display:block;"/>\n        <span style="font-family:var(--mono);font-size:11px;letter-spacing:1.1px;\n              text-transform:uppercase;color:var(--accent);text-align:center;">Escaneá y mirá los cinco</span>\n      </div>\n    </div>\n  </div>\n  <div class="foot"><img src="assets/humai-neg.png" alt=""/><span>Por dónde seguir</span></div>\n</section>'
slides = []
n = [0]


def slide(inner, acc="orange", foot=FOOT, cls="", pad=""):
    n[0] += 1
    st = f' style="{pad}"' if pad else ""
    cl = f"slide {cls} acc-{acc}".replace("  ", " ")
    slides.append(
        f'<section class="{cl}" id="s{n[0]}">\n  <div class="pad"{st}>\n{inner}\n  </div>\n'
        f'  <div class="foot"><img src="assets/humai-neg.png" alt=""/><span>{foot}</span></div>\n</section>'
    )


def content(kicker, title, body, acc="orange", sub=None, pad="padding-top:64px;", foot=FOOT):
    s = f'    <p class="kicker">{kicker}</p>\n    <h1 class="h">{title}</h1>\n'
    if sub:
        s += f'    <p class="sub" style="margin-top:10px;font-size:18px;">{sub}</p>\n'
    slide(s + body, acc, foot, pad=pad)


def divider(num, big, dsub, acc, minutes=""):
    n[0] += 1
    m = f'    <div class="minutes">{minutes}</div>\n' if minutes else ""
    slides.append(
        f'<section class="slide divider acc-{acc}" id="s{n[0]}">\n  <div class="pad">\n'
        f'    <div class="num">{num}</div>\n    <div class="big">{big}</div>\n'
        f'    <div class="dsub">{dsub}</div>\n{m}  </div>\n'
        f'  <div class="foot"><img src="assets/humai-neg.png" alt=""/><span>{FOOT}</span></div>\n</section>'
    )


def code(file, lang, text, size=""):
    return (f'    <div class="codewin {size}">\n      <div class="codewin-bar"><div class="codewin-dots"><i></i><i></i><i></i></div>\n'
            f'        <div class="codewin-file">{file}</div><div class="codewin-lang">{lang}</div></div>\n'
            f'<pre class="language-{lang}"><code>{html.escape(text.strip(chr(10)))}</code></pre>\n    </div>')


def card(n_, h, p, small=None, color=None):
    st = f' style="border-left-color:{color};"' if color else ""
    nc = f' style="color:{color};"' if color else ""
    sm = f"<p><small>{small}</small></p>" if small else ""
    return f'<div class="card"{st}><span class="n"{nc}>{n_}</span><h3>{h}</h3><p>{p}</p>{sm}</div>'


def cards(items, cols=3, mt=26):
    return f'    <div class="cards c{cols}" style="margin-top:{mt}px;">' + "".join(items) + "</div>"


def callout(text, color=None, mt=22, size=20):
    st = f"margin-top:{mt}px;font-size:{size}px;" + (f"border-left-color:{color};" if color else "")
    return f'    <div class="callout" style="{st}">{text}</div>'


def you(label, text):
    return f'    <div class="you"><b>{label}</b> {text}</div>'


def bullets(items, tight=True, mt=22):
    li = "".join(f"<li>{i}</li>" for i in items)
    return f'    <ul class="bul {"tight" if tight else ""}" style="margin-top:{mt}px;">{li}</ul>'


def steps(items):
    out = '    <div class="steps">'
    for k, t, s in items:
        sm = f"<small>{s}</small>" if s else ""
        out += f'<div class="step"><span class="k">{k}</span><div>{t}{sm}</div></div>'
    return out + "</div>"


def table(head_, rows, sm=True, mt=20):
    th = "".join(f"<th>{h}</th>" for h in head_)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'    <table class="tbl {"sm" if sm else ""}" style="margin-top:{mt}px;"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


# ───────── helpers SVG ─────────
def svg(vb, inner, label):
    defs = ""
    for mid, col in (("g", "#9aa3bd"), ("o", "#F59410"), ("t", "#22b8cf"), ("p", "#b15ad6"), ("v", "#34d399")):
        defs += (f'<marker id="a{mid}" markerWidth="9" markerHeight="9" refX="7.5" refY="3.2" orient="auto">'
                 f'<path d="M0,0 L7.5,3.2 L0,6.4 Z" fill="{col}"/></marker>')
    return (f'    <div class="diagram"><svg viewBox="{vb}" role="img" aria-label="{label}"><defs>{defs}</defs>{inner}</svg></div>')


def box(x, y, w, h, text, sub=None, stroke="rgba(255,255,255,.14)", fill="#1a1d2e", fs=16, bold=True, subcol="#9aa3bd"):
    t = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}"/>')
    cy = y + h / 2 + (5 if not sub else -2)
    t += (f'<text x="{x + w / 2}" y="{cy}" text-anchor="middle" font-family="Poppins, sans-serif" font-size="{fs}" '
          f'fill="#eef0f7" font-weight="{600 if bold else 400}">{text}</text>')
    if sub:
        t += (f'<text x="{x + w / 2}" y="{cy + 18}" text-anchor="middle" font-family="JetBrains Mono, monospace" '
              f'font-size="10.5" letter-spacing="1" fill="{subcol}">{sub}</text>')
    return t


def line(x1, y1, x2, y2, col="#9aa3bd", mk="g", dash=False, w=1.6):
    d = ' stroke-dasharray="5 5"' if dash else ""
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="{w}"{d} marker-end="url(#a{mk})"/>'


def label(x, y, text, col="#9aa3bd", anchor="middle", fs=11):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="JetBrains Mono, monospace" font-size="{fs}" '
            f'letter-spacing="1.4" fill="{col}">{text}</text>')


def zone(x, y, w, h, text, col, dash=False):
    d = ' stroke-dasharray="7 6"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{col}" fill-opacity=".06" stroke="{col}" '
            f'stroke-opacity=".4"{d}/>' + label(x + 20, y + 26, text, col, "start", 12))


# ═════════════════ PORTADA ═════════════════
n[0] += 1
slides.append(f'''<section class="slide cover acc-orange" id="s{n[0]}">
  <div class="pad">
    <div class="brandrow"><img src="assets/humai-neg.png" alt="Humai"/></div>
    <h1 class="title">MCP: conectar agentes<br/>a herramientas</h1>
    <div class="meta">Teoría, arquitectura y un caso real: Langfuse + GitHub</div>
    <div class="meta">Noviembre 2026</div>
  </div>
</section>''')

# ═════════════════ LEAD ═════════════════
slide('''    <p class="kicker">Lo que vamos a responder</p>
    <h1 class="h">Tres preguntas</h1>
    <div class="qs" style="flex:1;justify-content:center;gap:34px;margin-top:0;">
      <div class="q"><span class="n">01</span><div><div class="t">¿Qué es MCP y por qué existe?</div>
        <div class="a">Teoría: origen, cliente-servidor, tipos, ventajas y desventajas.</div></div></div>
      <div class="q fragment" data-fragment-index="1"><span class="n">02</span><div><div class="t">¿Qué MCP creamos y cómo se construye?</div>
        <div class="a">Tools, validación, pruebas y cómo se ejecuta.</div></div></div>
      <div class="q fragment" data-fragment-index="2"><span class="n">03</span><div><div class="t">¿Cómo encaja en una solución agéntica?</div>
        <div class="a">Cómo lo integramos con un agente, un MCP externo (GitHub) y una interfaz.</div></div></div>
    </div>''')

# ═════════════════ PARTE 1: TEORÍA ═════════════════
divider("Primera parte", "La teoría", "Qué es MCP, quién lo creó, para qué sirve y cómo funciona por dentro.", "orange")

# El problema N×M
inner = ""
inner += zone(0, 0, 520, 300, "SIN ESTÁNDAR · N × M INTEGRACIONES", "#ec5aa0")
inner += zone(568, 0, 520, 300, "CON MCP · N + M", "#34d399")
apps, tools_ = ["App de IA A", "App de IA B", "App de IA C"], ["GitHub", "Base de datos", "Slack"]
for i, a in enumerate(apps):
    inner += box(24, 56 + i * 80, 130, 52, a, fs=14)
for i, t in enumerate(tools_):
    inner += box(366, 56 + i * 80, 130, 52, t, fs=14)
for i in range(3):
    for j in range(3):
        inner += f'<path d="M156,{82 + i * 80} L364,{82 + j * 80}" stroke="#ec5aa0" stroke-opacity=".55" stroke-width="1.2"/>'
for i, a in enumerate(apps):
    inner += box(592, 56 + i * 80, 130, 52, a, fs=14)
    inner += line(724, 82 + i * 80, 800, 150, "#34d399", "v", w=1.3)
inner += box(804, 112, 82, 76, "MCP", stroke="#34d399", fill="#10261f", fs=20)
for i, t in enumerate(tools_):
    inner += box(934, 56 + i * 80, 130, 52, t, fs=14)
    inner += line(888, 150, 932, 82 + i * 80, "#34d399", "v", w=1.3)
content("El problema", "Cada app integraba cada herramienta a mano",
        svg("0 0 1088 300", inner, "N por M integraciones contra N más M con MCP") +
        callout("Con <strong>N aplicaciones</strong> y <strong>M herramientas</strong> hacen falta N×M conectores. "
                "Con un protocolo común, cada lado se implementa <strong>una sola vez</strong>.", mt=18, size=19), pad="padding-top:56px;")

# Qué es MCP
content("Definición", "Model Context Protocol (MCP)",
        '    <p class="sub">Un <strong>estándar abierto</strong> para que las aplicaciones de IA se conecten con sistemas externos: '
        'datos, herramientas y flujos de trabajo.</p>' +
        cards([
            card("La analogía", "USB-C para la IA", "Un solo conector en vez de un cable distinto por cada dispositivo."),
            card("Qué estandariza", "El lenguaje, no la lógica", "Cómo descubrir y llamar capacidades. Qué hacen es cosa de cada servidor."),
            card("Sobre qué se apoya", "JSON-RPC 2.0", "Mensajes JSON de pedido y respuesta, sobre stdio o HTTP."),
        ]) +
        callout("El modelo no \"sabe\" de GitHub ni de Langfuse. Solo ve <strong>una lista de herramientas con descripción y schema</strong>, y decide cuál llamar."))

# Quién y cuándo
content("Origen", "Quién lo creó y cuándo",
        table(["Cuándo", "Qué pasó"], [
            ["25 nov 2024", "<strong>Anthropic</strong> publica MCP como estándar abierto, con SDKs y servidores de ejemplo"],
            ["2025", "Lo adoptan otros actores (OpenAI, Google, Microsoft) y editores como Cursor"],
            ["Mar 2025", "El transporte <code>Streamable HTTP</code> pasa a reemplazar al anterior HTTP+SSE"],
            ["Dic 2025", "Se dona a la <strong>Agentic AI Foundation</strong> de la <strong>Linux Foundation</strong>"],
            ["Hoy", "Spec versionada por fecha: 2024-11-05, 2025-03-26, 2025-06-18, 2025-11-25 y siguientes"],
        ], sm=False) +
        callout("Es un estándar <strong>abierto y con gobierno neutral</strong>: ya no depende de un solo proveedor.", size=19, mt=20) , pad="padding-top:60px;")

# Host / client / server
inner = ""
inner += zone(0, 0, 500, 330, "HOST · LA APLICACIÓN DE IA", "#22b8cf")
inner += box(26, 110, 170, 100, "Aplicación", "agente · IDE · chat", stroke="#22b8cf", fs=16, subcol="#22b8cf")
inner += box(276, 48, 200, 64, "Cliente MCP 1", fs=15, stroke="rgba(255,255,255,.22)")
inner += box(276, 208, 200, 64, "Cliente MCP 2", fs=15, stroke="rgba(255,255,255,.22)")
inner += line(198, 140, 272, 84, "#22b8cf", "t") + line(198, 182, 272, 238, "#22b8cf", "t")
inner += label(250, 306, "1 cliente por servidor · expone las tools al modelo", "#9aa3bd", fs=10)
inner += box(640, 48, 200, 64, "Servidor A", "LOCAL · stdio", stroke="#F59410", subcol="#F59410")
inner += box(640, 208, 200, 64, "Servidor B", "REMOTO · HTTP", stroke="#b15ad6", subcol="#b15ad6")
inner += line(478, 80, 636, 80, "#F59410", "o") + line(478, 240, 636, 240, "#b15ad6", "p")
inner += label(557, 68, "JSON-RPC", "#F59410", fs=10) + label(557, 228, "JSON-RPC", "#b15ad6", fs=10)
inner += box(920, 48, 168, 64, "Sistema", "archivos · API · BD", fs=15)
inner += box(920, 208, 168, 64, "Sistema", "SaaS · servicio", fs=15)
inner += line(842, 80, 916, 80) + line(842, 240, 916, 240)
content("Cómo funciona", "Tres roles: host, cliente y servidor",
        svg("0 0 1088 340", inner, "Host con clientes MCP conectados a servidores MCP") +
        callout("El <strong>host</strong> crea un <strong>cliente</strong> por cada servidor. Cada servidor envuelve un sistema y publica lo que sabe hacer.", mt=14, size=18), pad="padding-top:52px;")

# Transportes + clasificación
content("Cómo se conecta", "Transportes y tipos de MCP",
        table(["", "stdio (local)", "Streamable HTTP (remoto)"], [
            ["Cómo funciona", "El cliente <strong>lanza el servidor como subproceso</strong> y habla por stdin/stdout", "El servidor es un <strong>endpoint HTTP</strong>; el cliente le manda pedidos"],
            ["Autenticación", "Hereda el entorno del proceso (variables)", "Cabeceras, tokens, OAuth"],
            ["En este proyecto", "<strong>MCP propio</strong> de Langfuse", "<strong>MCP oficial</strong> de GitHub"],
        ], sm=True) +
        table(["Clasificación", "Tipos"], [
            ["Por origen", "<strong>Oficiales</strong> (los publica el dueño del servicio) · <strong>de la comunidad</strong> · <strong>propios</strong> (los escribís vos)"],
            ["Por función", "<strong>Datos</strong> (BD, archivos, métricas) · <strong>acciones</strong> (GitHub, Slack, Linear) · <strong>automatización</strong> (navegador, terminal)"],
        ], mt=16, sm=True) +
        callout("El mismo servidor puede ofrecer los dos transportes: cambia una línea, no el código de las tools.", size=18, mt=16), pad="padding-top:50px;")

# Qué expone un servidor
content("Qué ofrece un servidor", "Tools, Resources y Prompts",
        cards([
            card("Tools", "Funciones que el modelo invoca", "Con nombre, descripción y JSON Schema de argumentos. Pueden tener efectos.", "Es lo que más se usa. Todo este proyecto trabaja con tools.", "#F59410"),
            card("Resources", "Datos que se leen", "Contenido identificado por URI: archivos, registros, páginas. Solo lectura.", "Los elige la aplicación, no el modelo.", "#22b8cf"),
            card("Prompts", "Plantillas reutilizables", "Instrucciones parametrizadas que el usuario dispara, como un comando.", "Útiles para flujos repetidos.", "#b15ad6"),
        ]) +
        '    <p class="sub" style="margin-top:22px;font-size:17px;">Del lado del <strong>cliente</strong> hay capacidades que el servidor puede pedir: '
        '<code>roots</code> (qué carpetas puede ver), <code>sampling</code> (pedirle una respuesta al modelo) y <code>elicitation</code> (preguntarle algo al usuario).</p>')

# Tools lectura/escritura (teoría)
content("Tools", "Lectura, escritura o ambas",
        '    <div class="cards c3" style="margin-top:22px;">' +
        card("Solo lectura", "Consultan, no cambian nada", "Leer un archivo, listar commits, pedir métricas. Se pueden repetir sin riesgo.", "Marcadas con <code>readOnlyHint: true</code>.", "#34d399") +
        card("Escritura", "Cambian el estado", "Crear una rama, abrir un PR, enviar un mensaje. Pueden ser irreversibles.", "Piden más cuidado y, a veces, aprobación.", "#ec5aa0") +
        card("Ambas", "Mezcla o depende de los argumentos", "Un servidor con tools de los dos tipos, o una tool que según el parámetro lee o escribe.", "Conviene separar y etiquetar cada una.", "#F59410") +
        '</div>' +
        table(["Anotación", "Significa"], [
            ["<code>readOnlyHint</code>", "La tool no modifica su entorno"],
            ["<code>destructiveHint</code>", "Puede hacer cambios destructivos, no solo agregar"],
            ["<code>idempotentHint</code>", "Llamarla de nuevo con los mismos argumentos no cambia nada más"],
            ["<code>openWorldHint</code>", "Interactúa con un mundo abierto (internet, terceros) o solo con algo cerrado"],
        ], mt=12) +
        callout("Son <strong>pistas para el cliente</strong>, no garantías: el control real está en el código y en los permisos.", size=18, mt=12), pad="padding-top:46px;")

# Ventajas / desventajas
content("Balance", "Ventajas y desventajas",
        '    <div class="two" style="margin-top:22px;align-items:start;">\n      <div>\n'
        '        <h4 style="font-family:var(--mono);font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#34d399;margin:0 0 4px;">Ventajas</h4>' +
        bullets(["<strong>Se escribe una vez</strong>, sirve para cualquier cliente compatible.",
                 "<strong>Descubrible</strong>: el agente aprende las tools en ejecución.",
                 "<strong>Desacopla</strong> el agente del sistema: cambiás uno sin tocar el otro.",
                 "<strong>Ecosistema</strong> grande y abierto, con SDKs en varios lenguajes.",
                 "Un lugar claro para poner <strong>límites y permisos</strong>."], mt=10) +
        '\n      </div>\n      <div>\n'
        '        <h4 style="font-family:var(--mono);font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#ec5aa0;margin:0 0 4px;">Desventajas</h4>' +
        bullets(["<strong>Cada tool ocupa contexto</strong>: muchas tools = más costo y más confusión.",
                 "<strong>Superficie de ataque</strong>: prompt injection y servidores no confiables.",
                 "<strong>Otra pieza</strong> para desplegar, versionar y monitorear.",
                 "<strong>Calidad desigual</strong> entre servidores de la comunidad.",
                 "Un estándar <strong>joven</strong>: la spec sigue cambiando."], mt=10).replace("#34d399", "#ec5aa0") +
        '\n      </div>\n    </div>')

# QR (copiado del deck original)
n[0] += 1
slides.append(QR_SLIDE.replace('id="s15"', f'id="s{n[0]}"'))


# ═════════════════ PARTE 2: EL MCP QUE CREAMOS ═════════════════
divider("Segunda parte", "El MCP que creamos", "Qué construimos, cómo está hecho, cómo se crean las tools y cómo se prueba.", "green")

content("Antes de construir", "Qué es Langfuse y para qué sirve",
        '    <p class="sub">Una plataforma <strong>open source</strong> de observabilidad para aplicaciones con IA: guarda lo que hizo tu app, paso a paso, para que puedas entenderlo, medirlo y mejorarlo.</p>' +
        cards([
            card("El problema", "Una app es una caja negra", "Si algo falla o se vuelve lento, no sabés qué paso pasó, con qué datos ni cuánto costó.", color="#34d399"),
            card("Qué hace", "Registra cada paso", "Tu código manda <strong>trazas</strong>: qué se ejecutó, cuánto tardó, qué entró y salió, y si hubo error.", color="#34d399"),
            card("Para qué", "Ver, medir, mejorar", "Errores, latencia, costo y tokens en un panel; evaluar la calidad de las respuestas.", color="#34d399"),
        ]) +
        callout("Es el <strong>“Datadog de las apps con IA”</strong>: en vez de adivinar, mirás lo que realmente pasó.", color="#34d399") +
        you("En el proyecto", "Langfuse es la <strong>fuente de datos</strong>: el agente la lee a través de nuestro MCP."), acc="green")

content("Antes de construir", "Las piezas de Langfuse, en simple",
        table(["Concepto", "Qué es", "Ejemplo en el proyecto"], [
            ["<strong>Trace</strong> (traza)", "El recorrido completo de <em>una</em> operación", "Un <code>checkout</code> de principio a fin"],
            ["<strong>Observation</strong>", "Cada paso dentro de la traza: span, generación (llamada a un LLM) o evento", "<code>reserve_stock</code>, <code>apply_discount</code>, <code>charge_payment</code>"],
            ["<strong>Level</strong>", "Gravedad del paso: <code>DEFAULT</code>, <code>WARNING</code>, <code>ERROR</code>", "<code>ERROR</code> cuando el cupón es inválido"],
            ["<strong>Métricas</strong>", "Conteos, latencia (p50/p95), costo y tokens, agrupables", "Cuántos checkouts fallaron y cuánto tardaron"],
            ["<strong>Scores</strong>", "Notas de calidad sobre una traza (manuales o automáticas)", "No los usamos todavía"],
        ], sm=False, mt=18) +
        bullets(["Se instrumenta con un <strong>SDK</strong> (<code>@observe</code> en Python) y los datos viajan por <strong>OpenTelemetry</strong>.",
                 "Se consulta por una <strong>API REST</strong> pública: justo la que envuelve nuestro MCP."], mt=14) +
        callout("Sin Langfuse no hay nada que observar: <strong>el MCP es el puente</strong> entre estos datos y el agente.", color="#34d399", size=19, mt=14), acc="green", pad="padding-top:50px;")

content("Parte práctica", "Langfuse Ops Agent",
        '    <p class="sub">Un agente SRE que observa una aplicación a través de <strong>Langfuse</strong> y actúa sobre su código con <strong>GitHub</strong>.</p>' +
        cards([
            card("Observa", "Salud, logs y métricas", "Lee Langfuse: health, errores, latencias, costos y trazas.", color="#34d399"),
            card("Diagnostica", "Errores con contexto", "Agrupa fallas, ubica el archivo y la línea, y distingue bugs de errores de negocio.", color="#34d399"),
            card("Propone", "Un Pull Request", "Lee el código, crea rama y commit, y abre el PR con la evidencia.", color="#34d399"),
        ]) +
        callout("Lo central del proyecto son <strong>los dos MCP</strong>: uno que construimos y uno de terceros.", color="#34d399") +
        you("Producto observado", "<code>humai-business-app</code>: un e-commerce demo con errores a propósito."), acc="green")


# El producto observado
content("El producto observado", "humai-business-app: de dónde salen los datos",
        '    <p class="sub">Un e-commerce demo en Python (carrito, cupones, stock, pago simulado) instrumentado con el SDK de Langfuse.</p>' +
        table(["Pieza", "Qué hace"], [
            ["<code>shop/checkout.py</code>", "<code>checkout → reserve_stock → apply_discount → charge_payment</code>, cada paso con <code>@observe</code>"],
            ["<code>shop/errors.py</code>", "Errores de dominio con código y contexto, y <code>report_error()</code>"],
            ["<code>traffic.py</code>", "Simula N compras con cupones y productos al azar"],
        ], mt=16) +
        table(["Error", "Causa", "Tipo"], [
            ["<code>INVALID_COUPON</code>", "Cupón en minúscula (<code>welcome10</code>)", "<strong>Bug de código</strong>: candidato a PR"],
            ["<code>OUT_OF_STOCK</code>", "Buzo con stock 0", "Error de negocio esperado"],
        ], mt=14) +
        you("Ojo", "Las trazas no se generan solas: existen cuando corre <code>traffic.py</code> o una app real."), acc="green", pad="padding-top:56px;")
# Estructura del MCP propio
content("MCP propio", "Un servidor en capas limpias",
        '    <div class="two" style="margin-top:20px;align-items:start;">\n      <div>' +
        code("mcp_langfuse/", "bash", '''mcp_langfuse/
├── config.py       # variables de entorno
├── client.py       # cliente HTTP de Langfuse
├── diagnostics.py  # lógica pura de agrupación
├── overview.py     # resumen para dashboards
├── server.py       # define las tools (FastMCP)
└── __main__.py     # CLI: stdio o http''', "sm") + '</div>\n      <div>' +
        table(["Capa", "Responsabilidad"], [
            ["config", "Settings con <code>SecretStr</code>"],
            ["client", "HTTP async, auth, errores legibles"],
            ["diagnostics", "Agrupar errores; sin red, fácil de probar"],
            ["overview", "Arma el resumen (salud, métricas, serie, incidentes) que usan el agente y el dashboard"],
            ["server", "Exponer tools y devolver errores como datos"],
        ], mt=0) + '</div>\n    </div>' +
        callout("Regla: <strong>el servidor MCP es una capa fina</strong>. La lógica vive en módulos que se prueban sin el protocolo.", color="#34d399", mt=22, size=19),
        acc="green", pad="padding-top:60px;")

# Crear una tool con FastMCP
content("Crear una tool", "Una función tipada es una tool",
        code("mcp_langfuse/server.py", "python", '''mcp = FastMCP("langfuse-ops", instructions=INSTRUCTIONS)

@mcp.tool(annotations={"readOnlyHint": True})
async def list_logs(
    level: Literal["DEBUG", "DEFAULT", "WARNING", "ERROR"] | None = None,
    since_minutes: Annotated[int, Field(ge=1, le=20160)] = 60,
    limit: Annotated[int, Field(ge=1, le=100)] = 25,
) -> dict[str, Any]:
    """Lista observaciones recientes; usá level=ERROR para ver fallos."""
    try:
        return await lf().observations(level=level, since_minutes=since_minutes, limit=limit)
    except LangfuseError as exc:
        return {"error": str(exc)}''', "sm") +
        bullets(["El <strong>nombre</strong> sale de la función, la <strong>descripción</strong> del docstring, el <strong>schema</strong> de los type hints.",
                 "<code>Literal</code> y <code>Field</code> validan <strong>antes</strong> de ejecutar: un nivel inválido se rechaza."], mt=14),
        acc="green", pad="padding-top:56px;")

# Las 7 tools
content("Las tools del MCP propio", "Siete herramientas, todas de solo lectura",
        table(["Tool", "Para qué sirve"], [
            ["<code>get_health</code>", "Liveness y readiness de Langfuse"],
            ["<code>get_metrics</code>", "Volumen, latencia p50/p95, costo y tokens por nombre, nivel o modelo"],
            ["<code>diagnose_errors</code>", "<strong>Informe de errores listo para diagnosticar</strong>: incidentes agrupados con causa y ubicación"],
            ["<code>get_error_summary</code>", "Conteo de errores por observación y trace"],
            ["<code>list_logs</code>", "Observaciones recientes con filtros"],
            ["<code>get_trace_logs</code>", "Todas las observaciones de un trace"],
            ["<code>get_overview</code>", "<strong>Resumen para dashboards</strong>: salud, volumen, serie temporal, operaciones e incidentes en una llamada"],
        ], mt=18, sm=False) +
        callout("El agente <strong>observa</strong>; las escrituras pasan por GitHub y bajo límites.", color="#34d399", size=19), acc="green")

# diagnose_errors antes/después
content("Diseñar para el modelo", "De logs crudos a un diagnóstico",
        '    <div class="two" style="margin-top:20px;align-items:start;">\n      <div>\n'
        '        <h4 style="font-family:var(--mono);font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#ec5aa0;margin:0 0 6px;">Antes · observaciones crudas</h4>' +
        bullets(["El mismo fallo repetido en cada span padre e hijo.",
                 "Sin tipo de excepción ni archivo.",
                 "Mensajes con valores variables: nada se agrupa.",
                 "Resultado: respuestas pobres del agente."], mt=6) +
        '\n      </div>\n      <div>\n'
        '        <h4 style="font-family:var(--mono);font-size:12px;letter-spacing:1.4px;text-transform:uppercase;color:#34d399;margin:0 0 6px;">Después · <code>diagnose_errors</code></h4>' +
        bullets(["<strong>Colapsa por trace</strong>: una falla cuenta una vez.",
                 "<strong>Agrupa por código</strong> de error, no por mensaje.",
                 "Agrega ubicación, contexto, stacktrace y ejemplos.",
                 "Ordena por impacto."], mt=6).replace("#ec5aa0", "#34d399") +
        '\n      </div>\n    </div>' +
        code("resultado (recortado)", "json", '''{"failed_traces": 31,
 "incidents": [{
   "operation": "checkout", "count": 9,
   "error_code": "INVALID_COUPON",
   "context": {"coupon": "vip20", "valid": ["WELCOME10","VIP20"]},
   "location": "pricing.py:14 en apply_discount",
   "sample_trace_ids": ["876d21a6...", "badd983c..."] }]}''', "xs"),
        acc="green", pad="padding-top:54px;")

# Probar el MCP
content("Probar el servidor", "Tests en memoria, sin red ni subprocesos",
        code("tests/test_server.py", "python", '''def make_client(handler) -> LangfuseClient:
    settings = Settings(public_key="pk", secret_key=SecretStr("sk"))
    return LangfuseClient(settings, transport=httpx.MockTransport(handler))

async def test_api_error_is_returned_not_raised():
    server = build_server(make_client(lambda r: httpx.Response(500, text="boom")))
    async with Client(server) as c:          # fastmcp.Client en memoria
        res = await c.call_tool("get_metrics", {})
    assert "500" in res.data["error"]

async def test_invalid_args_rejected():
    server = build_server(make_client(lambda r: httpx.Response(200, json={})))
    async with Client(server) as c:
        with pytest.raises(Exception):
            await c.call_tool("list_logs", {"level": "NOPE"})''', "sm") +
        bullets(["<code>build_server(client)</code> acepta un cliente falso: <strong>inyección de dependencias</strong>.",
                 "<code>fastmcp.Client(server)</code> habla con el servidor en el mismo proceso.",
                 "7 tests: tools, errores, validación y agrupación."], mt=14), acc="green", pad="padding-top:56px;")


# ═════════════════ PARTE 3 ═════════════════
divider("Tercera parte", "Cómo encaja en una solución agéntica", "El agente, el MCP externo de GitHub y cómo integramos todo.", "cyan")

# Cómo lo integramos
content("Integración", "Cómo lo integramos, paso a paso",
        steps([
            ("1", "Construimos y probamos el <strong>MCP propio</strong> por separado", "Tests en memoria y prueba por stdio contra Langfuse real."),
            ("2", "Sumamos el <strong>MCP oficial de GitHub</strong>", "Remoto por HTTP, con token y solo los toolsets <code>repos</code> y <code>pull_requests</code>."),
            ("3", "<code>MultiServerMCPClient</code> abre ambas conexiones", "Descubre las tools y las convierte en una única lista."),
            ("4", "Filtramos las tools peligrosas", "<code>BLOCKED_TOOLS</code> quita merge, borrado y creación de repos."),
            ("5", "<code>create_agent</code> recibe modelo, tools y system prompt", "El prompt dice cuándo usar cada MCP y cómo presentar el diagnóstico."),
            ("6", "FastAPI expone el agente y el front lo muestra", "Eventos SSE: se ve qué MCP llamó el agente y con qué argumentos."),
        ]), acc="cyan")
# Diagrama de arquitectura
inner = ""
inner += zone(0, 0, 250, 150, "PRODUCTO", "#34d399")
inner += box(25, 56, 200, 70, "humai-business-app", "e-commerce · @observe", stroke="#34d399", fs=14, subcol="#34d399")
inner += zone(0, 190, 250, 160, "OBSERVABILIDAD", "#ec5aa0")
inner += box(25, 246, 200, 76, "Langfuse v4", ":3000 · Kiri/Docker", stroke="#ec5aa0", fs=15, subcol="#ec5aa0")
inner += line(125, 128, 125, 242, "#34d399", "v")
inner += label(160, 190, "trazas", "#34d399", "start", 10)
inner += zone(300, 0, 788, 350, "LANGFUSE-OPS", "#22b8cf")
inner += box(322, 56, 120, 58, "Next.js", ":3001 · shadcn", fs=15, stroke="#22b8cf", subcol="#22b8cf")
inner += box(482, 56, 120, 58, "FastAPI", ":8000 · SSE", fs=15, stroke="#22b8cf", subcol="#22b8cf")
inner += box(642, 46, 190, 78, "Agente LangChain", "create_agent · OpenAI", fs=15, stroke="#F59410", subcol="#F59410")
inner += line(444, 85, 478, 85, "#22b8cf", "t") + line(604, 85, 638, 85, "#22b8cf", "t")
inner += box(660, 196, 154, 64, "Cliente MCP", "MultiServerMCPClient", fs=14, stroke="rgba(255,255,255,.2)", subcol="#9aa3bd")
inner += line(737, 126, 737, 192, "#F59410", "o")
inner += box(330, 270, 210, 60, "MCP propio · FastMCP", "stdio · 7 tools", fs=14, stroke="#F59410", subcol="#F59410")
inner += box(880, 270, 190, 60, "MCP GitHub", "HTTP remoto · ~16 tools", fs=14, stroke="#b15ad6", subcol="#b15ad6")
inner += line(662, 238, 544, 296, "#F59410", "o") + line(812, 238, 876, 296, "#b15ad6", "p")
inner += line(328, 300, 254, 290, "#ec5aa0", "g")
inner += label(290, 322, "REST", "#ec5aa0", fs=10)
inner += box(880, 150, 190, 50, "GitHub · repo", fs=14, stroke="rgba(255,255,255,.2)")
inner += line(975, 268, 975, 204, "#b15ad6", "p")
content("Arquitectura", "Cómo está conectado todo",
        svg("0 0 1088 352", inner, "Arquitectura del proyecto") , acc="cyan", pad="padding-top:50px;")

# Conectar ambos MCP
content("Conectar", "Un cliente, dos servidores, una lista de tools",
        code("api/agent.py", "python", '''client = MultiServerMCPClient({
    "langfuse": {                       # MCP propio · stdio
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "mcp_langfuse"],
    },
    "github": {                         # MCP externo · HTTP remoto
        "transport": "streamable_http",
        "url": "https://api.githubcopilot.com/mcp/",
        "headers": {"Authorization": f"Bearer {token}",
                    "X-MCP-Toolsets": "repos,pull_requests"},
    },
})
tools = [t for t in await client.get_tools() if t.name not in BLOCKED_TOOLS]
model = ChatOpenAI(model=OPENAI_MODEL)
agent = create_agent(model, tools, system_prompt=SYSTEM_PROMPT)''', "sm") +
        bullets(["El agente ve <strong>~23 tools</strong> sin saber de qué servidor viene cada una.",
                 "El servidor propio hereda el entorno del proceso: así lee <code>LANGFUSE_*</code>."], mt=14), acc="cyan", pad="padding-top:56px;")

# MCP GitHub
content("MCP externo", "GitHub: un servidor oficial que solo se configura",
        cards([
            card("Dónde", "Remoto y oficial", "<code>api.githubcopilot.com/mcp</code> por Streamable HTTP, con tu token como Bearer.", color="#b15ad6"),
            card("Qué se publica", "Dos toolsets", "<code>X-MCP-Toolsets: repos,pull_requests</code> deja ~16 tools en vez de decenas.", color="#b15ad6"),
            card("Qué se usó", "Leer y proponer", "<code>get_file_contents</code>, <code>create_branch</code>, <code>create_or_update_file</code>, <code>create_pull_request</code>.", color="#b15ad6"),
        ]) +
        callout("Token <em>fine-grained</em> de un solo repo: <code>Contents: write</code>, <code>Pull requests: write</code>, <code>Metadata: read</code>. "
                "Con solo lectura, GitHub responde <strong>403</strong> y el agente solo puede sugerir.", color="#b15ad6", size=18) +
        you("Aprendido", "Ni un MCP bien armado funciona si el token no tiene los permisos."), acc="cyan")

# Tools del proyecto: lectura vs escritura
content("Tools del proyecto", "Qué tools leen y cuáles escriben",
        table(["Servidor", "Solo lectura", "Escritura", "Bloqueadas"], [
            ["<strong>MCP propio</strong> (7)", "<code>get_health</code> · <code>get_metrics</code> · <code>diagnose_errors</code> · <code>get_error_summary</code> · <code>list_logs</code> · <code>get_trace_logs</code> · <code>get_overview</code>", "<strong>Ninguna</strong>: todas con <code>readOnlyHint</code>", "—"],
            ["<strong>MCP GitHub</strong> (16 tras filtrar)", "<code>get_file_contents</code> · <code>list_branches</code> · <code>list_commits</code> · <code>get_commit</code> · <code>list_pull_requests</code> · <code>pull_request_read</code> · <code>search_commits</code> · <code>search_pull_requests</code>", "<code>create_branch</code> · <code>create_or_update_file</code> · <code>push_files</code> · <code>create_pull_request</code> · <code>update_pull_request</code> · <code>update_pull_request_branch</code> · <code>add_reply_to_pull_request_comment</code> · <code>pull_request_review_write</code>", "<code>merge_pull_request</code> · <code>delete_file</code> · <code>create_repository</code> · <code>fork_repository</code>"],
        ], sm=True, mt=16) +
        callout("Combinación <strong>ambas</strong>: el agente <strong>lee</strong> con los dos MCP y <strong>escribe</strong> solo por GitHub, sobre ramas y PRs. Lo destructivo se filtra antes de llegar al modelo.", color="#22b8cf", size=18, mt=16), acc="cyan", pad="padding-top:54px;")

# Agente y API
content("El agente y la API", "Del modelo al navegador",
        '    <div class="two" style="margin-top:20px;align-items:start;">\n      <div>' +
        bullets(["<code>create_agent</code> de LangChain: <strong>loop de tool-calling</strong> sobre LangGraph.",
                 "El <strong>system prompt</strong> define el rol SRE, el formato del diagnóstico y los límites.",
                 "FastAPI inicia el agente <strong>una vez</strong> en el <code>lifespan</code>.",
                 "<code>POST /chat</code> responde por <strong>SSE</strong>."], mt=4) + '</div>\n      <div>' +
        table(["Evento SSE", "Cuándo"], [
            ["<code>tool_call</code>", "El modelo elige una tool"],
            ["<code>tool_result</code>", "La tool respondió"],
            ["<code>message</code>", "Respuesta final (Markdown)"],
            ["<code>error</code> · <code>done</code>", "Fallo · fin del stream"],
        ], mt=0) + '</div>\n    </div>' +
        callout("El front dibuja cada <code>tool_call</code> en vivo: se ve <strong>qué MCP usó el agente y con qué argumentos</strong>.", color="#34d399", mt=20, size=19), acc="cyan", pad="padding-top:60px;")

# Flujo de una consulta
content("Cómo funciona en el proyecto", "Qué pasa cuando preguntás",
        steps([
            ("1", "Escribís <em>\"Revisá los errores y proponé un PR\"</em>", "Next.js hace <code>POST /chat</code> con el historial."),
            ("2", "FastAPI le pasa el mensaje al agente", "Y devuelve la respuesta como eventos SSE."),
            ("3", "El agente llama <code>diagnose_errors</code>", "MCP propio → API de Langfuse → incidentes agrupados."),
            ("4", "Lee el código con <code>get_file_contents</code>", "MCP de GitHub → <code>pricing.py</code>."),
            ("5", "Crea rama, commit y PR", "<code>create_branch</code> → <code>create_or_update_file</code> → <code>create_pull_request</code>."),
            ("6", "El chat muestra cada tool y la respuesta final en Markdown", "Una persona revisa el PR y hace el merge."),
        ]), acc="cyan")

# Del error al PR
content("Caso completo", "Del error al Pull Request",
        '    <div class="two" style="margin-top:20px;align-items:start;">\n      <div>' +
        steps([
            ("A", "<code>traffic.py</code> simula compras", "Con cupones y productos al azar."),
            ("B", "El checkout falla", "<code>InvalidCoupon</code> si el cupón viene en minúscula."),
            ("C", "<code>report_error()</code> marca el span", "Código, tipo, archivo:línea, stacktrace, contexto."),
            ("D", "Langfuse lo guarda", "Como observación con <code>level=ERROR</code>."),
            ("E", "El agente lo diagnostica y propone el fix", "PR con trace ids y conteos como evidencia."),
        ]) + '</div>\n      <div>' +
        code("pricing.py · el bug", "python", '''def apply_discount(subtotal, coupon):
    if not coupon:
        return subtotal
    if coupon not in COUPONS:
        raise InvalidCoupon(coupon, valid=list(COUPONS))
    rate = COUPONS[coupon]   # distingue mayúsculas
    return round(subtotal * (1 - rate), 2)''', "sm") +
        callout("El fix claro: normalizar con <code>coupon.upper()</code> y agregar un test.", color="#22b8cf", mt=16, size=17) +
        '</div>\n    </div>', acc="cyan", pad="padding-top:60px;")

# Front
content("El frontend", "Chat agéntico y dashboard con OpenUI",
        cards([
            card("AI Elements", "Componentes de IA", "<code>Conversation</code>, <code>Message</code>, <code>PromptInput</code>, <code>Tool</code>, <code>Suggestion</code>.", "Se instalan como código fuente en el repo."),
            card("Streaming", "SSE propio", "Un lector de <code>fetch</code> parsea los eventos, incluidos tokens y costo por tool."),
            card("Dashboard", "OpenUI", "Pestaña con KPIs, tendencia, latencias e incidentes. La API lo arma con <code>get_overview</code> y el front lo dibuja con <code>dashboard-library</code>.", "Sin modelo ni OpenUI Cloud."),
            card("Tema", "Colores de Humai", "Claro y oscuro con variables CSS de shadcn. Cada tool muestra su origen: MCP Langfuse o MCP GitHub."),
        ], cols=2, mt=22) +
        callout("Mostrar las <strong>llamadas a tools</strong> y su <strong>costo</strong> es lo que vuelve entendible a un agente.", color="#34d399", size=19, mt=18), acc="cyan")

# Demo
content("Demo en vivo", "Cinco pasos, de menor a mayor",
        steps([
            ("1", "<em>¿Cómo está la salud de Langfuse?</em>", "Tool <code>get_health</code> · etiqueta MCP Langfuse."),
            ("2", "<em>Resumen de métricas de la última hora</em>", "Tool <code>get_metrics</code> · tabla en Markdown."),
            ("3", "<em>¿Qué errores hubo?</em>", "Tool <code>diagnose_errors</code> · separa bug de código y error de negocio."),
            ("4", "<em>Revisá los errores y proponé un PR si el fix es claro</em>", "Tools de GitHub · lee <code>pricing.py</code>, crea rama, commit y PR."),
            ("5", "<em>Abrí la pestaña Dashboard</em>", "Mismos datos que <code>get_overview</code>, en KPIs, gráficos e incidentes; y el costo por tool de la sesión."),
        ]) +
        you("Antes de empezar", "Langfuse, API y front arriba, y <code>traffic.py 40</code> corrido para tener datos frescos."), acc="cyan")


# ═════════════════ PARTE 4: TIPS ═════════════════
divider("Cuarta parte", "Tips para crear tus MCP", "Lo que aprendimos construyendo este proyecto.", "purple")

content("Diseño de tools", "Pensá en el modelo, no en la API",
        cards([
            card("01", "Pocas y con propósito", "Cada tool ocupa contexto. Mejor 6 buenas que 60.", color="#b15ad6"),
            card("02", "Devolvé conclusiones", "Agrupá, ordená y recortá. No vuelques JSON crudo de 10.000 líneas.", color="#b15ad6"),
            card("03", "Descripción como prompt", "El docstring le dice al modelo cuándo usarla. Escribilo para él.", color="#b15ad6"),
            card("04", "Argumentos acotados", "<code>Literal</code>, rangos y defaults: menos margen para equivocarse.", color="#b15ad6"),
            card("05", "Errores como datos", "Devolvé <code>{\"error\": ...}</code> legible, no un traceback.", color="#b15ad6"),
            card("06", "Nombres claros", "<code>diagnose_errors</code> se entiende solo; <code>query2</code> no.", color="#b15ad6"),
        ], cols=3, mt=24), acc="purple")

# Autenticación (teoría)
content("Autenticación", "Cómo se autentica un MCP",
        table(["Transporte", "Cómo se autentica", "Detalle"], [
            ["<strong>stdio</strong> (local)", "<strong>Credenciales del entorno</strong>", "El cliente lanza el proceso y le pasa variables de entorno. La spec indica <em>no</em> usar su flujo de autorización y leer las credenciales del entorno."],
            ["<strong>HTTP</strong> (remoto)", "<strong>OAuth 2.1</strong> (estándar de la spec)", "El servidor actúa como <em>resource server</em> y el cliente como cliente OAuth: el usuario autoriza y el cliente recibe un token de acceso."],
            ["<strong>HTTP</strong> (simple)", "<strong>Token o API key en cabecera</strong>", "<code>Authorization: Bearer ...</code>. Es lo más común en la práctica: tokens personales o de servicio."],
        ], sm=False, mt=18) +
        bullets(["El <strong>servidor</strong> es quien valida: cada pedido HTTP lleva el token y se verifica su alcance.",
                 "El token debe ser de <strong>mínimo privilegio</strong> y revocable; nunca va en el código ni en los logs."], mt=16) +
        callout("Autenticación = <strong>quién sos</strong>. Qué podés hacer lo define la <strong>autorización</strong>: los permisos del token.", size=19, mt=16), acc="purple", pad="padding-top:56px;")


# Autenticación en el proyecto
content("Autenticación", "Cómo se autentica cada pieza del proyecto",
        table(["Conexión", "Mecanismo", "Dónde vive la credencial"], [
            ["Agente → <strong>OpenAI</strong>", "API key", "<code>OPENAI_API_KEY</code> (<code>SecretStr</code>)"],
            ["Agente → <strong>MCP propio</strong> (stdio)", "Entorno heredado: el subproceso lee <code>LANGFUSE_*</code>", "<code>.env</code> de la API; no viaja por el protocolo"],
            ["MCP propio → <strong>Langfuse</strong>", "HTTP Basic con public y secret key del proyecto", "<code>LANGFUSE_PUBLIC_KEY</code> · <code>LANGFUSE_SECRET_KEY</code>"],
            ["Agente → <strong>MCP de GitHub</strong> (HTTP)", "<code>Authorization: Bearer</code> con token fine-grained", "<code>GITHUB_PERSONAL_ACCESS_TOKEN</code>"],
            ["Front → API", "Sin autenticación (demo local), solo CORS al origen del front", "<code>WEB_ORIGIN</code>"],
        ], sm=True, mt=16) +
        callout("El token de GitHub define <strong>qué puede hacer</strong> el agente: <code>Contents</code> y <code>Pull requests</code> en write, de un solo repo. "
                "Con solo lectura, GitHub responde <strong>403</strong>.", color="#b15ad6", size=18, mt=16) +
        you("Para producción", "Poner OAuth o tokens por usuario en el MCP propio por HTTP, y autenticar también la API del agente."), acc="purple", pad="padding-top:54px;")


content("Seguridad y operación", "Límites en varias capas: lo que no se negocia",
        table(["Capa", "Mecanismo en el proyecto"], [
            ["Código", "<code>BLOCKED_TOOLS</code> quita <code>merge_pull_request</code>, <code>delete_file</code>, <code>create_repository</code> y <code>fork_repository</code>"],
            ["Protocolo", "<code>X-MCP-Toolsets: repos,pull_requests</code> limita lo que publica GitHub"],
            ["Permisos", "Token fine-grained de un solo repo; MCP propio de solo lectura (<code>readOnlyHint</code>)"],
            ["Prompt", "Solo el repo configurado y sin push a la rama principal"],
            ["Proceso", "El agente propone el PR y <strong>una persona hace el merge</strong>"],
        ], mt=16) +
        bullets(["Secretos en variables de entorno (<code>SecretStr</code>), nunca en el código ni en los logs.",
                 "Errores de la API devueltos como datos legibles, sin romper al agente."], mt=14) +
        callout("Un solo control no alcanza: <strong>combiná capas</strong>.", color="#b15ad6", size=19, mt=14), acc="purple", pad="padding-top:54px;")

content("Lecciones del proyecto", "Lo que nos tocó resolver",
        table(["Problema", "Qué pasó", "Solución"], [
            ["API que cambia", "Langfuse v4 no tiene <code>/traces</code> (modo events_only)", "Usar <code>v2/observations</code> y <code>v2/metrics</code>"],
            ["Versiones", "<code>fastmcp</code> 4 exige <code>mcp</code> 2; los adapters aún no", "Fijar <code>fastmcp&lt;4</code> y <code>mcp&lt;2</code>"],
            ["Datos crudos", "El agente daba diagnósticos pobres", "<code>diagnose_errors</code> + errores con contexto"],
            ["Permisos", "GitHub devolvía 403 al crear la rama", "Token con <code>Contents</code> y <code>Pull requests</code> en write"],
            ["Estilos", "AI Elements sin estilos en el front", "Tema shadcn completo y <code>@source</code> de Tailwind"],
        ], mt=18), acc="purple")

# Cierre
slide('''    <p class="kicker">Para cerrar</p>
    <h1 class="h">Lo que se llevan</h1>
    <div class="cards c3" style="margin-top:30px;">
      <div class="card"><span class="n">Teoría</span><h3>MCP es un estándar abierto</h3>
        <p>Un protocolo para publicar y descubrir herramientas. Se escribe una vez y sirve a muchos clientes.</p></div>
      <div class="card"><span class="n">Práctica</span><h3>Un servidor es una capa fina</h3>
        <p>Funciones tipadas, validación, lógica en módulos aparte y tests sin el protocolo.</p></div>
      <div class="card"><span class="n">Criterio</span><h3>Diseñá para el modelo</h3>
        <p>Pocas tools, resultados con conclusiones, errores legibles y límites reales.</p></div>
    </div>
    <div class="callout" style="margin-top:28px;font-size:21px;">Un agente es tan útil como <strong>las herramientas que le das</strong>
      y tan seguro como <strong>los límites que le ponés</strong>.</div>
    <div class="you"><b>Material</b> Proyecto <code>langfuse-ops</code>, repo <code>humai-business-app</code> y documentación en <code>docs/</code>.</div>''',
      "orange", "MCP · Humai")

body = "\n\n".join(slides)
open(OUT, "w", encoding="utf-8").write(head + "\n<body data-deck-title=\"" + TITLE + "\">\n\n" + body + "\n\n" + engine)
print("slides:", n[0], "->", OUT)
