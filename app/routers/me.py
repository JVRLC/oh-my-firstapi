from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..models import Download, Favorite, ListeningProgress, User
from ..schemas.user import ProgressIn, ProgressOut
from ..services.security import current_user

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/progress", response_model=list[ProgressOut])
async def list_progress(
    user: User = Depends(current_user), db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ListeningProgress)
        .where(ListeningProgress.user_id == user.id)
        .order_by(ListeningProgress.updated_at.desc())
        .limit(20)
    )
    return (await db.execute(stmt)).scalars().all()


@router.put("/progress", response_model=ProgressOut)
async def save_progress(
    payload: ProgressIn,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.get(ListeningProgress, (user.id, payload.recording_id))
    if row is None:
        row = ListeningProgress(user_id=user.id, recording_id=payload.recording_id)
        db.add(row)
    row.position_ms = payload.position_ms
    await db.commit()
    await db.refresh(row)
    return row


@router.post("/favorites/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_favorite(
    recording_id: str,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    if await db.get(Favorite, (user.id, recording_id)) is None:
        db.add(Favorite(user_id=user.id, recording_id=recording_id))
        await db.commit()


@router.delete("/favorites/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    recording_id: str,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(Favorite).where(
            Favorite.user_id == user.id, Favorite.recording_id == recording_id
        )
    )
    await db.commit()


@router.post("/downloads/{recording_id}", status_code=status.HTTP_201_CREATED)
async def register_download(
    recording_id: str,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    if await db.get(Download, (user.id, recording_id)) is not None:
        return {"ok": True}

    if not user.is_premium:
        count = len(
            (
                await db.execute(select(Download).where(Download.user_id == user.id))
            ).scalars().all()
        )
        if count >= settings.free_download_limit:
            raise HTTPException(
                status.HTTP_402_PAYMENT_REQUIRED,
                "Limite de téléchargements atteinte, passez au soutien",
            )

    db.add(Download(user_id=user.id, recording_id=recording_id))
    await db.commit()
    return {"ok": True}
