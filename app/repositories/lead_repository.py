from sqlalchemy.orm import Session

from app.models import Lead


def create_lead(db: Session, **kwargs) -> Lead:
    lead = Lead(**kwargs)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead_by_id(db: Session, lead_id: int) -> Lead | None:
    return db.query(Lead).filter(Lead.id == lead_id).first()


def list_leads(db: Session) -> list[Lead]:
    return db.query(Lead).order_by(Lead.created_at.desc()).all()


def list_leads_by_assignee(db: Session, user_id: int) -> list[Lead]:
    return db.query(Lead).filter(Lead.assigned_to_user_id == user_id).order_by(Lead.created_at.desc()).all()


def update_lead(db: Session, lead: Lead, **kwargs) -> Lead:
    for key, value in kwargs.items():
        setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead: Lead) -> None:
    db.delete(lead)
    db.commit()
