from langchain_core.tools import tool
from app.rag.retriever import get_azure_retriever

@tool
def knowledge_base_search(query: str) -> str:
    """Retrieve relevant company policy info (Returns, Refunds, Shipping, Cancellations, Support)."""
    retriever = get_azure_retriever()
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant policy documents found."
    return "\n\n".join([f"[Source: {d.metadata.get('source', 'Unknown')}]: {d.page_content}" for d in docs])
    