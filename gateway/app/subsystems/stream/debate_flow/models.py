from pydantic import BaseModel


class SegmentItem(BaseModel):
    name: str
    duration: int = 180
    side: str = "both"  # "left" | "right" | "both"


class DebateFlowSaveRequest(BaseModel):
    stream_id: str
    segments: list[SegmentItem]


class DebateFlowControlRequest(BaseModel):
    stream_id: str
    action: str  # "start" | "pause" | "resume" | "reset" | "next" | "prev"
