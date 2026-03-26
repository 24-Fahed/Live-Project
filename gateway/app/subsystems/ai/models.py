from pydantic import BaseModel


class AIGenerateRequest(BaseModel):
    prompt: str
    context: str = ""
    config: dict = {}


class AIGenerateResponse(BaseModel):
    content: str
    side: str = "left"
    position: str = "left"
    confidence: float = 0.0
    metadata: dict = {}
