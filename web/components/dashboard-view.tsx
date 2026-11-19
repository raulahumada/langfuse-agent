"use client";

import { useCallback, useEffect, useMemo, useState, useSyncExternalStore } from "react";
import { RefreshCwIcon } from "lucide-react";
import { ThemeProvider, library } from "@openuidev/dashboard-library";
import { Renderer } from "@openuidev/react-lang";
import { Button } from "@/components/ui/button";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const WINDOWS = [
  { label: "1 h", minutes: 60 },
  { label: "24 h", minutes: 1440 },
  { label: "3 días", minutes: 4320 },
  { label: "7 días", minutes: 10080 },
];

type Totals = {
  input: number;
  output: number;
  cost: number | null;
  priced: boolean;
  tools: Record<string, { calls: number; input: number; output: number; cost: number; ms: number }>;
};

// Se suscribe a cambios de la clase `dark` en <html> para sincronizar el tema del dashboard.
const subscribe = (cb: () => void) => {
  const obs = new MutationObserver(cb);
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
  return () => obs.disconnect();
};
// Lee si el tema oscuro está activo.
const isDark = () => document.documentElement.classList.contains("dark");

/** Consumo del agente en esta sesión, como OpenUI Lang (se arma en el navegador con los eventos SSE). */
function sessionLang(t: Totals): string | null {
  const tools = Object.entries(t.tools);
  if (!t.input && !t.output) return null;
  const j = JSON.stringify;
  const metric = (v: { cost: number; input: number; output: number }) => (t.priced ? v.cost : v.input + v.output);
  tools.sort((a, b) => metric(b[1]) - metric(a[1]));
  const kpis = [
    t.priced ? `Kpi("Costo de la sesión", ${t.cost ?? 0}, "currency-precise")` : null,
    `Kpi("Tokens de entrada", ${t.input}, "number")`,
    `Kpi("Tokens de salida", ${t.output}, "number")`,
    `Kpi("Llamadas a tools", ${tools.reduce((s, [, v]) => s + v.calls, 0)}, "number")`,
  ].filter(Boolean);
  const rows = [`Kpis([${kpis.join(", ")}])`];
  if (tools.length) {
    const names = tools.map(([n]) => n);
    rows.push(
      `Row([Card("${t.priced ? "Costo estimado por tool" : "Tokens por tool"}", [Bars(${j(names)}, [Series("${
        t.priced ? "USD" : "Tokens"
      }", ${j(tools.map(([, v]) => +metric(v).toFixed(6)))})], "${t.priced ? "currency-precise" : "number"}", "horizontal")], "half", "Estimación: tokens de la llamada + los del resultado"), ` +
        `Card("Detalle", [Table([Column("Tool", ${j(names)}, "primary"), Column("Llamadas", ${j(
          tools.map(([, v]) => v.calls),
        )}, "number", "number"), Column("Entrada", ${j(tools.map(([, v]) => v.input))}, "number", "number"), Column("Salida", ${j(
          tools.map(([, v]) => v.output),
        )}, "number", "number"), Column("Tiempo", ${j(tools.map(([, v]) => Math.round(v.ms)))}, "number", "ms")])], "half")], 320)`,
    );
  }
  return `root = Dashboard([Section("Consumo del agente (esta sesión)", [${rows.join(", ")}])])\n`;
}

/** Dashboard OpenUI: métricas de Langfuse (desde /dashboard) + consumo del agente en la sesión. */
export function DashboardView({ totals }: { totals: Totals }) {
  const dark = useSyncExternalStore(subscribe, isDark, () => true);
  const [minutes, setMinutes] = useState(10080);
  const [lang, setLang] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Pide el dashboard a la API para la ventana elegida y guarda el OpenUI Lang resultante.
  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/dashboard?since_minutes=${minutes}`);
      const body = await res.json();
      if (!res.ok) throw new Error(body.error ?? res.statusText);
      setLang(body.openui);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, [minutes]);

  useEffect(() => {
    load();
  }, [load]);

  const session = useMemo(() => sessionLang(totals), [totals]);

  return (
    <div className="min-h-0 flex-1 space-y-4 overflow-y-auto rounded-xl border bg-card/50 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex rounded-lg border p-0.5">
          {WINDOWS.map((w) => (
            <Button key={w.minutes} size="sm" variant={minutes === w.minutes ? "default" : "ghost"} onClick={() => setMinutes(w.minutes)}>
              {w.label}
            </Button>
          ))}
        </div>
        <Button size="sm" variant="outline" onClick={load} disabled={loading}>
          <RefreshCwIcon className={`size-3.5 ${loading ? "animate-spin" : ""}`} /> Actualizar
        </Button>
      </div>
      {error && (
        <p className="rounded-lg border border-destructive/50 p-3 text-sm text-destructive">
          No se pudo cargar el dashboard: {error}
        </p>
      )}
      <ThemeProvider mode={dark ? "dark" : "light"}>
        {lang && <Renderer response={lang} library={library} />}
        {session && <Renderer response={session} library={library} />}
      </ThemeProvider>
    </div>
  );
}
