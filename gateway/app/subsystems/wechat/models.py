from pydantic import BaseModel


class WechatLoginRequest(BaseModel):
    code: str = ""
    userInfo: dict | None = None
    encryptedData: str | None = None
    iv: str | None = None
