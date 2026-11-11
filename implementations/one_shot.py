import json
from implementations.common import SYSTEM_RULES, validate_final

PROMPT = '''
Выполни за один проход две операции:
1) извлеки из резюме профиль кандидата и классифицируй навыки;
2) если текст вакансии предоставлен, выдели требования и сопоставь их с навыками кандидата.
Если вакансия отсутствует или пуста, укажи overall_match="not_assessed", пустой список matches
и объясни ограничение в caveats.
Категории навыков: programming, data, devops, design, management, communication,
languages, domain, other.
Уровень: beginner, intermediate, advanced, expert, unknown. Если указан CEFR:
A1/A2 -> beginner, B1/B2 -> intermediate, C1 -> advanced, C2/native -> expert.
Категории выбирай только из перечисленного списка; framework относит к programming,
database/analytics/spreadsheet — к data, soft_skill — к communication,
cloud/container_orchestration — к devops, неизвестную категорию — к other.
Для overall_match используй только high, medium, low, not_assessed;
частичное соответствие обозначай medium.
Статус требования: match, partial_match, not_found, unclear.
Верни JSON с ключами:
{
 "candidate": {
   "candidate_summary": "string",
   "skills": [{"name":"string","category":"programming","proficiency":"unknown",
               "evidence":"string","confidence":0.0}],
   "education": ["string"], "experience_years": null, "additional_notes": ["string"]
 },
 "vacancy": {
   "overall_match":"not_assessed",
   "matches":[{"requirement":"string","related_candidate_skills":["string"],
               "status":"unclear","explanation":"string"}],
   "missing_or_unclear_requirements":["string"], "caveats":["string"]
 },
 "recommendation":"string", "limitations":["string"]
}
Не добавляй markdown и текст вне JSON.

ДАННЫЕ КАНДИДАТА:
{candidate_text}

ДАННЫЕ ВАКАНСИИ (могут быть пустыми):
{vacancy_text}
'''

def run_one_shot(client, candidate_text: str, vacancy_text: str = ""):
    raw, usage = client.complete_json(
        SYSTEM_RULES,
        PROMPT.replace("{candidate_text}", candidate_text).replace("{vacancy_text}", vacancy_text)
    )
    return validate_final(raw), usage
