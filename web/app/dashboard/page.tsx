"use client";

import { DashboardView } from "@/components/dashboard-view";

const EMPTY = { input: 0, output: 0, cost: null, priced: false, tools: {} };

/** Ruta /dashboard: muestra solo el dashboard (sin consumo de sesión). */
export default function DashboardPage() {
  return (
    <main className="mx-auto flex h-screen w-full max-w-6xl flex-col p-4">
      <DashboardView totals={EMPTY} />
    </main>
  );
}
