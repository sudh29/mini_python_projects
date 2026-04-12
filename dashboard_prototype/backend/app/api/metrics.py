"""
Metrics API route — provides a JSON summary at /api/metrics for the dashboard.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser, get_current_user
from app.database import get_db
from app.services.metric_service import MetricService

router = APIRouter(tags=["metrics"])


def get_metric_service(db: Annotated[AsyncSession, Depends(get_db)]) -> MetricService:
    return MetricService(db)


@router.get("/api/metrics")
async def get_dashboard_metrics(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    service: Annotated[MetricService, Depends(get_metric_service)],
):
    """
    Returns aggregated metrics for the current tenant's dashboard.
    """
    return await service.get_dashboard_metrics(user.client_id)
