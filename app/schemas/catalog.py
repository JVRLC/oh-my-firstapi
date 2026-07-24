from pydantic import BaseModel, ConfigDict


class KourelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    city: str | None = None
    bio: str | None = None
    photo_url: str | None = None


class VerseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    position: int
    text_arabic: str
    translit: str | None = None
    translation_fr: str | None = None


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


class RecordingDetail(RecordingOut):
    verses: list[VerseOut]


class TimingOut(BaseModel):
    verse_position: int
    start_ms: int
    end_ms: int


class SignedUrlOut(BaseModel):
    url: str
    expires_in_sec: int
