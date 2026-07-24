from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Khassaide, Kourel, Recording
from ..schemas.catalog import KourelOut, RecordingDetail, RecordingOut

router = APIRouter(tags=["catalog"])


def _with_relations(stmt):
    return stmt.options(
        selectinload(Recording.khassaide), selectinload(Recording.kourel)
    )


@router.get("/recordings", response_model=list[RecordingOut])
async def list_recordings(
    kourel_id: str | None = None,
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = _with_relations(select(Recording).where(Recording.is_published))
    if kourel_id:
        stmt = stmt.where(Recording.kourel_id == kourel_id)
    result = await db.execute(stmt.limit(limit))
    return result.scalars().all()


@router.get("/recordings/{recording_id}", response_model=RecordingDetail)
async def get_recording(recording_id: str, db: AsyncSession = Depends(get_db)):
    stmt = _with_relations(select(Recording)).options(
        selectinload(Recording.khassaide).selectinload(Khassaide.verses)
    ).where(Recording.id == recording_id)
    rec = (await db.execute(stmt)).scalar_one_or_none()
    if rec is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enregistrement introuvable")

    return RecordingDetail(
        id=rec.id,
        duration_sec=rec.duration_sec,
        khassaide=rec.khassaide,
        kourel=rec.kourel,
        verses=rec.khassaide.verses,
    )


@router.get("/kourels", response_model=list[KourelOut])
async def list_kourels(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Kourel))).scalars().all()


@router.get("/search", response_model=list[RecordingOut])
async def search(q: str = Query(min_length=2), db: AsyncSession = Depends(get_db)):
    pattern = f"%{q}%"
    stmt = (
        _with_relations(select(Recording))
        .join(Khassaide)
        .join(Kourel)
        .where(
            Recording.is_published,
            or_(
                Khassaide.title_latin.ilike(pattern),
                Khassaide.title_arabic.ilike(pattern),
                Kourel.name.ilike(pattern),
            ),
        )
        .limit(30)
    )
    return (await db.execute(stmt)).scalars().all()
