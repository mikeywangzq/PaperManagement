"""Data models and schemas for the application."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    TXT = "txt"
    MD = "md"
    ARXIV = "arxiv"


class Category(str, Enum):
    """Main categories for documents."""
    MACHINE_LEARNING = "machine_learning"
    CRYPTOGRAPHY = "cryptography"
    OTHER = "other"


class Document(BaseModel):
    """Document metadata."""
    id: str
    title: str
    file_path: str
    document_type: DocumentType
    category: Optional[Category] = None
    tags: List[str] = Field(default_factory=list)
    upload_date: datetime = Field(default_factory=datetime.now)
    file_size: int
    num_pages: Optional[int] = None
    language: str = "en"
    summary: Optional[str] = None
    key_points: List[str] = Field(default_factory=list)


class PaperSummary(BaseModel):
    """Summary of a research paper."""
    document_id: str
    title: str
    abstract: str
    summary: str
    key_points: List[str]
    methodology: Optional[str] = None
    contributions: List[str] = Field(default_factory=list)
    conclusions: Optional[str] = None
    datasets_used: List[str] = Field(default_factory=list)
    language: str = "en"


class Query(BaseModel):
    """User query for Q&A."""
    question: str
    document_ids: Optional[List[str]] = None
    category: Optional[Category] = None
    top_k: int = 5


class QueryResponse(BaseModel):
    """Response to a user query."""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: Optional[float] = None


class ClassificationResult(BaseModel):
    """Result of document classification."""
    document_id: str
    category: Category
    tags: List[str]
    confidence: float


class LearningPathNode(BaseModel):
    """A node in a learning path."""
    id: str
    title: str
    description: str
    prerequisites: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    estimated_time: Optional[str] = None


class LearningPath(BaseModel):
    """A complete learning path."""
    goal: str
    nodes: List[LearningPathNode]
    total_estimated_time: Optional[str] = None


class Flashcard(BaseModel):
    """A flashcard for study."""
    question: str
    answer: str
    category: Category
    tags: List[str] = Field(default_factory=list)


class CheatSheet(BaseModel):
    """A cheat sheet for quick review."""
    title: str
    category: Category
    sections: List[Dict[str, Any]]


class ComparisonTable(BaseModel):
    """Comparison between concepts."""
    concepts: List[str]
    dimensions: List[str]
    data: List[List[str]]
