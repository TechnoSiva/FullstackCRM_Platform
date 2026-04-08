from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityCreate(BaseModel):
    lead_id: int
    type: str
    notes: str = ""


class ActivityOut(BaseModel):
    id: int
    lead_id: int
    type: str
    notes: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
