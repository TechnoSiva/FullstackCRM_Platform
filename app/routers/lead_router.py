from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas.lead import LeadCreate, LeadOut, LeadUpdate
from app.services.lead_service import (
    create_lead_service,
    delete_lead_service,
    get_lead_service,
    list_leads_service,
    update_lead_service,
)
from app.utils.deps import get_current_user, require_roles

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SALES)),
):
    if current_user.role == UserRole.SALES and payload.assigned_to_user_id not in (None, current_user.id):
        payload.assigned_to_user_id = current_user.id
    return create_lead_service(db, payload)


@router.get("", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_leads_service(db, current_user)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_lead_service(db, lead_id, current_user)


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SALES)),
):
    return update_lead_service(db, lead_id, payload, current_user)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    delete_lead_service(db, lead_id)
