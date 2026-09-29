import json
import uuid
from langchain_core.messages import HumanMessage
from app.tools.order_tools import order_lookup, cancellation_eligibility
from app.tools.refund_tools import refund_eligibility
from app.graph.workflow import graph_app

def test_order_lookup_valid():
    res = order_lookup.invoke({"order_id": "ORD-1001"})
    data = json.loads(res)
    assert data["order_id"] == "ORD-1001"
    assert data["status"] == "Delivered"

    missing = order_lookup.invoke({"order_id": "NON-EXISTENT"})
    assert "not found" in missing.lower()

def test_refund_threshold_logic():
    low_val_res = refund_eligibility.invoke({"order_id": "ORD-1001", "reason": "Return item"})
    low_data = json.loads(low_val_res)
    assert low_data["requires_manager_approval"] is False

    high_val_res = refund_eligibility.invoke({"order_id": "ORD-1002", "reason": "Damaged screen"})
    high_data = json.loads(high_val_res)
    assert high_data["requires_manager_approval"] is True

def test_cancellation_eligibility():
    delivered_res = cancellation_eligibility.invoke({"order_id": "ORD-1001"})
    deliv_data = json.loads(delivered_res)
    assert deliv_data["eligible_for_cancellation"] is False

    processing_res = cancellation_eligibility.invoke({"order_id": "ORD-1002"})
    proc_data = json.loads(processing_res)
    assert proc_data["eligible_for_cancellation"] is True

def test_graph_routing_flow():
    thread_id = f"test-thread-{uuid.uuid4().hex[:6]}"
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "messages": [HumanMessage(content="Where is my order ORD-1001?")],
        "approval_status": None,
        "requires_escalation": False,
        "retrieved_data": {}
    }
    
    result = graph_app.invoke(initial_state, config=config)
    assert result["intent"] is not None
    assert len(result["messages"]) > 1