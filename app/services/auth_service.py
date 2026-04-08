from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import create_user, get_user_by_email
from app.schemas.auth import UserCreate
from app.utils.security import create_access_token, hash_password, verify_password


def register_user(db: Session, payload: UserCreate):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = create_user(
        db,
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        role=payload.role,
    )
    token = create_access_token(str(user.id), user.role.value)
    return user, token


def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(str(user.id), user.role.value)
    return user, token
