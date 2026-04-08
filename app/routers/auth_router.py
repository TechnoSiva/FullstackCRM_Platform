from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import AuthResponse, UserCreate, UserLogin, UserOut
from app.services.auth_service import login_user, register_user
from app.utils.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user, token = register_user(db, payload)
    return {"user": UserOut.model_validate(user), "token": {"access_token": token, "token_type": "bearer"}}


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user, token = login_user(db, payload.email, payload.password)
    return {"user": UserOut.model_validate(user), "token": {"access_token": token, "token_type": "bearer"}}


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return UserOut.model_validate(current_user)
