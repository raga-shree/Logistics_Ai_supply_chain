"""Coordination API routes — suppliers, factories, customers."""

from fastapi import APIRouter, Query
from app.services.coordination import (
    get_network_status,
    get_node_detail,
    get_coordination_feed,
    get_network_map_data,
)

router = APIRouter()


@router.get("/network")
def network_status():
    """Full live status of all suppliers, factories, customers and order flows."""
    return get_network_status()


@router.get("/node/{node_id}")
def node_detail(node_id: str):
    """Detailed info and active order flows for a single node."""
    return get_node_detail(node_id)


@router.get("/feed")
def coordination_feed(limit: int = Query(default=20, le=50)):
    """Live coordination event feed (alerts, updates, completions)."""
    return {"events": get_coordination_feed(limit)}


@router.get("/map")
def network_map():
    """All node lat/lon + order flow edges for the coordination map."""
    return get_network_map_data()


@router.get("/suppliers")
def list_suppliers():
    from app.services.coordination import SUPPLIERS
    return {"suppliers": list(SUPPLIERS.keys())}


@router.get("/factories")
def list_factories():
    from app.services.coordination import FACTORIES
    return {"factories": list(FACTORIES.keys())}


@router.get("/customers")
def list_customers():
    from app.services.coordination import CUSTOMERS
    return {"customers": list(CUSTOMERS.keys())}
