"use client";

import { useRef, useState } from "react";
import { ActivityIcon, BotIcon, CoinsIcon, GitPullRequestIcon, UserIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/theme-toggle";
import { DashboardView } from "@/components/dashboard-view";
import { Button } from "@/components/ui/button";
import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import { Message, MessageContent, MessageResponse } from "@/components/ai-elements/message";
import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
  type PromptInputMessage,
} from "@/components/ai-elements/prompt-input";
import { Suggestion, Suggestions } from "@/components/ai-elements/suggestion";
import { Tool, ToolContent, ToolHeader, ToolInput, ToolOutput } from "@/components/ai-elements/tool";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ToolState = "input-available" | "output-available" | "output-error";
type Part =
  | { kind: "text"; text: string }
  | { kind: "tool"; id: string; name: string; input: unknown; output?: string; state: ToolState; usage?: ToolUsage; ms?: number };
type ToolUsage = { input_tokens: number; output_tokens: number; cost: number | null; duration_ms?: number | null };
type Totals = {
  input: number;
  output: number;
  cost: number | null;
  priced: boolean;
  tools: Record<string, { calls: number; input: number; output: number; cost: number; ms: number }>;
};
const EMPTY: Totals = { input: 0, output: 0, cost: null, priced: false, tools: {} };

/** Formatea un número de tokens con separador de miles (es-AR). */
const fmtTok = (n: number) => n.toLocaleString("es-AR");
/** Formatea un costo en USD; muestra "—" si no hay precio configurado. */
const fmtCost = (c: number | null | undefined) =>
  c == null ? "—" : `US$ ${c < 0.01 ? c.toFixed(5) : c.toFixed(4)}`;

type Msg = { id: string; role: "user" | "assistant"; parts: Part[] };

/** Tools del MCP propio de Langfuse (el resto se considera del MCP de GitHub). */
const LANGFUSE_TOOLS = new Set(["get_health", "list_logs", "get_trace_logs", "get_metrics", "get_error_summary", "diagnose_errors"]);

/** Badge que indica de qué servidor MCP viene una tool (Langfuse o GitHub). */
function ToolSource({ name }: { name: string }) {
  const lf = LANGFUSE_TOOLS.has(name);
  return (
    <Badge variant="outline" className={lf ? "border-primary/50 text-primary" : "border-border text-muted-foreground"}>
      {lf ? <ActivityIcon className="size-3" /> : <GitPullRequestIcon className="size-3" />}
      {lf ? "MCP Langfuse" : "MCP GitHub"}
    </Badge>
  );
}

/** Badge con tokens, costo y duración atribuidos a una llamada de tool. */
function UsageBadge({ u, ms }: { u?: ToolUsage; ms?: number }) {
  if (!u && ms == null) return null;
  return (
    <Badge variant="outline" className="ml-2 gap-1 font-mono text-[11px] text-muted-foreground">
      <CoinsIcon className="size-3" />
      {u ? `${fmtTok(u.input_tokens)} in · ${fmtTok(u.output_tokens)} out · ${fmtCost(u.cost)}` : "calculando…"}
      {ms != null && ` · ${ms} ms`}
    </Badge>
  );
}

/** Panel lateral "Consumo en vivo": costo total, desglose por tool y contexto base. */
function CostPanel({ t, last }: { t: Totals; last: Totals | null }) {
  const rows = Object.entries(t.tools).sort((a, b) => b[1].cost - a[1].cost || b[1].input + b[1].output - (a[1].input + a[1].output));
  const attributed = rows.reduce((s, [, v]) => s + v.input + v.output, 0);
  const base = Math.max(t.input + t.output - attributed, 0);
  const max = Math.max(...rows.map(([, v]) => v.cost || v.input + v.output), 1e-9);
  return (
    <aside className="hidden w-72 shrink-0 flex-col gap-3 overflow-y-auto rounded-xl border bg-card p-4 text-sm lg:flex">
      <div className="flex items-center gap-2 font-semibold">
        <CoinsIcon className="size-4 text-primary" /> Consumo en vivo
      </div>
      <div>
        <div className="font-mono text-2xl font-semibold text-primary">{fmtCost(t.cost)}</div>
        <div className="text-xs text-muted-foreground">
          {fmtTok(t.input)} tokens in · {fmtTok(t.output)} out
        </div>
        {!t.priced && t.input > 0 && (
          <p className="mt-1 text-xs text-amber-500">
            Sin precios: definí OPENAI_PRICE_IN_PER_M y OPENAI_PRICE_OUT_PER_M en el .env de la API.
          </p>
        )}
      </div>
      <div className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Por tool (estimado)</div>
      {rows.length === 0 && <p className="text-xs text-muted-foreground">Todavía no se usó ninguna tool.</p>}
      <ul className="space-y-2">
        {rows.map(([name, v]) => (
          <li key={name}>
            <div className="flex items-center justify-between gap-2">
              <span className="truncate font-mono text-xs">{name}</span>
              <span className="font-mono text-xs">{fmtCost(t.priced ? v.cost : null)}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded bg-muted">
              <div className="h-full bg-primary" style={{ width: `${Math.max(((t.priced ? v.cost : v.input + v.output) / max) * 100, 3)}%` }} />
            </div>
            <div className="text-[11px] text-muted-foreground">
              {v.calls} {v.calls === 1 ? "llamada" : "llamadas"} · {fmtTok(v.input)} in · {fmtTok(v.output)} out · {Math.round(v.ms)} ms
            </div>
          </li>
        ))}
      </ul>
      <div className="mt-auto rounded-lg bg-muted/60 p-2 text-[11px] text-muted-foreground">
        Contexto base (prompt, historial, respuesta): {fmtTok(base)} tokens.
        {last && <> Último turno: {fmtCost(last.cost)}.</>}
        <br />
        Las tools no cuestan por sí mismas: se les atribuyen los tokens que el modelo gastó en llamarlas y en leer su resultado.
      </div>
    </aside>
  );
}

