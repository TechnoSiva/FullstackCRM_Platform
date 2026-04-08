from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.schemas.dashboard import KPIOut, RevenueTrendPoint
from app.services.analytics_service import get_kpis, get_revenue_trend
from app.utils.deps import require_roles

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=KPIOut)
def kpis(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    return get_kpis(db)


@router.get("/revenue-trend", response_model=list[RevenueTrendPoint])
def revenue_trend(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
):
    return get_revenue_trend(db)
