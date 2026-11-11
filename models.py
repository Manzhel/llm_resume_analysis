from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

class Skill(BaseModel):
    name: str = Field(description="Нормализованное название навыка")
    category: Literal[
        "programming", "data", "devops", "design", "management",
        "communication", "languages", "domain", "other"
    ]
    proficiency: Literal["beginner", "intermediate", "advanced", "expert", "unknown"]
    evidence: str = Field(description="Фрагмент или краткое указание на основание из входных данных")
    confidence: float = Field(ge=0, le=1)

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value):
        if not isinstance(value, str):
            return "other"
        value = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "framework": "programming", "markup": "programming", "stylesheet": "programming",
            "database": "data", "bi_tool": "data", "analytics": "data", "spreadsheet": "data",
            "tool": "other", "build_tool": "programming", "testing": "programming",
            "language": "languages", "soft_skill": "communication",
            "project_management": "management", "cloud": "devops",
            "container_orchestration": "devops", "infrastructure_as_code": "devops",
            "operating_system": "devops", "design_tool": "design",
            "research": "domain", "marketing": "domain", "advertising": "domain",
            "accounting_software": "domain", "accounting_process": "domain",
        }
        allowed = {"programming", "data", "devops", "design", "management",
                   "communication", "languages", "domain", "other"}
        normalized = aliases.get(value, value)
        return normalized if normalized in allowed else "other"

    @field_validator("proficiency", mode="before")
    @classmethod
    def normalize_proficiency(cls, value):
        if not isinstance(value, str):
            return "unknown"
        value = value.strip().lower()
        aliases = {
            "a1": "beginner", "a2": "beginner", "b1": "intermediate",
            "b2": "intermediate", "c1": "advanced", "c2": "expert",
            "native": "expert", "fluent": "advanced", "professional": "advanced",
            "working": "intermediate", "basic": "beginner",
        }
        allowed = {"beginner", "intermediate", "advanced", "expert", "unknown"}
        normalized = aliases.get(value, value)
        return normalized if normalized in allowed else "unknown"

class CandidateProfile(BaseModel):
    candidate_summary: str
    skills: list[Skill]
    education: list[str] = []
    experience_years: float | None = None
    additional_notes: list[str] = []

class RequirementMatch(BaseModel):
    requirement: str
    related_candidate_skills: list[str]
    status: Literal["match", "partial_match", "not_found", "unclear"]
    explanation: str

class VacancyAnalysis(BaseModel):
    overall_match: Literal["high", "medium", "low", "not_assessed"]

    @field_validator("overall_match", mode="before")
    @classmethod
    def normalize_overall_match(cls, value):
        if not isinstance(value, str):
            return "not_assessed"
        value = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {"partial": "medium", "partial_match": "medium", "moderate": "medium",
                   "strong": "high", "good": "high", "weak": "low", "poor": "low",
                   "unknown": "not_assessed", "not_assessed": "not_assessed"}
        normalized = aliases.get(value, value)
        return normalized if normalized in {"high", "medium", "low", "not_assessed"} else "not_assessed"
    matches: list[RequirementMatch]
    missing_or_unclear_requirements: list[str]
    caveats: list[str] = []

class AnalysisResult(BaseModel):
    candidate: CandidateProfile
    vacancy: VacancyAnalysis
    recommendation: str
    limitations: list[str] = []

class ExtractionOutput(BaseModel):
    candidate: CandidateProfile

class VacancyOutput(BaseModel):
    requirements: list[str]
    vacancy_summary: str

class MatchingOutput(BaseModel):
    vacancy: VacancyAnalysis
    recommendation: str
    limitations: list[str] = []
