import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Kourel(Base):
    __tablename__ = "kourels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(150))
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    recordings: Mapped[list["Recording"]] = relationship(back_populates="kourel")


class Khassaide(Base):
    __tablename__ = "khassaides"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    title_latin: Mapped[str] = mapped_column(String(200))
    title_arabic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meaning_fr: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    verses: Mapped[list["Verse"]] = relationship(
        back_populates="khassaide", order_by="Verse.position"
    )
    recordings: Mapped[list["Recording"]] = relationship(back_populates="khassaide")


class Verse(Base):
    __tablename__ = "verses"
    __table_args__ = (UniqueConstraint("khassaide_id", "position"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    khassaide_id: Mapped[str] = mapped_column(ForeignKey("khassaides.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer)
    text_arabic: Mapped[str] = mapped_column(Text)
    translit: Mapped[str | None] = mapped_column(Text, nullable=True)
    translation_fr: Mapped[str | None] = mapped_column(Text, nullable=True)
    translation_wo: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Set once a religious committee has approved the text.
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)

    khassaide: Mapped[Khassaide] = relationship(back_populates="verses")


class Recording(Base):
    __tablename__ = "recordings"
    __table_args__ = (UniqueConstraint("khassaide_id", "kourel_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    khassaide_id: Mapped[str] = mapped_column(ForeignKey("khassaides.id", ondelete="CASCADE"))
    kourel_id: Mapped[str] = mapped_column(ForeignKey("kourels.id", ondelete="CASCADE"))
    duration_sec: Mapped[int] = mapped_column(Integer)
    # Path relative to the CDN, signed on demand.
    audio_path: Mapped[str] = mapped_column(Text)
    quality_high: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    play_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    khassaide: Mapped[Khassaide] = relationship(back_populates="recordings")
    kourel: Mapped[Kourel] = relationship(back_populates="recordings")
    timings: Mapped[list["VerseTiming"]] = relationship(
        back_populates="recording", order_by="VerseTiming.start_ms"
    )


class VerseTiming(Base):
    __tablename__ = "verse_timestamps"

    recording_id: Mapped[str] = mapped_column(
        ForeignKey("recordings.id", ondelete="CASCADE"), primary_key=True
    )
    verse_id: Mapped[str] = mapped_column(
        ForeignKey("verses.id", ondelete="CASCADE"), primary_key=True
    )
    start_ms: Mapped[int] = mapped_column(Integer)
    end_ms: Mapped[int] = mapped_column(Integer)

    recording: Mapped[Recording] = relationship(back_populates="timings")
    verse: Mapped[Verse] = relationship()
