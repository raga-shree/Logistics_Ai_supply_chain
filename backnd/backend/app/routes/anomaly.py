from fastapi import APIRouter
from app.models.schemas import AnomalyRequest, AnomalyResponse
from app.services.anomaly import detect_anomalies

router = APIRouter()

@router.post("/detect", response_model=AnomalyResponse)
def anomaly_detect(req: AnomalyRequest):
    return detect_anomalies(req.product_id, req.region, req.sensitivity)

@router.get("/sensitivity-guide")
def sensitivity_guide():
    return {"guide": {
        "2.0": "Standard — flags clear outliers",
        "1.5": "Sensitive — flags moderate deviations",
        "3.0": "Conservative — only extreme events",
    }}
