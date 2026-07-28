from pydantic import BaseModel, ConfigDict


class KourelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    city: str | None = None
    bio: str | None = None
    photo_url: str | None = None
    parent_id: str | None = None


class KhassaideOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    title_latin: str
    title_arabic: str | None = None
    meaning_fr: str | None = None


class RecordingOut(BaseModel):
    id: str
    duration_sec: int
    khassaide: KhassaideOut
    kourel: KourelOut
    event_name: str | None = None


class RecordingDetail(RecordingOut):
    pass


class SignedUrlOut(BaseModel):
    url: str
    expires_in_sec: int
