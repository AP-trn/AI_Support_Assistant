import json
import uuid
from typing import Optional
from langchain_core.tools import tool
from app.db.database import SessionLocal
from app.db.model import SupportTicket

@tool
def support_ticket_creation(customer_id: str, issue_type: str, details: str, order_id: Optional[str] = None, thread_id: Optional[str] = None) -> str:
    """Create a formal customer support escalation ticket in the SQL database for human agents to inspect."""
    db = SessionLocal()
    ticket_id = f"TICK-{uuid.uuid4().hex[:6].upper()}"
    
    new_ticket = SupportTicket(
        ticket_id=ticket_id,
        thread_id=thread_id,
        customer_id=customer_id,
        order_id=order_id,
        issue_type=issue_type,
        details=details,
        status="OPEN"
    )
    db.add(new_ticket)
    db.commit()
    db.close()
    
    return json.dumps({
        "ticket_id": ticket_id,
        "status": "OPEN",
        "customer_id": customer_id,
        "order_id": order_id,
        "issue_type": issue_type,
        "details": details,
        "message": f"Escalation ticket {ticket_id} created and assigned to the human support queue."
    })


@tool
def ticket_lookup(ticket_id: str) -> str:
    """Retrieve status, issue type, details, and order reference for an existing support ticket."""
    db = SessionLocal()
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id.strip().upper()).first()
    if not ticket:
        db.close()
        return f"Support ticket {ticket_id} not found."

    data = {
        "ticket_id": ticket.ticket_id,
        "status": ticket.status,
        "customer_id": ticket.customer_id,
        "order_id": ticket.order_id,
        "issue_type": ticket.issue_type,
        "details": ticket.details,
        "agent_notes": ticket.agent_notes,
        "created_at": str(ticket.created_at)
    }
    db.close()
    return json.dumps(data)