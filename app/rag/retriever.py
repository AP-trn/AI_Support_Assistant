from langchain_azure_ai.vectorstores import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from app.config import settings

def get_azure_retriever():
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=settings.azure_openai_embedding_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version
    )
    
    vector_store = AzureSearch(
        azure_search_endpoint=settings.azure_ai_search_endpoint,
        azure_search_key=settings.azure_ai_search_key,
        index_name=settings.azure_ai_search_index_name,
        embedding_function=embeddings.embed_query
    )
    
    return vector_store.as_retriever(k=settings.search_k)