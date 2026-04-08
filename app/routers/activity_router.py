from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas.activity import ActivityCreate, ActivityOut
from app.services.activity_service import create_activity_service, list_activities_service
from app.utils.deps import get_current_user, require_roles

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SALES)),
):
    return create_activity_service(db, payload, current_user)


@router.get("/lead/{lead_id}", response_model=list[ActivityOut])
def list_activities(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_activities_service(db, lead_id, current_user)
