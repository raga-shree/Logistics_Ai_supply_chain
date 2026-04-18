from fastapi import APIRouter
from app.models.schemas import KPIResponse
from app.services.kpi import get_kpis

router = APIRouter()

@router.get("", response_model=KPIResponse)
def kpis():
    return get_kpis()
