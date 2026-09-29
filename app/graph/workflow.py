import os
import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.graph.nodes import (
    request_analysis_node,
    react_agent_node,
    tool_execution_node,
    resolution_validation_node,
    human_approval_node,
    escalation_node,
    final_response_node,
)
from app.graph.state import AgentState

def _route_react(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_execution"
    return "resolution_validation"

def _route_after_validation(state: AgentState) -> str:
    if state.get("approval_status") == "PENDING":
        return "human_approval"
    if state.get("requires_escalation")and not state.get("ticket_id"):
        return "escalation"
    return "final_response"

workflow = StateGraph(AgentState)

workflow.add_node("request_analysis", request_analysis_node)
workflow.add_node("react_agent", react_agent_node)
workflow.add_node("tool_execution", tool_execution_node)
workflow.add_node("resolution_validation", resolution_validation_node)
workflow.add_node("human_approval", human_approval_node)
workflow.add_node("escalation", escalation_node)
workflow.add_node("final_response", final_response_node)

workflow.add_edge(START, "request_analysis")
workflow.add_edge("request_analysis", "react_agent")

workflow.add_conditional_edges(
    "react_agent",
    _route_react,
    {
        "tool_execution": "tool_execution",
        "resolution_validation": "resolution_validation"
    }
)
workflow.add_edge("tool_execution", "react_agent")

workflow.add_conditional_edges(
    "resolution_validation",
    _route_after_validation,
    {
        "human_approval": "human_approval",
        "escalation": "escalation",
        "final_response": "final_response",
    }
)

workflow.add_edge("human_approval", "final_response")
workflow.add_edge("escalation", "final_response")
workflow.add_edge("final_response", END)

os.makedirs("data", exist_ok=True)
connection = sqlite3.connect("data/chat_checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(connection)
graph_app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_approval"]
)
