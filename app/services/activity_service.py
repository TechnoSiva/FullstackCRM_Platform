from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.repositories.activity_repository import create_activity, list_activities_for_lead
from app.repositories.lead_repository import get_lead_by_id
from app.schemas.activity import ActivityCreate
from app.services.lead_service import recalculate_lead_score_for_lead_id


def create_activity_service(db: Session, payload: ActivityCreate, current_user: User):
    lead = get_lead_by_id(db, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    if current_user.role == UserRole.SALES and lead.assigned_to_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create activity for this lead")

    activity = create_activity(db, **payload.model_dump())
    recalculate_lead_score_for_lead_id(db, payload.lead_id)
    return activity


def list_activities_service(db: Session, lead_id: int, current_user: User):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    if current_user.role == UserRole.SALES and lead.assigned_to_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view activities for this lead")

    return list_activities_for_lead(db, lead_id)
