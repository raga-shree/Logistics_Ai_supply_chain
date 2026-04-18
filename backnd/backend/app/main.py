from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import forecast, optimize, simulate, kpi, anomaly
from backend.app.routes import coordination

app = FastAPI(
    title="CognixOps Logistics AI API",
    description=(
        "AI-Enhanced Logistics: Prophet+XGBoost Forecasting · "
        "LP+MIP+Network Flow Optimization · Disruption Simulation · "
        "Multi-tier Coordination · AI Chatbot"
    ),
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forecast.router,      prefix="/forecast",      tags=["Forecasting"])
app.include_router(optimize.router,      prefix="/optimize",      tags=["Optimization"])
app.include_router(simulate.router,      prefix="/simulate",      tags=["Simulation"])
app.include_router(kpi.router,           prefix="/kpi",           tags=["KPIs"])
app.include_router(anomaly.router,       prefix="/anomaly",       tags=["Anomaly Detection"])
app.include_router(coordination.router,  prefix="/coordination",  tags=["Coordination"])   # NEW

@app.get("/")
def root():
    return {
        "message": "CognixOps Logistics AI API v3.0",
        "methods": ["Prophet+XGBoost Forecasting", "LP+MIP+Network Flow Optimization"],
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}
