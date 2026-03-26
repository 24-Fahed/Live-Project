from pydantic import BaseModel


class CommentCreate(BaseModel):
    contentId: str
    text: str
    user: str = "匿名用户"
    avatar: str = "👤"


class LikeCreate(BaseModel):
    contentId: str
    commentId: str | None = None


class CommentDelete(BaseModel):
    contentId: str


class AIContentCreate(BaseModel):
    streamId: str = "default"
    content: str
    side: str = "left"
    confidence: float = 0.0


class AIStartRequest(BaseModel):
    streamId: str
    settings: dict = {}
    notifyUsers: bool = True


class AIStopRequest(BaseModel):
    streamId: str = ""
    saveHistory: bool = True
    notifyUsers: bool = True


class AIToggleRequest(BaseModel):
    streamId: str
    action: str  # "pause" | "resume"
    notifyUsers: bool = True
