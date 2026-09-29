from app.db.database import SessionLocal
from app.db.model import ChatMessage

def get_past_order_conversations(order_id: str, current_thread_id: str, limit: int = 6) -> str:
    """Fetch previous chat messages discussing this order from other threads."""
    if not order_id:
        return ""
    
    db = SessionLocal()
    try:
        # Find messages tied to this order from PREVIOUS threads
        past_msgs = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.order_id == order_id.strip().upper(),
                ChatMessage.thread_id != current_thread_id
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )
        
        if not past_msgs:
            return ""
        
        # Order them chronologically
        past_msgs.reverse()
        formatted = []
        for m in past_msgs:
            role = "Customer" if m.role == "user" else "Agent"
            formatted.append(f"{role}: {m.content}")
        
        return "\n".join(formatted)
    finally:
        db.close()