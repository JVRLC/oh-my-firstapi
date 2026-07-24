import random
from datetime import datetime, timedelta

from ..config import settings

# In-memory store; replace with Redis before going to production.
_codes: dict[str, tuple[str, datetime]] = {}
_TTL = timedelta(minutes=5)


def generate(phone: str) -> str:
    code = f"{random.randint(0, 999999):06d}"
    _codes[phone] = (code, datetime.utcnow() + _TTL)
    if not settings.otp_dev_mode:
        _send_sms(phone, code)
    return code


def verify(phone: str, code: str) -> bool:
    entry = _codes.get(phone)
    if entry is None:
        return False
    expected, expires_at = entry
    if datetime.utcnow() > expires_at:
        _codes.pop(phone, None)
        return False
    if code != expected:
        return False
    _codes.pop(phone, None)
    return True


def _send_sms(phone: str, code: str) -> None:
    # Plug a Senegalese SMS aggregator here.
    raise NotImplementedError("SMS provider not configured")
