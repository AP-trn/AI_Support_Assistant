import os
import glob
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_azure_ai.vectorstores import AzureSearch
from app.config import settings

def parse_documents_with_doc_intelligence(docs_dir: str = settings.policies_dir):
    client = None
    if settings.azure_document_intelligence_endpoint and settings.azure_document_intelligence_key:
        client = DocumentIntelligenceClient(
            endpoint=settings.azure_document_intelligence_endpoint,
            credential=AzureKeyCredential(settings.azure_document_intelligence_key)
        )
    
    parsed_documents = []

    for filepath in glob.glob(f"{docs_dir}/*.md") + glob.glob(f"{docs_dir}/*.txt"):
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip():
                parsed_documents.append(
                    Document(page_content=content, metadata={"source": filename})
                )
                
    for filepath in glob.glob(f"{docs_dir}/*.pdf"):
        if not client:
            print(f"Skipping {filepath}: Document Intelligence client not initialized.")
            continue
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            poller = client.begin_analyze_document(
                model_id="prebuilt-layout",
                body=f,
                output_content_format="markdown",
                content_type="application/octet-stream"
            )
            result = poller.result()
            parsed_documents.append(
                Document(page_content=result.content, metadata={"source": filename})
            )

    return parsed_documents

def build_azure_search_index(policy_dir: str = settings.policies_dir):
    docs = parse_documents_with_doc_intelligence(policy_dir)
    if not docs:
        print(f"No valid documents found in {policy_dir} to index.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size, 
        chunk_overlap=settings.chunk_overlap
    )
    chunked_docs = splitter.split_documents(docs)
    
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
    
    vector_store.add_documents(documents=chunked_docs)
    print(f"Successfully ingested {len(chunked_docs)} chunks into Azure AI Search index '{settings.azure_ai_search_index_name}'.")

if __name__ == "__main__":
    build_azure_search_index()