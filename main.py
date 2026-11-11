import argparse
import json
from pathlib import Path
from llm.client import LLMClient
from implementations.one_shot import run_one_shot
from implementations.workflow import run_workflow

def main():
    parser = argparse.ArgumentParser(description="Классификатор навыков кандидатов")
    parser.add_argument("--candidate", required=True, help="Путь к текстовому файлу резюме")
    parser.add_argument("--vacancy", default="", help="Путь к текстовому файлу вакансии (необязательно)")
    parser.add_argument("--mode", choices=["one-shot", "workflow"], default="workflow")
    parser.add_argument("--output", default="results/last_result.json")
    args = parser.parse_args()

    candidate_text = Path(args.candidate).read_text(encoding="utf-8")
    vacancy_text = Path(args.vacancy).read_text(encoding="utf-8") if args.vacancy else ""

    client = LLMClient()
    fn = run_one_shot if args.mode == "one-shot" else run_workflow
    result, usage = fn(client, candidate_text, vacancy_text)

    payload = {"result": result, "usage": usage, "mode": args.mode}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\nРезультат сохранён: {out}")

if __name__ == "__main__":
    main()
