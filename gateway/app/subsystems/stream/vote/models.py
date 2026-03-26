from pydantic import BaseModel


class UserVoteRequest(BaseModel):
    streamId: str = "default"
    userId: str = ""
    leftVotes: int = 0
    rightVotes: int = 0


class AdminVoteUpdate(BaseModel):
    streamId: str = "default"
    action: str = "set"
    leftVotes: int = 0
    rightVotes: int = 0


class ResetVoteRequest(BaseModel):
    streamId: str = "default"
    resetTo: dict | None = None
    saveBackup: bool = True
