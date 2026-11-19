"use client";

import { MoonIcon, SunIcon } from "lucide-react";
import { useSyncExternalStore } from "react";
import { Button } from "@/components/ui/button";

// Se suscribe a cambios de la clase `dark` en <html> para que React re-renderice al cambiar el tema.
const subscribe = (cb: () => void) => {
  const obs = new MutationObserver(cb);
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
  return () => obs.disconnect();
};
// Lee si el tema oscuro está activo.
const isDark = () => document.documentElement.classList.contains("dark");

/** Botón que alterna tema claro/oscuro y lo guarda en localStorage. */
export function ThemeToggle() {
  const dark = useSyncExternalStore(subscribe, isDark, () => true);
  return (
    <Button
      variant="outline"
      size="icon"
      aria-label="Cambiar tema"
      onClick={() => {
        const next = !dark;
        document.documentElement.classList.toggle("dark", next);
        localStorage.setItem("theme", next ? "dark" : "light");
      }}
    >
      {dark ? <SunIcon className="size-4" /> : <MoonIcon className="size-4" />}
    </Button>
  );
}
