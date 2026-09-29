import json
from langchain_core.tools import tool
from app.config import settings
from app.db.database import SessionLocal
from app.db.model import Order

@tool
def refund_eligibility(order_id: str, reason: str) -> str:
    """Check whether an order is eligible for a full or partial refund based on business rules."""
    db = SessionLocal()
    order = db.query(Order).filter(Order.order_id == order_id.strip().upper()).first()
    if not order:
        db.close()
        return f"Cannot evaluate refund: Order {order_id} not found."
    total_amount = sum(item.price for item in order.items)
    requires_approval = total_amount > settings.high_value_refund_threshold
    db.close()
    return json.dumps({
        "order_id": order_id,
        "total_amount": round(total_amount, 2),
        "requires_manager_approval": requires_approval,
        "threshold": settings.high_value_refund_threshold
    })
    