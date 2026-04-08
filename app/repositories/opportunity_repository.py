from sqlalchemy.orm import Session

from app.models import Lead, Opportunity


def create_opportunity(db: Session, **kwargs) -> Opportunity:
    opp = Opportunity(**kwargs)
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp


def get_opportunity_by_id(db: Session, opportunity_id: int) -> Opportunity | None:
    return db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()


def list_opportunities(db: Session) -> list[Opportunity]:
    return db.query(Opportunity).order_by(Opportunity.id.desc()).all()


def list_opportunities_by_assignee(db: Session, user_id: int) -> list[Opportunity]:
    return (
        db.query(Opportunity)
        .join(Opportunity.lead)
        .filter(Lead.assigned_to_user_id == user_id)
        .order_by(Opportunity.id.desc())
        .all()
    )


def get_primary_opportunity_for_lead(db: Session, lead_id: int) -> Opportunity | None:
    return (
        db.query(Opportunity)
        .filter(Opportunity.lead_id == lead_id)
        .order_by(Opportunity.id.asc())
        .first()
    )


def update_opportunity(db: Session, opportunity: Opportunity, **kwargs) -> Opportunity:
    for key, value in kwargs.items():
        setattr(opportunity, key, value)
    db.commit()
    db.refresh(opportunity)
    return opportunity


def delete_opportunity(db: Session, opportunity: Opportunity) -> None:
    db.delete(opportunity)
    db.commit()
