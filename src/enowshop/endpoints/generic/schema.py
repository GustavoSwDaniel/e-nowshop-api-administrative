from pydantic import BaseModel


class LogoutSchema(BaseModel):
    refresh_token: str