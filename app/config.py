import os
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    azure_openai_api_key: str = Field(
        ..., 
        validation_alias=AliasChoices("AZURE_OPENAI_API_KEY", "OPENAI_API_KEY")
    )
    azure_openai_endpoint: str = Field(
        ..., 
        validation_alias=AliasChoices("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_BASE")
    )
    azure_openai_api_version: str = Field(
        "2024-05-01-preview", 
        validation_alias=AliasChoices("AZURE_OPENAI_API_VERSION")
    )
    azure_openai_chat_deployment: str = Field(
        "gpt-5.4", 
        validation_alias=AliasChoices("AZURE_OPENAI_CHAT_DEPLOYMENT")
    )
    azure_openai_embedding_deployment: str = Field(
        "text-embedding-3-small", 
        validation_alias=AliasChoices("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )

    
    azure_ai_search_endpoint: str = Field(
        ..., 
        validation_alias=AliasChoices("AZURE_SEARCH_ENDPOINT", "AZURE_AI_SEARCH_ENDPOINT", "AZURE_SEARCH_SERVICE_ENDPOINT")
    )
    azure_ai_search_key: str = Field(
        ..., 
        validation_alias=AliasChoices("AZURE_SEARCH_KEY", "AZURE_AI_SEARCH_KEY", "AZURE_SEARCH_ADMIN_KEY")
    )
    azure_ai_search_index_name: str = Field(
        "ecommerce-policies-index", 
        validation_alias=AliasChoices("AZURE_SEARCH_INDEX_NAME", "AZURE_AI_SEARCH_INDEX_NAME")
    )
    
    azure_document_intelligence_endpoint: str = Field(
        ..., 
        validation_alias=AliasChoices("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "DOCUMENT_INTELLIGENCE_ENDPOINT")
    )
    azure_document_intelligence_key: str = Field(
        ..., 
        validation_alias=AliasChoices("AZURE_DOCUMENT_INTELLIGENCE_KEY", "DOCUMENT_INTELLIGENCE_KEY")
    )

    # LangSmith Tracing & Evaluation
    langchain_tracing_v2: bool = Field(True, validation_alias=AliasChoices("LANGCHAIN_TRACING_V2"))
    langchain_api_key: str = Field(..., validation_alias=AliasChoices("LANGCHAIN_API_KEY"))
    langchain_endpoint: str = Field("https://api.smith.langchain.com", validation_alias=AliasChoices("LANGCHAIN_ENDPOINT"))
    langchain_project: str = Field("ecommerce-customer-support-agent", validation_alias=AliasChoices("LANGCHAIN_PROJECT"))
    langsmith_dataset_name: str = Field("ecommerce-support-eval-dataset", validation_alias=AliasChoices("LANGSMITH_DATASET_NAME"))

    # App Parameters
    chunk_size: int = 800
    chunk_overlap: int = 120
    search_k: int = 3
    policies_dir: str = "data/policies"
    orders_db_path: str = "data/orders.json"
    high_value_refund_threshold: float = 100.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def sync_to_environ(self):
        os.environ["LANGCHAIN_TRACING_V2"] = str(self.langchain_tracing_v2).lower()
        os.environ["LANGCHAIN_API_KEY"] = self.langchain_api_key
        os.environ["LANGCHAIN_ENDPOINT"] = self.langchain_endpoint
        os.environ["LANGCHAIN_PROJECT"] = self.langchain_project

settings = Settings()
settings.sync_to_environ()