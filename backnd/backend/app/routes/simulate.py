from fastapi import APIRouter
from app.models.schemas import SimulationRequest, SimulationResult
from app.services.simulation import run_simulation

router = APIRouter()

@router.post("/disruption")
def simulate_disruption(req: SimulationRequest):
    return run_simulation(req.disruption_type, req.affected_node, req.severity, req.duration_days)

@router.get("/disruption-types")
def list_disruption_types():
    return {"types": ["port_closure", "supplier_delay", "weather", "demand_spike", "transport_failure"]}
