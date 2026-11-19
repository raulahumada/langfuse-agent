from mcp_langfuse.diagnostics import group_errors


# Helper: arma una observación de error de Langfuse con metadata `error.*`.
def obs(name, msg, trace, ts, **meta):
    return {"name": name, "statusMessage": msg, "traceId": trace, "startTime": ts,
            "input": '{"args": [1]}', "metadata": {f"error.{k}": v for k, v in meta.items()}}


def test_groups_and_ranks_by_count():
    """Agrupa errores iguales y ordena los incidentes por frecuencia."""
    data = [obs("a", "x", "t1", "1"), obs("a", "x", "t2", "2", type="KeyError", location="p.py:3 en f"),
            obs("b", "y", "t3", "3")]
    r = group_errors(data, total_observations=10)
    assert r["failed_traces"] == 3
    top = r["incidents"][0]
    assert (top["operation"], top["count"], top["exception_type"]) == ("a", 2, "KeyError")
    assert top["sample_input"] == {"args": [1]}


def test_collapses_nested_spans_of_same_trace():
    """Un mismo trace con spans anidados con error cuenta una sola vez (gana el más informativo)."""
    data = [obs("child", "boom", "t1", "1"), obs("parent", "boom", "t1", "2", type="KeyError")]
    r = group_errors(data)
    assert r["failed_traces"] == 1 and r["incidents"][0]["operation"] == "parent"
