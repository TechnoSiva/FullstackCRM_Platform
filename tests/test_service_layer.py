from datetime import date

import pytest
from fastapi import HTTPException

from app.models import OpportunityStage, UserRole
from app.repositories.lead_repository import create_lead
from app.repositories.opportunity_repository import create_opportunity
from app.repositories.user_repository import create_user
from app.services.analytics_service import get_kpis
from app.services.lead_service import create_lead_service, update_lead_service
from app.services.opportunity_service import create_opportunity_service
from app.schemas.lead import LeadCreate, LeadUpdate
from app.schemas.opportunity import OpportunityCreate


class MockModel:
    def __init__(self, probability: float = 0.82):
        self.probability = probability

    def predict_proba(self, rows):
        return [[1 - self.probability, self.probability] for _ in rows]


def test_lead_scoring_integration_uses_loaded_model(db_session, monkeypatch):
    monkeypatch.setattr("app.services.lead_service.load_model", lambda: MockModel(probability=0.91))

    lead = create_lead_service(
        db_session,
        LeadCreate(name="Score Lead", email="score@example.com", source="website", assigned_to_user_id=None),
    )

    assert lead.score == pytest.approx(0.91)


def test_sales_cannot_update_unassigned_lead(db_session):
    manager = create_user(
        db_session,
        name="Manager",
        email="manager@test.com",
        password="hashed",
        role=UserRole.MANAGER,
    )
    sales = create_user(
        db_session,
        name="Sales",
        email="sales@test.com",
        password="hashed",
        role=UserRole.SALES,
    )

    lead = create_lead(
        db_session,
        name="Protected Lead",
        email="lead@test.com",
        source="website",
        status="NEW",
        assigned_to_user_id=manager.id,
        score=0.2,
    )

    with pytest.raises(HTTPException) as exc:
        update_lead_service(db_session, lead.id, LeadUpdate(status="CONTACTED"), sales)

    assert exc.value.status_code == 403


def test_analytics_service_returns_expected_values(db_session):
    admin = create_user(
        db_session,
        name="Admin",
        email="admin@test.com",
        password="hashed",
        role=UserRole.ADMIN,
    )
    lead = create_lead(
        db_session,
        name="Lead A",
        email="a@test.com",
        source="referral",
        status="NEW",
        assigned_to_user_id=admin.id,
        score=0.5,
    )
    create_opportunity(
        db_session,
        lead_id=lead.id,
        deal_value=25000,
        stage=OpportunityStage.CLOSED_WON,
        probability=0.9,
        expected_close_date=date(2026, 2, 1),
    )

    kpis = get_kpis(db_session)

    assert kpis["total_leads"] == 1
    assert kpis["conversion_rate"] == 100.0
    assert kpis["total_revenue"] == 25000.0
    assert kpis["pipeline_stage_distribution"]["CLOSED_WON"] == 1


def test_sales_can_create_opportunity_for_assigned_lead(db_session):
    sales = create_user(
        db_session,
        name="Sales Person",
        email="sales2@test.com",
        password="hashed",
        role=UserRole.SALES,
    )
    lead = create_lead(
        db_session,
        name="Assigned Lead",
        email="assigned@test.com",
        source="event",
        status="NEW",
        assigned_to_user_id=sales.id,
        score=0.1,
    )

    opportunity = create_opportunity_service(
        db_session,
        OpportunityCreate(
            lead_id=lead.id,
            deal_value=10000,
            stage=OpportunityStage.PROSPECTING,
            probability=0.2,
            expected_close_date=date(2026, 3, 1),
        ),
        sales,
    )

    assert opportunity.id is not None
    assert opportunity.lead_id == lead.id
