from datetime import datetime

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models import Lead, Opportunity, OpportunityStage


def count_total_leads(db: Session) -> int:
    return db.query(Lead).count()


def count_closed_won(db: Session) -> int:
    return db.query(Opportunity).filter(Opportunity.stage == OpportunityStage.CLOSED_WON).count()


def sum_closed_won_revenue(db: Session) -> float:
    value = db.query(func.sum(Opportunity.deal_value)).filter(Opportunity.stage == OpportunityStage.CLOSED_WON).scalar()
    return float(value or 0.0)


def pipeline_stage_distribution(db: Session) -> dict[str, int]:
    rows = db.query(Opportunity.stage, func.count(Opportunity.id)).group_by(Opportunity.stage).all()
    return {stage.value: count for stage, count in rows}


def lead_source_performance(db: Session) -> list[dict[str, float | int | str]]:
    total_by_source = db.query(Lead.source, func.count(Lead.id)).group_by(Lead.source).all()
    won_by_source = (
        db.query(Lead.source, func.count(Opportunity.id))
        .join(Opportunity, Opportunity.lead_id == Lead.id)
        .filter(Opportunity.stage == OpportunityStage.CLOSED_WON)
        .group_by(Lead.source)
        .all()
    )
    won_map = {source: count for source, count in won_by_source}

    output: list[dict[str, float | int | str]] = []
    for source, total in total_by_source:
        won = won_map.get(source, 0)
        conversion = (won / total * 100) if total else 0.0
        output.append({"source": source, "count": int(total), "conversion_rate": round(conversion, 2)})
    return output


def monthly_revenue_trend(db: Session) -> list[dict[str, float | str]]:
    rows = (
        db.query(
            extract("year", Opportunity.expected_close_date).label("year"),
            extract("month", Opportunity.expected_close_date).label("month"),
            func.sum(Opportunity.deal_value).label("revenue"),
        )
        .filter(Opportunity.stage == OpportunityStage.CLOSED_WON)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    result: list[dict[str, float | str]] = []
    for row in rows:
        year = int(row.year)
        month = int(row.month)
        result.append({"month": datetime(year, month, 1).strftime("%Y-%m"), "revenue": float(row.revenue or 0.0)})
    return result
