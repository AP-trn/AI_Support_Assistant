import json
from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.db.model import Shipment


@tool
def shipment_tracking(order_id: str) -> str:
    """Retrieve shipment status, current location, tracking number, and estimated delivery date."""
    db = SessionLocal()
    shipment = db.query(Shipment).filter(Shipment.order_id == order_id.strip().upper()).first()
    if not shipment:
        db.close()
        return f"Shipment details for order {order_id} not found."
    db.close()
    return json.dumps({
        "tracking_num": shipment.tracking_num,
        "status": shipment.status,
        "current_location": shipment.current_location,
        "estimated_delivery": shipment.estimated_delivery
    })