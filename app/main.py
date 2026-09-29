import json
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage, ToolMessage
from app.graph.workflow import graph_app
from app.db.database import SessionLocal
from app.db.model import SupportTicket
from app.db.model import ChatMessage, SupportTicket

app = FastAPI(title="Azure LangGraph Customer Support Service")

class ChatRequest(BaseModel):
    thread_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    tools_used: List[str] = []
    escalated: bool = False
    ticket_id: Optional[str] = None
    pending_approval: bool = False

class ApproveRequest(BaseModel):
    thread_id: str
    approved: bool

class ApproveResponse(BaseModel):
    thread_id: str
    status: str
    final_response: str

class TicketResolveRequest(BaseModel):
    ticket_id: str
    agent_notes: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    
    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "thread_id": req.thread_id,
        "approval_status": None,
        "requires_escalation": False,
        "retrieved_data": {}
    }
    
    result = graph_app.invoke(initial_state, config=config)

    identified_order_id = result.get("order_id")


    if result.get("approval_status") == "PENDING":
        response_text = "Refund exceeds $100 and is awaiting manager sign-off."
    elif result.get("resolution"):
        response_text = result["resolution"]
    else:
        response_text = result["messages"][-1].content


    db = SessionLocal()
    try:
        user_msg = ChatMessage(
            id=uuid.uuid4().hex,
            thread_id=req.thread_id,
            order_id=identified_order_id,
            role="user",
            content=req.message
        )
        assistant_msg = ChatMessage(
            id=uuid.uuid4().hex,
            thread_id=req.thread_id,
            order_id=identified_order_id,
            role="assistant",
            content=response_text
        )
        db.add_all([user_msg, assistant_msg])
        db.commit()
    finally:
        db.close()
        
    tools_used = [
        tc["name"] for msg in result.get("messages", [])
        if hasattr(msg, "tool_calls") and msg.tool_calls
        for tc in msg.tool_calls
    ]

    extracted_ticket_id = result.get("ticket_id")
    if not extracted_ticket_id:
        for msg in reversed(result.get("messages", [])):
            if isinstance(msg, ToolMessage) and msg.name == "support_ticket_creation":
                try:
                    payload = json.loads(msg.content)
                    extracted_ticket_id = payload.get("ticket_id")
                    break
                except Exception:
                    pass
    
    is_pending = result.get("approval_status") == "PENDING"
    is_escalated = bool(extracted_ticket_id or result.get("requires_escalation"))

    response_text = result.get("resolution") or (
        "Refund exceeds $100 and is awaiting manager sign-off." if is_pending else result["messages"][-1].content
    )
    return ChatResponse(
        response=response_text,
        intent=result.get("intent"),
        tools_used=tools_used,
        escalated=is_escalated,
        ticket_id=extracted_ticket_id,
        pending_approval=is_pending
    )

@app.post("/approve", response_model=ApproveResponse)
async def approve_endpoint(req: ApproveRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    state = graph_app.get_state(config)
    if not state.next:
        raise HTTPException(status_code=400, detail="No pending human approval found for this thread.")
    
    decision = "APPROVED" if req.approved else "REJECTED"
    graph_app.update_state(config, {"approval_status": decision}, as_node="resolution_validation")
    resumed = graph_app.invoke(None, config=config)
    
    final_text = resumed.get("resolution") or resumed["messages"][-1].content
    return ApproveResponse(thread_id=req.thread_id, status=decision, final_response=final_text)

@app.get("/tickets")
def list_tickets():
    """List open tickets for human agents to inspect."""
    db = SessionLocal()
    tickets = db.query(SupportTicket).filter(SupportTicket.status == "OPEN").all()
    out = [
        {
            "ticket_id": t.ticket_id,
            "thread_id": t.thread_id,
            "customer_id": t.customer_id,
            "order_id": t.order_id,
            "issue_type": t.issue_type,
            "details": t.details,
            "created_at": str(t.created_at)
        } for t in tickets
    ]
    db.close()
    return out

@app.post("/tickets/resolve")
def resolve_ticket(req: TicketResolveRequest):
    """Human agent inspects and closes a ticket."""
    db = SessionLocal()
    ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id == req.ticket_id).first()
    if not ticket:
        db.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = "RESOLVED"
    ticket.agent_notes = req.agent_notes
    db.commit()
    db.close()
    return {"message": f"Ticket {req.ticket_id} marked as RESOLVED."}