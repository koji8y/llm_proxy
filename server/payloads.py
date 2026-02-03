from pydantic import BaseModel
from typing import Any


class PromptHolder(BaseModel):
    prompt: str

class PromptToDetectInfo(PromptHolder):
    experiment: bool = True

class PromptToValidate(PromptHolder):
    with_lang_detection: bool = True

class LangJudgmentHistory(BaseModel):
    text: str
    lang: str
    prev_lang: str | None = None
    is_latin: bool = False

class LangInfo(BaseModel):
    final: str
    for_whole: str
    for_parts: list[LangJudgmentHistory] | None
    detail: dict[str, Any] | None = None
    prompt: str
    parameters: dict[str, Any]
