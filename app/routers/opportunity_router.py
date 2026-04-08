from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas.opportunity import OpportunityCreate, OpportunityOut, OpportunityUpdate
from app.services.opportunity_service import (
    create_opportunity_service,
    delete_opportunity_service,
    list_opportunities_service,
    update_opportunity_service,
)
from app.utils.deps import get_current_user, require_roles

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.post("", response_model=OpportunityOut, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SALES)),
):
    return create_opportunity_service(db, payload, current_user)


@router.get("", response_model=list[OpportunityOut])
def list_opportunities(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_opportunities_service(db, current_user)


@router.put("/{opportunity_id}", response_model=OpportunityOut)
def update_opportunity(
    opportunity_id: int,
    payload: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.SALES)),
):
    return update_opportunity_service(db, opportunity_id, payload, current_user)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    delete_opportunity_service(db, opportunity_id, current_user)
