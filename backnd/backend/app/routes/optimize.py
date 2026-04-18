from fastapi import APIRouter
from app.models.schemas import RouteRequest, OptimizeResponse
from app.services.optimization import run_optimization

router = APIRouter()

@router.post("/route", response_model=OptimizeResponse)
def optimize_route(req: RouteRequest):
    return run_optimization(req.origin, req.destination, req.cargo_weight_kg,
                            req.priority, req.carrier_cap)

@router.get("/nodes")
def list_nodes():
    return {"nodes": ["WH-A", "WH-B", "PLT-1", "PLT-2", "CUST"]}

@router.get("/methods")
def list_methods():
    return {"methods": ["Linear Programming", "Mixed Integer Programming", "Network Flow"]}
