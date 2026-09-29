from langsmith.schemas import Example, Run
from app.agents.support_agent import get_support_llm

def intent_evaluator(run: Run, example: Example) -> dict:
    predicted_intent = run.outputs.get("intent", "").strip().lower()
    expected_intent = example.outputs.get("expected_intent", "").strip().lower()
    score = 1.0 if expected_intent in predicted_intent or predicted_intent in expected_intent else 0.0
    return {"key": "intent_accuracy", "score": score}

def tool_selection_evaluator(run: Run, example: Example) -> dict:
    actual_tools = set(run.outputs.get("tools_used", []))
    expected_tools = set(example.outputs.get("expected_tools", []))
    score = 1.0 if expected_tools.issubset(actual_tools) else 0.0
    return {"key": "tool_selection_accuracy", "score": score}

def escalation_evaluator(run: Run, example: Example) -> dict:
    actual_esc = bool(run.outputs.get("escalated", False))
    expected_esc = bool(example.outputs.get("expected_escalation", False))
    return {"key": "escalation_accuracy", "score": 1.0 if actual_esc == expected_esc else 0.0}

def hallucination_and_groundedness_evaluator(run: Run, example: Example) -> dict:
    llm = get_support_llm()
    query = run.inputs.get("query")
    response = run.outputs.get("response")
    prompt = (
        f"User Query: {query}\n"
        f"Agent Response: {response}\n\n"
        "Evaluate if the response contains hallucinations or unsupported factual claims. "
        "Answer strictly with SCORE: 1.0 (Grounded, factual) or SCORE: 0.0 (Contains hallucination)."
    )
    verdict = llm.invoke(prompt).content
    score = 1.0 if "SCORE: 1.0" in verdict else 0.0
    return {"key": "groundedness_score", "score": score}
