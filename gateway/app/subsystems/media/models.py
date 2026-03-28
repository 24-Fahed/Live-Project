from pydantic import BaseModel


class MediaStreamInfo(BaseModel):
    streamId: str
    pushUrl: str
    playUrl: str
    publishStatus: str


class MediaHookPayload(BaseModel):
    app: str | None = None
    stream: str | None = None
    client_id: str | None = None
    ip: str | None = None
    param: str | None = None
