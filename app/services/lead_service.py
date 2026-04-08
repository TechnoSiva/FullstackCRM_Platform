from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ml.model_loader import load_model
from app.models import Lead, User, UserRole
from app.repositories.activity_repository import count_activities_for_lead, first_activity_for_lead
from app.repositories.lead_repository import create_lead, delete_lead, get_lead_by_id, list_leads, list_leads_by_assignee, update_lead
from app.repositories.opportunity_repository import get_primary_opportunity_for_lead
from app.schemas.lead import LeadCreate, LeadUpdate

LEAD_SOURCE_MAP = {"website": 0, "referral": 1, "event": 2, "cold_call": 3}
SENTINEL_FIRST_RESPONSE_HOURS = 72.0


def _source_to_code(source: str) -> int:
    return LEAD_SOURCE_MAP.get(source.lower(), 0)


def _score_lead(source: str, interaction_count: int, deal_value: float, first_response_hours: float) -> float:
    model = load_model()
    features = [[_source_to_code(source), interaction_count, deal_value, first_response_hours]]
    probability = model.predict_proba(features)[0][1]
    return float(round(probability, 4))


def _calculate_first_response_hours(lead: Lead, first_activity_at: datetime | None) -> float:
    if not first_activity_at:
        return SENTINEL_FIRST_RESPONSE_HOURS
    created_at = lead.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if first_activity_at.tzinfo is None:
        first_activity_at = first_activity_at.replace(tzinfo=timezone.utc)
    delta_hours = (first_activity_at - created_at).total_seconds() / 3600
    return max(0.0, float(delta_hours))


def recalculate_lead_score_for_lead(db: Session, lead: Lead) -> Lead:
    activity_count = count_activities_for_lead(db, lead.id)
    first_activity = first_activity_for_lead(db, lead.id)
    first_response_hours = _calculate_first_response_hours(lead, first_activity.created_at if first_activity else None)
    primary_opp = get_primary_opportunity_for_lead(db, lead.id)
    deal_value = float(primary_opp.deal_value) if primary_opp else 0.0
    score = _score_lead(lead.source, activity_count, deal_value, first_response_hours)
    return update_lead(db, lead, score=score)


def recalculate_lead_score_for_lead_id(db: Session, lead_id: int) -> Lead | None:
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None
    return recalculate_lead_score_for_lead(db, lead)


def create_lead_service(db: Session, payload: LeadCreate):
    lead = create_lead(db, **payload.model_dump(), score=0.0)
    return recalculate_lead_score_for_lead(db, lead)


def list_leads_service(db: Session, current_user: User):
    if current_user.role == UserRole.SALES:
        return list_leads_by_assignee(db, current_user.id)
    # TODO: restrict MANAGER visibility to team-scoped leads when team model is introduced.
    return list_leads(db)


def get_lead_service(db: Session, lead_id: int, current_user: User):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    if current_user.role == UserRole.SALES and lead.assigned_to_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view this lead")
    return lead


def update_lead_service(db: Session, lead_id: int, payload: LeadUpdate, current_user: User):
    lead = get_lead_service(db, lead_id, current_user)

    updates = payload.model_dump(exclude_unset=True)
    if current_user.role == UserRole.SALES and "assigned_to_user_id" in updates:
        updates.pop("assigned_to_user_id")

    updated_lead = update_lead(db, lead, **updates)

    if any(field in updates for field in ["source", "status", "assigned_to_user_id"]):
        return recalculate_lead_score_for_lead(db, updated_lead)
    return updated_lead


def delete_lead_service(db: Session, lead_id: int):
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    delete_lead(db, lead)
