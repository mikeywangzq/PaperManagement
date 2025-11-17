"""Application settings and configuration."""
import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # OpenAI Configuration
    openai_api_key: str = ""
    openai_api_base: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"

    # Paths
    vector_db_path: str = "./data/vectorstore"
    document_path: str = "./data/documents"
    metadata_path: str = "./data/metadata"

    # Application Settings
    max_file_size_mb: int = 50
    supported_languages: List[str] = ["en", "zh"]

    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    # LLM Settings
    temperature: float = 0.7
    max_tokens: int = 2000

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    def ensure_directories(self):
        """Ensure all required directories exist."""
        paths = [
            self.vector_db_path,
            self.document_path,
            self.metadata_path,
        ]
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
