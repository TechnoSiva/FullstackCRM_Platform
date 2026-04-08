from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import delete_user, get_user_by_id, list_users, update_user_role
from app.schemas.auth import UserCreate, UserRoleUpdate
from app.services.auth_service import register_user


def list_users_service(db: Session):
    return list_users(db)


def create_user_by_admin_service(db: Session, payload: UserCreate):
    user, _ = register_user(db, payload)
    return user


def update_user_role_service(db: Session, user_id: int, payload: UserRoleUpdate):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return update_user_role(db, user, payload.role)


def delete_user_service(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    delete_user(db, user)
