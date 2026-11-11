import json
import time
from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL, validate_config

class LLMClient:
    def __init__(self):
        validate_config()
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
            timeout=120.0,
            max_retries=0,
            default_headers={
                "HTTP-Referer": "https://localhost",
                "X-Title": "HR Candidate Skill Classifier"
            }
        )
        self.model = MODEL
        self.total_calls = 0

    def complete_json(self, system_prompt: str, user_prompt: str, max_retries: int = 1):
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                self.total_calls += 1
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                message = response.choices[0].message.content or ""
                usage = response.usage
                usage_info = {
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                    "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
                    "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0
                }
                try:
                    return json.loads(message), usage_info
                except json.JSONDecodeError as exc:
                    last_error = f"Некорректный JSON: {exc}. Ответ: {message[:500]}"
            except Exception as exc:
                last_error = f"Ошибка обращения к OpenRouter: {type(exc).__name__}: {exc}"
                if attempt == max_retries:
                    break
                time.sleep(min(2 ** (attempt + 1), 8))
        raise RuntimeError(last_error or "Неизвестная ошибка LLM")
