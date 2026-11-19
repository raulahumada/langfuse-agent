from api.costs import Prices, TurnMeter


def test_attributes_result_tokens_to_tools():
    """Los tokens de entrada del paso siguiente se reparten entre las tools según el tamaño de su resultado."""
    m = TurnMeter(prices=Prices(1.0, 2.0))  # USD / 1M tokens
    assert m.on_ai_step(1000, 50, [("a", "get_health"), ("b", "diagnose_errors")]) == []
    m.record_result("a", 100, 10)
    m.record_result("b", 300, 20)
    out = m.on_ai_step(1000 + 50 + 400, 30, [])  # +400 tokens de resultados
    by = {u["id"]: u for u in out}
    assert by["a"]["input_tokens"] == 100 and by["b"]["input_tokens"] == 300
    assert by["a"]["output_tokens"] == 25
    s = m.summary()
    assert s["input_tokens"] == 2450 and s["output_tokens"] == 80
    assert s["base_input_tokens"] == 2450 - 400
    assert s["cost"] == (2450 * 1 + 80 * 2) / 1_000_000


def test_no_prices_means_no_cost():
    """Sin precios configurados no se calcula costo (solo tokens)."""
    m = TurnMeter(prices=Prices())
    m.on_ai_step(10, 5, [])
    assert m.summary()["cost"] is None and not m.summary()["prices_configured"]
