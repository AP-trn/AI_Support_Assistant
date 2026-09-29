from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage
from app.config import settings
from app.tools.agent_tools import ALL_TOOLS

def get_support_llm():
    return AzureChatOpenAI(
        azure_deployment=settings.azure_openai_chat_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        temperature=0.0,
        request_timeout=60,
        max_retries=2
    )


def invoke_react_agent(messages: list, context_info: dict):
    llm = get_support_llm().bind_tools(ALL_TOOLS)
    prior_notes = context_info.get("prior_order_notes", "")

    system_prompt_text = (
            "You are an intelligent customer support agent for an e-commerce platform. \n\n "
            "STRICT DOMAIN BOUNDARY:\n"
            "- You ONLY assist with store-related matters: order tracking, deliveries, cancellations, returns, refunds, store policies, and customer complaints.\n"
            "- If the user asks about general knowledge, celebrities, politics, coding, personal advice, or anything unrelated to this store (e.g., 'Who is Elon Musk?'), politely refuse and steer them back to customer support.\n"
            "- Example refusal: 'I am here to assist with your orders, shipments, returns, and store policies. I am unable to answer general knowledge or trivia questions. How can I assist you with your purchase today?'\n\n"
            "OPERATING GUIDELINES:\n"
            "Dynamically select and invoke tools to resolve user issues. "
            "Do not expose internal Chain of Thought. Keep responses grounded in tool results.\n"
            f"Context: Intent={context_info.get('intent')}, OrderID={context_info.get('order_id')}, "
            f"CustomerID={context_info.get('customer_id')}."
    )

    if prior_notes:
        system_prompt_text += f"\n{prior_notes}\n"
    system_msg = SystemMessage(content=system_prompt_text)
    return llm.invoke([system_msg] + messages)