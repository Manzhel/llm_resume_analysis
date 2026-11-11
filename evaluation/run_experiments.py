import json, time, csv
from pathlib import Path
from llm.client import LLMClient
from implementations.one_shot import run_one_shot
from implementations.workflow import run_workflow
from evaluation.metrics import skill_metrics, summarize_runs

DATA = Path("evaluation/test_dataset.json")
OUT = Path("results")
OUT.mkdir(exist_ok=True)

def main():
    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    client = LLMClient()
    all_rows = []
    summaries = {}
    for mode, fn, calls in [
        ("one-shot", run_one_shot, 1),
        ("workflow", run_workflow, 3)
    ]:
        rows = []
        for item in dataset:
            start = time.perf_counter()
            calls_before = client.total_calls
            try:
                result, usage = fn(client, item["candidate"], item["vacancy"])
                elapsed = time.perf_counter() - start
                names = [s["name"] for s in result["candidate"]["skills"]]
                scores = skill_metrics(names, item["expected_skills"])
                row = {
                    "id": item["id"], "mode": mode, "success": True,
                    "latency_seconds": round(elapsed, 3), "llm_calls": client.total_calls - calls_before,
                    "prompt_tokens": usage["prompt_tokens"],
                    "completion_tokens": usage["completion_tokens"],
                    "total_tokens": usage["total_tokens"],
                    "skill_precision": round(scores["precision"], 4),
                    "skill_recall": round(scores["recall"], 4),
                    "skill_f1": round(scores["f1"], 4),
                    "ambiguous": item["ambiguous"]
                }
            except Exception as exc:
                row = {"id": item["id"], "mode": mode, "success": False,
                       "latency_seconds": round(time.perf_counter() - start, 3),
                       "llm_calls": client.total_calls - calls_before, "prompt_tokens": 0, "completion_tokens": 0,
                       "total_tokens": 0, "skill_precision": None, "skill_recall": None,
                       "skill_f1": None, "ambiguous": item["ambiguous"], "error": str(exc)}
            rows.append(row)
            all_rows.append(row)
            print(mode, item["id"], row, flush=True)
            time.sleep(2)
        summaries[mode] = summarize_runs([
            {**r, "skill_f1": r["skill_f1"]} for r in rows
        ])
    with (OUT / "experiment_rows.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=sorted({k for r in all_rows for k in r}))
        writer.writeheader()
        writer.writerows(all_rows)
    (OUT / "comparison.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nИтог:", json.dumps(summaries, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
