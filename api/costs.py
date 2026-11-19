"""Medición de tokens y costo por turno, con atribución estimada a cada tool.

Las tools no cuestan por sí mismas; cuestan los tokens del modelo:
- salida: los tokens con los que el modelo decidió llamar a la tool (se reparten entre las llamadas del paso);
- entrada: los tokens del resultado de la tool, que el modelo relee en el paso siguiente
  (≈ input_siguiente − input_anterior − output_anterior, repartido según el tamaño de cada resultado).
Lo que no se atribuye a ninguna tool (system prompt, historial, respuesta final) queda como "contexto base".
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


MODEL_PRICES: dict[str, tuple[float, float]] = {
    "gpt-6-luna": (0.10, 0.50),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-5": (1.25, 10.00),
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5-nano": (0.05, 0.40),
}


@dataclass
class Prices:
    """USD por millón de tokens. None = sin configurar (se muestran solo tokens)."""

    input_per_m: float | None = None
    output_per_m: float | None = None

    @classmethod
    def from_env(cls) -> "Prices":
        """Toma precios del .env o, si faltan, de MODEL_PRICES según OPENAI_MODEL."""
        def num(name: str) -> float | None:
            """Lee una variable de entorno numérica; None si está vacía o inválida."""
            raw = os.getenv(name, "").strip()
            try:
                return float(raw) if raw else None
            except ValueError:
                return None

        # Precios por defecto en el código (USD / 1M tokens, página de precios de OpenAI); el .env solo los pisa.
        default = MODEL_PRICES.get(os.getenv("OPENAI_MODEL", "").strip(), MODEL_PRICES["gpt-4o-mini"])
        return cls(num("OPENAI_PRICE_IN_PER_M") or default[0], num("OPENAI_PRICE_OUT_PER_M") or default[1])

    @property
    def configured(self) -> bool:
        """True si hay precio de entrada y de salida."""
        return self.input_per_m is not None and self.output_per_m is not None

    def cost(self, input_tokens: float, output_tokens: float) -> float | None:
        """Costo en USD para esa cantidad de tokens (None si no hay precios)."""
        if not self.configured:
            return None
        return (input_tokens * self.input_per_m + output_tokens * self.output_per_m) / 1_000_000  # type: ignore[operator]


@dataclass
class _Call:
    """Llamada a una tool pendiente de atribuir: tokens de salida, tamaño del resultado y duración."""

    id: str
    name: str
    out_tokens: float = 0.0
    result_chars: int = 0
    duration_ms: int | None = None


@dataclass
class TurnMeter:
    """Acumula tokens y costo de un turno del agente y los reparte entre las tools usadas."""

    prices: Prices = field(default_factory=Prices.from_env)
    input_tokens: int = 0
    output_tokens: int = 0
    _prev_in: int = 0
    _prev_out: int = 0
    _pending: list[_Call] = field(default_factory=list)
    by_tool: dict[str, dict] = field(default_factory=dict)  # id -> uso atribuido

    def record_result(self, call_id: str, chars: int, duration_ms: int | None = None) -> None:
        """Registra tamaño y duración del resultado de una tool (sirve de peso para repartir la entrada)."""
        for c in self._pending:
            if c.id == call_id:
                c.result_chars, c.duration_ms = chars, duration_ms

    def on_ai_step(self, in_tok: int, out_tok: int, calls: list[tuple[str, str]]) -> list[dict]:
        """Procesa un paso del modelo. Devuelve el uso atribuido a las tools del paso anterior."""
        self.input_tokens += in_tok
        self.output_tokens += out_tok

        emitted: list[dict] = []
        if self._pending:
            delta_in = max(in_tok - self._prev_in - self._prev_out, 0)
            total_chars = sum(c.result_chars for c in self._pending) or len(self._pending)
            for c in self._pending:
                weight = (c.result_chars or 1) / total_chars
                tin = delta_in * weight
                usage = {
                    "id": c.id,
                    "name": c.name,
                    "input_tokens": round(tin),
                    "output_tokens": round(c.out_tokens),
                    "cost": self.prices.cost(tin, c.out_tokens),
                    "duration_ms": c.duration_ms,
                }
                self.by_tool[c.id] = usage
                emitted.append(usage)

        share = out_tok / len(calls) if calls else 0.0
        self._pending = [_Call(i, n, out_tokens=share) for i, n in calls]
        self._prev_in, self._prev_out = in_tok, out_tok
        return emitted

    def flush(self) -> list[dict]:
        """Si el turno termina con tools sin siguiente paso (error), las cierra solo con su salida."""
        out = []
        for c in self._pending:
            u = {"id": c.id, "name": c.name, "input_tokens": 0, "output_tokens": round(c.out_tokens),
                 "cost": self.prices.cost(0, c.out_tokens), "duration_ms": c.duration_ms}
            self.by_tool[c.id] = u
            out.append(u)
        self._pending = []
        return out

    def summary(self) -> dict:
        """Totales del turno, costo, contexto base (no atribuido) y detalle por tool."""
        attributed_in = sum(u["input_tokens"] for u in self.by_tool.values())
        attributed_out = sum(u["output_tokens"] for u in self.by_tool.values())
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.prices.cost(self.input_tokens, self.output_tokens),
            "base_input_tokens": max(self.input_tokens - attributed_in, 0),
            "base_output_tokens": max(self.output_tokens - attributed_out, 0),
            "prices_configured": self.prices.configured,
            "tools": list(self.by_tool.values()),
        }
