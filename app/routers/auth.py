from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..models import User
from ..schemas.user import OtpRequest, OtpVerify, TokenOut, UserOut
from ..services import otp_service
from ..services.security import create_token, current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp")
async def request_otp(payload: OtpRequest):
    code = otp_service.generate(payload.phone)
    # Only echo the code while OTP_DEV_MODE is on.
    return {"sent": True, "dev_code": code if settings.otp_dev_mode else None}


@router.post("/verify", response_model=TokenOut)
async def verify_otp(payload: OtpVerify, db: AsyncSession = Depends(get_db)):
    if not otp_service.verify(payload.phone, payload.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Code invalide ou expiré")

    result = await db.execute(select(User).where(User.phone == payload.phone))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(phone=payload.phone)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return TokenOut(access_token=create_token(user.id))


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(current_user)):
    return user
