from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Recording
from ..schemas.catalog import SignedUrlOut
from ..services.signing_service import signed_url

router = APIRouter(prefix="/recordings", tags=["player"])


@router.post("/{recording_id}/signed-url", response_model=SignedUrlOut)
async def get_signed_url(recording_id: str, db: AsyncSession = Depends(get_db)):
    rec = await db.get(Recording, recording_id)
    if rec is None or not rec.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Enregistrement introuvable")

    rec.play_count += 1
    await db.commit()

    url, ttl = signed_url(rec.audio_path)
    return SignedUrlOut(url=url, expires_in_sec=ttl)
