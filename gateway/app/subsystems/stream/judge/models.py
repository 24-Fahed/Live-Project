from pydantic import BaseModel


class JudgeItem(BaseModel):
    id: str
    name: str
    role: str = ""
    avatar: str = ""
    votes: int = 0


class JudgesSaveRequest(BaseModel):
    stream_id: str
    judges: list[JudgeItem]
