from langsmith import Client
from app.config import settings

TEST_CASES = [
    # 1. Order Tracking (5 cases)
    {"input": "Where is my order ORD-1001?", "expected_intent": "Order tracking", "expected_tools": ["order_lookup"], "expected_escalation": False},
    {"input": "Can you check the status of order ORD-1002?", "expected_intent": "Order tracking", "expected_tools": ["order_lookup"], "expected_escalation": False},
    {"input": "Give me purchase details for ORD-1001", "expected_intent": "Order tracking", "expected_tools": ["order_lookup"], "expected_escalation": False},
    {"input": "Did my order ORD-1002 go through?", "expected_intent": "Order tracking", "expected_tools": ["order_lookup"], "expected_escalation": False},
    {"input": "What items are inside ORD-1001?", "expected_intent": "Order tracking", "expected_tools": ["order_lookup"], "expected_escalation": False},
    
    # 2. Delivery Issues (5 cases)
    {"input": "Track my shipment for ORD-1001", "expected_intent": "Delivery issues", "expected_tools": ["shipment_tracking"], "expected_escalation": False},
    {"input": "My delivery is delayed for ORD-1002. Where is it?", "expected_intent": "Delivery issues", "expected_tools": ["shipment_tracking"], "expected_escalation": False},
    {"input": "What is the courier name and tracking code for ORD-1001?", "expected_intent": "Delivery issues", "expected_tools": ["shipment_tracking"], "expected_escalation": False},
    {"input": "Estimated arrival date for package ORD-1002?", "expected_intent": "Delivery issues", "expected_tools": ["shipment_tracking"], "expected_escalation": False},
    {"input": "Has package ORD-1001 been delivered yet?", "expected_intent": "Delivery issues", "expected_tools": ["shipment_tracking"], "expected_escalation": False},

    # 3. Return Requests (5 cases)
    {"input": "I want to return an item from ORD-1001. What is the return window?", "expected_intent": "Return requests", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "Can I return open electronics per policy?", "expected_intent": "Return requests", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "How do I print a return label for my purchase?", "expected_intent": "Return requests", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "What is your holiday return window?", "expected_intent": "Return requests", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "Is international return shipping free?", "expected_intent": "Return requests", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},

    # 4. Refund Requests (5 cases)
    {"input": "Check if I can get a refund on ORD-1001", "expected_intent": "Refund requests", "expected_tools": ["refund_eligibility"], "expected_escalation": False},
    {"input": "I need a refund for my order ORD-1002 immediately", "expected_intent": "Refund requests", "expected_tools": ["refund_eligibility"], "expected_escalation": False},
    {"input": "How long does a refund take to hit my bank?", "expected_intent": "Refund requests", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "Am I eligible for a full refund for damaged ORD-1001?", "expected_intent": "Refund requests", "expected_tools": ["refund_eligibility"], "expected_escalation": False},
    {"input": "Are restocking fees deducted from refunds?", "expected_intent": "Refund requests", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},

    # 5. Policy Questions (5 cases)
    {"input": "What are your standard shipping timelines?", "expected_intent": "Policy questions", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "Do you offer customer support on weekends?", "expected_intent": "Policy questions", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "What is the order cancellation window policy?", "expected_intent": "Policy questions", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "What payment methods are supported?", "expected_intent": "Policy questions", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},
    {"input": "What is your policy on lost or stolen packages?", "expected_intent": "Policy questions", "expected_tools": ["knowledge_base_search"], "expected_escalation": False},

    # 6. Escalation Scenarios (5 cases)
    {"input": "I am furious, your service is terrible! I want a supervisor immediately!", "expected_intent": "Customer complaints", "expected_tools": ["support_ticket_creation"], "expected_escalation": True},
    {"input": "Fraudulent charge detected on my card. Escalate this immediately!", "expected_intent": "Customer complaints", "expected_tools": ["support_ticket_creation"], "expected_escalation": True},
    {"input": "Third time I am complaining about my broken package. Resolve now!", "expected_intent": "Customer complaints", "expected_tools": ["support_ticket_creation"], "expected_escalation": True},
    {"input": "Your agent lied to me yesterday. Open a formal complaint.", "expected_intent": "Customer complaints", "expected_tools": ["support_ticket_creation"], "expected_escalation": True},
    {"input": "Escalate my ticket to human support right away.", "expected_intent": "Customer complaints", "expected_tools": ["support_ticket_creation"], "expected_escalation": True}
]

def seed_evaluation_dataset():
    client = Client()
    if not client.has_dataset(dataset_name=settings.langsmith_dataset_name):
        dataset = client.create_dataset(
            dataset_name=settings.langsmith_dataset_name, 
            description="Customer Support Evaluation Suite (30 cases)"
        )
        for case in TEST_CASES:
            client.create_example(
                inputs={"query": case["input"]},
                outputs={
                    "expected_intent": case["expected_intent"],
                    "expected_tools": case["expected_tools"],
                    "expected_escalation": case["expected_escalation"]
                },
                dataset_id=dataset.id
            )
        print(f"Created and populated dataset '{settings.langsmith_dataset_name}' with 30 cases.")
    else:
        print(f"Dataset '{settings.langsmith_dataset_name}' already exists in LangSmith.")

if __name__ == "__main__":
    seed_evaluation_dataset()