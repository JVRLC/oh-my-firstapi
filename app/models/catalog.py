import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Kourel(Base):
    __tablename__ = "kourels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(150))
    # Filesystem/S3-safe name, used to build the storage folder for this kourel's audio.
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Set when this kourel is a sub-group of a larger association (e.g. HT Touba).
    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("kourels.id", ondelete="CASCADE"), nullable=True
    )

    parent: Mapped["Kourel | None"] = relationship(
        remote_side=[id], back_populates="children"
    )
    children: Mapped[list["Kourel"]] = relationship(back_populates="parent")
    recordings: Mapped[list["Recording"]] = relationship(back_populates="kourel")


class Khassaide(Base):
    __tablename__ = "khassaides"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    slug: Mapped[str] = mapped_column(String(200), unique=True)
    title_latin: Mapped[str] = mapped_column(String(200))
    title_arabic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meaning_fr: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    recordings: Mapped[list["Recording"]] = relationship(back_populates="khassaide")


class Recording(Base):
    __tablename__ = "recordings"
    __table_args__ = (UniqueConstraint("khassaide_id", "kourel_id", "event_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    khassaide_id: Mapped[str] = mapped_column(ForeignKey("khassaides.id", ondelete="CASCADE"))
    kourel_id: Mapped[str] = mapped_column(ForeignKey("kourels.id", ondelete="CASCADE"))
    # Free-text: the gathering this was recorded at (e.g. "Magal de Touba 2025").
    event_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    duration_sec: Mapped[int] = mapped_column(Integer)
    # Path relative to the CDN, signed on demand.
    audio_path: Mapped[str] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    play_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    khassaide: Mapped[Khassaide] = relationship(back_populates="recordings")
    kourel: Mapped[Kourel] = relationship(back_populates="recordings")
