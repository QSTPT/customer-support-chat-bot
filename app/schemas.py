from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    system: str = "You are a concise, helpful assistant." # Will be changed later.
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=1, le=8192)