from pydantic import BaseModel


class DebateCreate(BaseModel):
    title: str
    description: str = ""
    leftPosition: str = ""
    rightPosition: str = ""
    isActive: bool = False


class DebateUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    leftPosition: str | None = None
    rightPosition: str | None = None
    isActive: bool | None = None
