import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

def validate_config():
    if not API_KEY or API_KEY == "вставьте_сюда_свой_ключ":
        raise RuntimeError(
            "Не найден OPENROUTER_API_KEY. Создайте файл .env на основе .env.example "
            "и вставьте API-ключ OpenRouter."
        )
