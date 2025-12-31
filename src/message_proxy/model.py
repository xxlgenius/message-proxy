from pydantic import BaseModel


class WechatBody(BaseModel):
    touser: str = "@all"
    message: str | None = None
