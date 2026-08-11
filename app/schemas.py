import json
from typing import Literal
from pydantic import BaseModel, Field
from app.prompts import PROMPTS, build_messages

class SupportAnswer(BaseModel):
    in_scope: bool
    category: Literal["setup", "connection", "billing", "privacy", "other"]
    answer: str = Field(..., min_length=1)
    steps: list[str] = Field(default_factory=list)
    escalate: bool = False

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    preset: Literal["default", "structured"] = "default"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=1, le=8192)

    @property
    def messages(self) -> list[dict[str, str]]:
        return build_messages(
            self.preset,
            self.prompt,
            json.dumps(SupportAnswer.model_json_schema(), indent=2),
        )