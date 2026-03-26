from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.infra.auth.config import jwt_settings


def sign_token(user_info: dict) -> str:
    payload = {
        **user_info,
        "exp": datetime.now(timezone.utc) + timedelta(hours=jwt_settings.JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, jwt_settings.JWT_SECRET, algorithm=jwt_settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    return jwt.decode(token, jwt_settings.JWT_SECRET, algorithms=[jwt_settings.JWT_ALGORITHM])
