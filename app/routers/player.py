from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Recording, VerseTiming
from ..schemas.catalog import SignedUrlOut, TimingOut
from ..services.signing_service import signed_url

router = APIRouter(prefix="/recordings", tags=["player"])


@router.get("/{recording_id}/timestamps", response_model=list[TimingOut])
async def timestamps(recording_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(VerseTiming)
        .options(selectinload(VerseTiming.verse))
        .where(VerseTiming.recording_id == recording_id)
        .order_by(VerseTiming.start_ms)
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [
        TimingOut(verse_position=r.verse.position, start_ms=r.start_ms, end_ms=r.end_ms)
        for r in rows
    ]


@router.post("/{recording_id}/signed-url", response_model=SignedUrlOut)
async def get_signed_url(recording_id: str, db: AsyncSession = Depends(get_db)):
    rec = await db.get(Recording, recording_id)
    if rec is None or not rec.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enregistrement introuvable")

    rec.play_count += 1
    await db.commit()

    url, ttl = signed_url(rec.audio_path)
    return SignedUrlOut(url=url, expires_in_sec=ttl)
