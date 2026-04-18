from fastapi import APIRouter
from app.models.schemas import ForecastRequest, ForecastResponse
from app.services.forecasting import run_forecast

router = APIRouter()

@router.post("/", response_model=ForecastResponse)
def forecast(req: ForecastRequest):
    return run_forecast(req.product_id, req.region, req.horizon_days, req.include_safety_stock)

@router.get("/products")
def list_products():
    return {"products": ["SKU-001", "SKU-002", "SKU-003", "SKU-004", "SKU-005"]}

@router.get("/regions")
def list_regions():
    return {"regions": ["ALL", "North", "South", "East", "West", "Central"]}
