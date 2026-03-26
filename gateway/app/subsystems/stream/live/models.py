from pydantic import BaseModel


class StreamCreate(BaseModel):
    name: str
    url: str | None = None
    type: str = "hls"
    description: str = ""


class StreamUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    type: str | None = None
    description: str | None = None
    enabled: bool | None = None


class LiveStartRequest(BaseModel):
    streamId: str
    autoStartAI: bool = False
    notifyUsers: bool = False


class LiveStopRequest(BaseModel):
    streamId: str
    saveStatistics: bool = True
    notifyUsers: bool = False
