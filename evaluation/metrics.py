from collections import Counter

def skill_metrics(predicted_names, expected_names):
    pred = {x.strip().lower() for x in predicted_names}
    expected = {x.strip().lower() for x in expected_names}
    if not expected:
        return {"precision": 1.0 if not pred else 0.0, "recall": 1.0, "f1": 1.0 if not pred else 0.0}
    tp = len(pred & expected)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(expected)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}

def summarize_runs(rows):
    if not rows:
        return {}
    n = len(rows)
    success = sum(1 for r in rows if r.get("success"))
    successful = [r for r in rows if r.get("success")]
    def mean_for_successful(key):
        values = [r.get(key) for r in successful if r.get(key) is not None]
        return sum(values) / len(values) if values else None
    return {
        "success_rate": success / n,
        "mean_latency_seconds": sum(r.get("latency_seconds", 0) for r in rows) / n,
        "mean_llm_calls": sum(r.get("llm_calls", 0) for r in rows) / n,
        "mean_total_tokens_successful": mean_for_successful("total_tokens"),
        "mean_skill_f1_successful": mean_for_successful("skill_f1"),
        "successful_runs_for_quality_metrics": success
    }
