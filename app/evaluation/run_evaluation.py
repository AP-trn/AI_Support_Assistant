import uuid
from langsmith import Client
from langsmith.evaluation import evaluate
from langchain_core.messages import HumanMessage
from app.graph.workflow import graph_app
from app.config import settings
from app.evaluation.evaluators import (
    intent_evaluator,
    tool_selection_evaluator,
    escalation_evaluator,
    hallucination_and_groundedness_evaluator
)

def target_predict(inputs: dict) -> dict:
    query = inputs["query"]
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    result = graph_app.invoke(
        {"messages": [HumanMessage(content=query)]},
        config=config
    )
    
    tools_used = [
        tc["name"] for msg in result.get("messages", [])
        if hasattr(msg, "tool_calls") and msg.tool_calls
        for tc in msg.tool_calls
    ]
    
    return {
        "response": result.get("resolution") or result["messages"][-1].content,
        "intent": result.get("intent"),
        "tools_used": tools_used,
        "escalated": bool(result.get("ticket_id"))
    }

def run_evaluation_suite():
    print(f"Executing evaluation against dataset: {settings.langsmith_dataset_name}...")
    experiment_results = evaluate(
        target_predict,
        data=settings.langsmith_dataset_name,
        evaluators=[
            intent_evaluator,
            tool_selection_evaluator,
            escalation_evaluator,
            hallucination_and_groundedness_evaluator
        ],
        experiment_prefix="Azure-LangGraph-Support-Evaluation",
    )
    print("Evaluation completed successfully. Check LangSmith for run metrics and traces.")
    print(f"Experiment Results: {experiment_results}")

if __name__ == "__main__":
    run_evaluation_suite()
    