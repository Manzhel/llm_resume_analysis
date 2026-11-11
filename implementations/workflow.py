from implementations.common import SYSTEM_RULES, validate_final
from models import ExtractionOutput, VacancyOutput, MatchingOutput

EXTRACT_PROMPT = '''
Извлеки только сведения о кандидате из резюме. Нормализуй названия навыков.
Для каждого навыка укажи категорию строго из списка programming, data, devops, design,
management, communication, languages, domain, other; подтверждённый уровень (иначе unknown),
evidence и confidence от 0 до 1. Не выдумывай сведения.
Синонимы категорий: framework/markup/stylesheet -> programming; database/analytics/
spreadsheet/BI tool -> data; soft_skill -> communication; language -> languages;
cloud/container orchestration/infrastructure as code -> devops; неизвестное -> other.
CEFR: A1/A2 -> beginner, B1/B2 -> intermediate, C1 -> advanced, C2/native -> expert.
Верни JSON: {"candidate":{"candidate_summary":"...", "skills":[
{"name":"...", "category":"programming", "proficiency":"unknown",
"evidence":"...", "confidence":0.8}],
"education":[], "experience_years":null, "additional_notes":[]}}
РЕЗЮМЕ:
{candidate_text}
'''

VACANCY_PROMPT = '''
Извлеки требования из текста вакансии. Разделяй обязательные и желательные требования
в формулировке строки (например, "Обязательно: Python"). Не добавляй требований,
которых нет в тексте. Верни JSON: {"requirements":["..."],"vacancy_summary":"..."}
ВАКАНСИЯ:
{vacancy_text}
'''

MATCH_PROMPT = '''
Сопоставь извлечённые требования вакансии с профилем кандидата.
Используй только переданные структурированные данные. overall_match должен быть строго
high, medium, low или not_assessed; частичное общее соответствие обозначай medium.
Для каждого требования укажи
related_candidate_skills и статус match / partial_match / not_found / unclear.
Не считай отсутствие упоминания доказательством отсутствия навыка: используй not_found
как "не найдено в предоставленном резюме". Если текст недостаточен — unclear.
Верни JSON:
{"vacancy":{"overall_match":"high|medium|low|not_assessed",
"matches":[{"requirement":"...", "related_candidate_skills":[],
"status":"match|partial_match|not_found|unclear","explanation":"..."}],
"missing_or_unclear_requirements":[],"caveats":[]},"recommendation":"...",
"limitations":[]}
ПРОФИЛЬ КАНДИДАТА:
{candidate_json}
ТРЕБОВАНИЯ ВАКАНСИИ:
{requirements_json}
'''

def run_workflow(client, candidate_text: str, vacancy_text: str = ""):
    # Stage 1: candidate skill extraction/classification
    candidate_raw, usage1 = client.complete_json(
        SYSTEM_RULES, EXTRACT_PROMPT.replace("{candidate_text}", candidate_text)
    )
    candidate = ExtractionOutput.model_validate(candidate_raw).candidate

    # Stage 2: vacancy requirements extraction (or explicit empty-vacancy branch)
    if vacancy_text.strip():
        vacancy_raw, usage2 = client.complete_json(
            SYSTEM_RULES, VACANCY_PROMPT.replace("{vacancy_text}", vacancy_text)
        )
        vacancy_data = VacancyOutput.model_validate(vacancy_raw)
        requirements = vacancy_data.requirements
        vacancy_summary = vacancy_data.vacancy_summary
    else:
        usage2 = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        requirements = []
        vacancy_summary = "Вакансия не предоставлена; сопоставление не выполнялось."

    # Stage 3: matching uses validated structured outputs from previous stages
    if requirements:
        matching_raw, usage3 = client.complete_json(
            SYSTEM_RULES,
            MATCH_PROMPT.replace("{candidate_json}", candidate.model_dump_json()).replace(
                "{requirements_json}", vacancy_data.model_dump_json()
            )
        )
        matching = MatchingOutput.model_validate(matching_raw)
        vacancy_result = matching.vacancy
        recommendation = matching.recommendation
        limitations = matching.limitations
    else:
        usage3 = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        from models import VacancyAnalysis
        vacancy_result = VacancyAnalysis(
            overall_match="not_assessed", matches=[],
            missing_or_unclear_requirements=[],
            caveats=[vacancy_summary]
        )
        recommendation = "Профиль навыков сформирован. Для оценки соответствия нужна вакансия."
        limitations = ["Сопоставление с требованиями вакансии не выполнялось."]

    result = {
        "candidate": candidate.model_dump(),
        "vacancy": vacancy_result.model_dump(),
        "recommendation": recommendation,
        "limitations": limitations
    }
    return validate_final(result), merge_usage(usage1, usage2, usage3)

def merge_usage(*items):
    keys = ("prompt_tokens", "completion_tokens", "total_tokens")
    return {key: sum(int(item.get(key, 0) or 0) for item in items) for key in keys}
