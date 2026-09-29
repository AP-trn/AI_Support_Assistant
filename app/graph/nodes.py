import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field
from app.graph.state import AgentState
from app.tools.agent_tools import ALL_TOOLS, support_ticket_creation
from app.agents.support_agent import get_support_llm, invoke_react_agent
from app.db.memory import get_past_order_conversations

class RequestAnalysisOutput(BaseModel):
    intent: str = Field(description="Order tracking, Delivery issues, Return requests, Refund requests, Order cancellation, Policy questions, Customer complaints, Ticket inquiry, or General")
    issue_type: str = Field(description="Sub-category or specific issue summary")
    order_id: str = Field(default=None, description="Extracted order ID like ORD-1001, if present")
    customer_id: str = Field(default=None, description="Extracted customer ID like CUST-501, if present")
    ticket_id: str = Field(default=None, description="Extracted ticket ID like TICK-XXXXXX, if present")

def request_analysis_node(state: AgentState) -> dict:
    llm = get_support_llm().with_structured_output(RequestAnalysisOutput)
    analysis_prompt = (
        "Analyze customer requests and extract entities: intent, issue_type, order_id, customer_id.\n"
        f"Messages: {[m.content for m in state['messages']]}"
    )
    result = llm.invoke([HumanMessage(content=analysis_prompt)])
    
    return {
        "intent": result.intent,
        "issue_type": result.issue_type,
        "order_id": result.order_id or state.get("order_id"),
        "customer_id": result.customer_id or state.get("customer_id"),
    }

def react_agent_node(state: AgentState) -> dict:
    order_id = state.get("order_id")
    thread_id = state.get("thread_id", "")
    

    past_history = get_past_order_conversations(order_id, thread_id) if order_id else ""

    context = {
            "intent": state.get("intent"),
            "order_id": state.get("order_id"),
            "customer_id": state.get("customer_id"),
        }

    if past_history:
        context["prior_order_notes"] = (
            f"PREVIOUS CONVERSATION HISTORY FOR ORDER {order_id}:\n{past_history}\n"
            "Use this background context naturally to maintain continuity."
        )


    response = invoke_react_agent(state["messages"], context)
    return {"messages": [response]}


def tool_execution_node(state: AgentState) -> dict:
    tool_map = {t.name: t for t in ALL_TOOLS}
    last_message = state["messages"][-1]
    tool_messages = []
    
    for tool_call in getattr(last_message, "tool_calls", []):
        target_tool = tool_map[tool_call["name"]]
        if target_tool:
            args = dict(tool_call.get("args") or {})
            if tool_call["name"] == "support_ticket_creation" and not args.get("thread_id"):
                args["thread_id"] = state.get("thread_id")
            try:
                output = target_tool.invoke(args)
            except Exception as e:
                output = json.dumps({"error": str(e)})
        tool_messages.append(
            ToolMessage(content=str(output), tool_call_id=tool_call["id"], name=tool_call["name"])
        )
    return {"messages": tool_messages}

def resolution_validation_node(state: AgentState) -> dict:
    approval_status = state.get("approval_status")

    if approval_status in ["APPROVED", "REJECTED"]:
        return {"requires_escalation": False}
    
    for m in reversed(state["messages"]):
        if isinstance(m, ToolMessage) and "requires_manager_approval" in m.content:
            try:
                data = json.loads(m.content)
                if data.get("requires_manager_approval") and approval_status != "APPROVED":
                    return {"approval_status": "PENDING"}
            except Exception:
                pass
                
    if state.get("intent") == "Customer complaints" and not state.get("ticket_id"):
        return {"requires_escalation": True}
        
    return {"requires_escalation": False}

def human_approval_node(state: AgentState) -> dict:
    return {"approval_status": "APPROVED"}

def escalation_node(state: AgentState) -> dict:
    ticket_raw = support_ticket_creation.invoke({
        "customer_id": state.get("customer_id") or "CUST-DEFAULT",
        "order_id": state.get("order_id"),
        "issue_type": state.get("issue_type") or "Customer Complaint Escalation",
        "details": f"Auto-escalated conversation. Message: {state['messages'][-1].content}",
        "thread_id": state.get("thread_id")
    })
    ticket_data = json.loads(ticket_raw)
    return {
        "ticket_id": ticket_data["ticket_id"],
        "requires_escalation": False,
        "messages": [AIMessage(content=f"Your issue has been escalated to Tier-2 human support. Reference Ticket ID: {ticket_data['ticket_id']}.")]
    }

def final_response_node(state: AgentState) -> dict:
    llm = get_support_llm()
    system_prompt = SystemMessage(
        content=(
            "You are a human-like, empathetic Customer Support Specialist for an e-commerce store.\n\n"
            "COMMUNICATION GUIDELINES:\n"
            "1. Domain Restriction: ONLY answer questions related to orders, products, shipping, cancellations, returns, refunds, and store policies. Politely decline any general trivia, external entities, or unrelated inquiries.\n"
            "2. Grounding: Base answers strictly on verified tool outputs and retrieved policy documentation. When declining out-of-scope inquiries, deliver the polite refusal directly without requiring tool data.\n"
            "3. Tone: Warm, professional, accountable, and concise. Acknowledge frustration sincerely without over-apologizing.\n"
            "4. Relevance: Address the customer's actual problem directly. Do NOT bring up policies that aren't relevant (e.g., if a parcel is missing, do not discuss cancellation rules).\n"
            "5. Resolution Commitments: Specify clear expectations (e.g., 'A support specialist will reach out within 24 business hours'). Do not claim 24/7 coverage unless confirmed by policy.\n"
            "6. Structure: 2-3 short conversational paragraphs. Use bold text sparingly for critical items like Ticket ID and Order ID."
        )
    )
    final_ans = llm.invoke([system_prompt] + state["messages"])
    return {"resolution": final_ans.content, "messages": [final_ans]}