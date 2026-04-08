from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.repositories.lead_repository import get_lead_by_id
from app.repositories.opportunity_repository import (
    create_opportunity,
    delete_opportunity,
    get_opportunity_by_id,
    list_opportunities,
    list_opportunities_by_assignee,
    update_opportunity,
)
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.services.lead_service import recalculate_lead_score_for_lead_id


def create_opportunity_service(db: Session, payload: OpportunityCreate, current_user: User):
    lead = get_lead_by_id(db, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    if current_user.role == UserRole.SALES and lead.assigned_to_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create opportunity for this lead")

    opportunity = create_opportunity(db, **payload.model_dump())
    recalculate_lead_score_for_lead_id(db, payload.lead_id)
    return opportunity


def list_opportunities_service(db: Session, current_user: User):
    if current_user.role == UserRole.SALES:
        return list_opportunities_by_assignee(db, current_user.id)
    return list_opportunities(db)


def update_opportunity_service(db: Session, opportunity_id: int, payload: OpportunityUpdate, current_user: User):
    opportunity = get_opportunity_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    if current_user.role == UserRole.SALES and opportunity.lead.assigned_to_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update this opportunity")

    updates = payload.model_dump(exclude_unset=True)
    updated = update_opportunity(db, opportunity, **updates)
    recalculate_lead_score_for_lead_id(db, updated.lead_id)
    return updated


def delete_opportunity_service(db: Session, opportunity_id: int, current_user: User):
    opportunity = get_opportunity_by_id(db, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    lead_id = opportunity.lead_id
    delete_opportunity(db, opportunity)
    recalculate_lead_score_for_lead_id(db, lead_id)
