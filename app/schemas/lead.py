from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import LeadStatus


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    source: str
    status: LeadStatus = LeadStatus.NEW
    assigned_to_user_id: int | None = None


class LeadUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    source: str | None = None
    status: LeadStatus | None = None
    assigned_to_user_id: int | None = None


class LeadOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    source: str
    status: LeadStatus
    score: float
    created_at: datetime
    assigned_to_user_id: int | None

    model_config = ConfigDict(from_attributes=True)
