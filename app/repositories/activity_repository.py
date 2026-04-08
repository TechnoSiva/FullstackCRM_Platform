from sqlalchemy.orm import Session

from app.models import Activity


def create_activity(db: Session, **kwargs) -> Activity:
    activity = Activity(**kwargs)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def list_activities_for_lead(db: Session, lead_id: int) -> list[Activity]:
    return db.query(Activity).filter(Activity.lead_id == lead_id).order_by(Activity.created_at.desc()).all()


def count_activities_for_lead(db: Session, lead_id: int) -> int:
    return db.query(Activity).filter(Activity.lead_id == lead_id).count()


def first_activity_for_lead(db: Session, lead_id: int) -> Activity | None:
    return db.query(Activity).filter(Activity.lead_id == lead_id).order_by(Activity.created_at.asc()).first()
