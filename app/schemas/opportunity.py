from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models import OpportunityStage


class OpportunityCreate(BaseModel):
    lead_id: int
    deal_value: float
    stage: OpportunityStage = OpportunityStage.PROSPECTING
    probability: float = 0.1
    expected_close_date: date | None = None


class OpportunityUpdate(BaseModel):
    deal_value: float | None = None
    stage: OpportunityStage | None = None
    probability: float | None = None
    expected_close_date: date | None = None


class OpportunityOut(BaseModel):
    id: int
    lead_id: int
    deal_value: float
    stage: OpportunityStage
    probability: float
    expected_close_date: date | None

    model_config = ConfigDict(from_attributes=True)
