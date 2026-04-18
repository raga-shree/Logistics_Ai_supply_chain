from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class DisruptionType(str, Enum):
    PORT_CLOSURE      = "port_closure"
    SUPPLIER_DELAY    = "supplier_delay"
    WEATHER           = "weather"
    DEMAND_SPIKE      = "demand_spike"
    TRANSPORT_FAILURE = "transport_failure"


class TransportMode(str, Enum):
    AIR  = "air"
    SEA  = "sea"
    ROAD = "road"
    RAIL = "rail"


# ── Forecast ─────────────────────────────────────────────────────────────────
class ForecastRequest(BaseModel):
    product_id:           str
    region:               Optional[str] = "ALL"
    horizon_days:         int = 30
    include_safety_stock: bool = True


class ForecastPoint(BaseModel):
    date:             str
    predicted_demand: float
    lower_bound:      float
    upper_bound:      float


class ForecastResponse(BaseModel):
    product_id:         str
    region:             str
    forecast:           List[ForecastPoint]
    safety_stock:       Optional[float]
    reorder_point:      Optional[float]
    model_mae:          Optional[float] = None
    baseline_mae:       Optional[float] = None
    model_fill_rate:    Optional[float] = None
    baseline_fill_rate: Optional[float] = None


# ── Optimize ─────────────────────────────────────────────────────────────────
class RouteRequest(BaseModel):
    origin:          str
    destination:     str
    cargo_weight_kg: float
    priority:        str = "balanced"
    carrier_cap:     Optional[int] = None


class RouteOption(BaseModel):
    mode:            str
    carrier:         str
    cost_usd:        float
    lead_time_days:  float
    co2_kg:          float
    score:           float
    lp_fraction:     Optional[float] = None
    mip_selected:    Optional[bool]  = None


class OptimizeResponse(BaseModel):
    recommended:          RouteOption
    alternatives:         List[RouteOption]
    optimization_method:  Optional[str] = None
    network_flow_cost:    Optional[float] = None
    network_flow_co2:     Optional[float] = None


# ── Simulate ─────────────────────────────────────────────────────────────────
class SimulationRequest(BaseModel):
    disruption_type: DisruptionType
    affected_node:   str
    severity:        float
    duration_days:   int


class SimulationResult(BaseModel):
    disruption_type:           str
    affected_node:             str
    estimated_cost_impact_usd: float
    estimated_delay_days:      float
    service_level_drop:        float
    recommended_playbook:      List[str]
    risk_score:                float


# ── KPI ──────────────────────────────────────────────────────────────────────
class KPIResponse(BaseModel):
    service_level_pct:    float
    avg_lead_time_days:   float
    total_cost_usd:       float
    co2_emissions_kg:     float
    inventory_turnover:   float
    on_time_delivery_pct: float
    stockout_rate_pct:    float
    fill_rate_pct:        float


# ── Anomaly ──────────────────────────────────────────────────────────────────
class AnomalyRequest(BaseModel):
    product_id:  str
    region:      Optional[str] = "ALL"
    sensitivity: float = 2.0


class AnomalyPoint(BaseModel):
    date:        str
    demand:      float
    z_score:     float
    severity:    str
    explanation: str
    disruption:  Optional[str] = None


class AnomalyResponse(BaseModel):
    product_id:    str
    region:        str
    anomalies:     List[AnomalyPoint]
    baseline_mean: float
    baseline_std:  float
