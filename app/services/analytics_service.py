from sqlalchemy.orm import Session

from app.repositories.analytics_repository import (
    count_closed_won,
    count_total_leads,
    lead_source_performance,
    monthly_revenue_trend,
    pipeline_stage_distribution,
    sum_closed_won_revenue,
)


def get_kpis(db: Session) -> dict:
    total_leads = count_total_leads(db)
    closed_won = count_closed_won(db)
    conversion_rate = round((closed_won / total_leads * 100), 2) if total_leads else 0.0

    return {
        "total_leads": total_leads,
        "conversion_rate": conversion_rate,
        "total_revenue": sum_closed_won_revenue(db),
        "pipeline_stage_distribution": pipeline_stage_distribution(db),
        "lead_source_performance": lead_source_performance(db),
    }


def get_revenue_trend(db: Session) -> list[dict[str, float | str]]:
    return monthly_revenue_trend(db)
