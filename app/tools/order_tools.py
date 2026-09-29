import json
from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.db.model import Order


@tool
def order_lookup(order_id: str) -> str:
    """Retrieve order status, customer ID, order date, and purchased items from the SQL database."""
    db = SessionLocal()
    order = db.query(Order).filter(Order.order_id == order_id.strip().upper()).first()
    if not order:
        db.close()
        return f"Order {order_id} not found."
    
    data = {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "order_date": order.order_date,
        "status": order.status,
        "items": [{"sku": it.sku, "name": it.name, "price": it.price} for it in order.items]
    }
    db.close()
    return json.dumps(data)

@tool
def cancellation_eligibility(order_id: str) -> str:
    """Check SQL database if an order can be cancelled based on its fulfillment status."""
    db = SessionLocal()
    order = db.query(Order).filter(Order.order_id == order_id.strip().upper()).first()
    if not order:
        db.close()
        return f"Order {order_id} not found."
    
    status = order.status.lower()
    can_cancel = status in ["placed", "processing"]
    db.close()
    
    return json.dumps({
        "order_id": order_id,
        "eligible_for_cancellation": can_cancel,
        "current_status": order.status,
        "message": "Order is eligible for cancellation." if can_cancel else f"Cannot cancel order in status '{order.status}'. Return after delivery if required."
    })
    