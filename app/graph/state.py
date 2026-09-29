from typing import Annotated, List, Optional, Dict, Any
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    thread_id: Optional[str]
    customer_id: Optional[str]
    order_id: Optional[str]
    intent: Optional[str]
    issue_type: Optional[str]
    retrieved_data: Dict[str, Any]
    resolution: Optional[str]
    requires_escalation: bool
    ticket_id: Optional[str]
    approval_status: Optional[str]  