/** Intenta parsear el resultado de una tool como JSON; si no se puede, devuelve el texto crudo. */
function parseOutput(raw?: string): unknown {
  if (!raw) return undefined;
  try {
    return JSON.parse(raw);
  } catch {
    return raw;
  }
}

/** Preguntas de ejemplo que se muestran como atajos en el chat. */
const SUGGESTIONS = [
  "¿Cómo está la salud de Langfuse?",
  "Resumen de métricas de la última hora",
  "¿Qué errores hubo? Mostrame los logs",
  "Revisá los errores y proponé un PR si el fix es claro",
];

/** Pantalla principal: chat con el agente (vía SSE), dashboard y panel de consumo. */
export default function Page() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<"chat" | "dashboard">("chat");
  const [totals, setTotals] = useState<Totals>(EMPTY);
  const [lastTurn, setLastTurn] = useState<Totals | null>(null);
  const history = useRef<{ role: string; content: string }[]>([]);

  // Aplica un cambio a las partes del último mensaje (el del asistente que se está armando).
  const patchLast = (fn: (parts: Part[]) => Part[]) =>
    setMessages((ms) => {
      const copy = [...ms];
      const last = copy[copy.length - 1];
      copy[copy.length - 1] = { ...last, parts: fn(last.parts) };
      return copy;
    });

  // Traduce cada evento SSE de la API (tool_call, tool_result, usage, message...) en estado de la UI.
  function handleEvent(event: string, data: Record<string, any>) { // eslint-disable-line @typescript-eslint/no-explicit-any
    if (event === "tool_call") {
      patchLast((p) => [...p, { kind: "tool", id: data.id, name: data.name, input: data.args, state: "input-available" }]);
    } else if (event === "tool_result") {
      patchLast((p) => {
        const idx = p.findIndex((x) => x.kind === "tool" && x.id === data.id);
        if (idx < 0) return p;
        const next = [...p];
        next[idx] = { ...(p[idx] as Extract<Part, { kind: "tool" }>), output: data.content, state: "output-available", ms: data.duration_ms };
        return next;
      });
    } else if (event === "tool_usage") {
      patchLast((p) => p.map((x) => (x.kind === "tool" && x.id === data.id ? { ...x, usage: data as ToolUsage } : x)));
      setTotals((tt) => {
        const cur = tt.tools[data.name] ?? { calls: 0, input: 0, output: 0, cost: 0, ms: 0 };
        return {
          ...tt,
          tools: {
            ...tt.tools,
            [data.name]: {
              calls: cur.calls + 1,
              input: cur.input + data.input_tokens,
              output: cur.output + data.output_tokens,
              cost: cur.cost + (data.cost ?? 0),
              ms: cur.ms + (data.duration_ms ?? 0),
            },
          },
        };
      });
    } else if (event === "usage") {
      setTotals((tt) => ({
        ...tt,
        input: tt.input + data.input_tokens,
        output: tt.output + data.output_tokens,
        cost: data.cost == null ? tt.cost : (tt.cost ?? 0) + data.cost,
        priced: tt.priced || data.cost != null,
      }));
    } else if (event === "turn_usage") {
      setLastTurn({ ...EMPTY, cost: data.cost, priced: data.prices_configured });
    } else if (event === "message") {
      patchLast((p) => [...p, { kind: "text", text: data.content }]);
      history.current.push({ role: "assistant", content: data.content });
    } else if (event === "error") {
      patchLast((p) => [...p, { kind: "text", text: `⚠️ ${data.message}` }]);
    }
  }

  // Envía el mensaje a POST /chat y procesa el stream SSE frame por frame.
  async function send(text: string) {
    if (!text.trim() || busy) return;
    history.current.push({ role: "user", content: text });
    setMessages((ms) => [
      ...ms,
      { id: crypto.randomUUID(), role: "user", parts: [{ kind: "text", text }] },
      { id: crypto.randomUUID(), role: "assistant", parts: [] },
    ]);
    setBusy(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ messages: history.current }),
      });
      if (!res.body) throw new Error("Sin respuesta");
      const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
      let buf = "";
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += value;
        const frames = buf.split("\n\n");
        buf = frames.pop() ?? "";
        for (const f of frames) {
          const event = /^event: (.*)$/m.exec(f)?.[1];
          const raw = /^data: (.*)$/m.exec(f)?.[1];
          if (event && raw) handleEvent(event, JSON.parse(raw));
        }
      }
    } catch (e) {
      handleEvent("error", { message: String(e) });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex h-screen w-full max-w-6xl flex-col gap-3 p-4">
      <header className="flex items-center justify-between rounded-xl border bg-card px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ActivityIcon className="size-5" />
          </div>
          <div>
            <h1 className="text-base font-semibold leading-tight">Langfuse Ops Agent</h1>
            <p className="text-xs text-muted-foreground">Salud, logs y métricas · PRs con GitHub</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className={`size-2 rounded-full bg-primary ${busy ? "animate-pulse" : ""}`} />
            {busy ? "Trabajando…" : "Listo"}
          </span>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/humai.png" alt="Humai" className="hidden h-5 dark:block" />
          <div className="flex rounded-lg border p-0.5">
            {(["chat", "dashboard"] as const).map((k) => (
              <Button key={k} size="sm" variant={tab === k ? "default" : "ghost"} onClick={() => setTab(k)}>
                {k === "chat" ? "Chat" : "Dashboard"}
              </Button>
            ))}
          </div>
          <ThemeToggle />
        </div>
      </header>

      {tab === "dashboard" && <DashboardView totals={totals} />}
      <div className={`min-h-0 flex-1 gap-3 ${tab === "chat" ? "flex" : "hidden"}`}>
      <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-3">
      <Conversation className="rounded-xl border bg-card/50">
        <ConversationContent>
          {messages.length === 0 ? (
            <ConversationEmptyState
              icon={<BotIcon className="size-8" />}
              title="Preguntame por tu app"
              description="Leo salud, logs y métricas de Langfuse y puedo proponer un PR."
            />
          ) : (
            messages.map((m) => (
              <Message key={m.id} from={m.role}>
                <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground group-[.is-user]:ml-auto">
                  {m.role === "user" ? <UserIcon className="size-3.5" /> : <BotIcon className="size-3.5 text-primary" />}
                  {m.role === "user" ? "Vos" : "Agente"}
                </div>
                <MessageContent className="group-[.is-user]:bg-primary group-[.is-user]:text-primary-foreground group-[.is-assistant]:rounded-xl group-[.is-assistant]:border group-[.is-assistant]:bg-card group-[.is-assistant]:px-4 group-[.is-assistant]:py-3">
                  {m.parts.map((p, i) =>
                    p.kind === "text" ? (
                      <MessageResponse key={i}>{p.text}</MessageResponse>
                    ) : (
                      <Tool key={i} className="mb-0 bg-background/60">
                        <ToolHeader type="dynamic-tool" toolName={p.name} state={p.state} title={p.name} />
                        <ToolContent>
                          <div className="flex flex-wrap items-center">
                            <ToolSource name={p.name} />
                            <UsageBadge u={p.usage} ms={p.ms} />
                          </div>
                          <ToolInput input={p.input as never} />
                          <ToolOutput output={parseOutput(p.output) as never} errorText={undefined} />
                        </ToolContent>
                      </Tool>
                    ),
                  )}
                  {m.role === "assistant" && busy && m === messages[messages.length - 1] && (
                    <span className="text-xs text-muted-foreground animate-pulse">Pensando…</span>
                  )}
                </MessageContent>
              </Message>
            ))
          )}
        </ConversationContent>
        <ConversationScrollButton />
      </Conversation>

      <div className="space-y-2 pt-3">
        {messages.length === 0 && (
          <Suggestions>
            {SUGGESTIONS.map((s) => (
              <Suggestion key={s} suggestion={s} onClick={send} />
            ))}
          </Suggestions>
        )}
        <PromptInput onSubmit={(m: PromptInputMessage) => send(m.text)}>
          <PromptInputBody>
            <PromptInputTextarea placeholder="Preguntá por salud, métricas, errores…" />
          </PromptInputBody>
          <PromptInputFooter>
            <span />
            <PromptInputSubmit status={busy ? "streaming" : undefined} disabled={busy} />
          </PromptInputFooter>
        </PromptInput>
      </div>
      </div>
      <CostPanel t={totals} last={lastTurn} />
      </div>
    </main>
  );
}
