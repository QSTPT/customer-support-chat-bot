from pydantic import BaseModel, Field
from app.prompts import build_messages
from typing import Literal

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    preset: Literal["default"] = "default"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=1, le=8192)
    
    @property
    def messages(self) -> list[dict[str, str]]:
        return build_messages(self.preset, self.prompt)