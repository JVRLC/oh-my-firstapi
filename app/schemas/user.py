from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OtpRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=20)


class OtpVerify(BaseModel):
    phone: str
    code: str = Field(min_length=4, max_length=6)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    phone: str
    display_name: str | None = None
    is_premium: bool


class ProgressIn(BaseModel):
    recording_id: str
    position_ms: int


class ProgressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recording_id: str
    position_ms: int
    updated_at: datetime
