from pydantic import BaseModel


class KPIOut(BaseModel):
    total_leads: int
    conversion_rate: float
    total_revenue: float
    pipeline_stage_distribution: dict[str, int]
    lead_source_performance: list[dict[str, float | int | str]]


class RevenueTrendPoint(BaseModel):
    month: str
    revenue: float
