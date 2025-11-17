"""Document processing module for extracting text from various file formats."""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

import fitz  # PyMuPDF
import arxiv

from backend.models.schemas import Document, DocumentType
from backend.utils.file_utils import (
    get_file_hash,
    get_document_type,
    get_file_size,
    sanitize_filename
)
from config.settings import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and extract text from documents."""

    def __init__(self):
        """Initialize document processor."""
        self.metadata_dir = Path(settings.metadata_path)
        self.document_dir = Path(settings.document_path)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.document_dir.mkdir(parents=True, exist_ok=True)

    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text and metadata from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary containing text and metadata
        """
        try:
            doc = fitz.open(file_path)
            text_content = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text_content.append(page.get_text())

            full_text = "\n\n".join(text_content)

            # Extract metadata
            metadata = doc.metadata

            result = {
                "text": full_text,
                "num_pages": len(doc),
                "metadata": metadata,
                "title": metadata.get("title", Path(file_path).stem),
            }

            doc.close()
            return result

        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise

    def process_text_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from plain text or markdown file.

        Args:
            file_path: Path to text file

        Returns:
            Dictionary containing text and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            return {
                "text": text,
                "num_pages": None,
                "metadata": {},
                "title": Path(file_path).stem,
            }
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            raise

    def process_arxiv(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Download and process paper from arXiv.

        Args:
            arxiv_id: arXiv paper ID (e.g., "2301.12345")

        Returns:
            Dictionary containing text and metadata
        """
        try:
            # Search for the paper
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(search.results())

            # Download PDF
            filename = sanitize_filename(f"{arxiv_id}.pdf")
            file_path = self.document_dir / filename
            paper.download_pdf(str(file_path))

            # Process the downloaded PDF
            pdf_result = self.process_pdf(str(file_path))

            # Add arXiv metadata
            pdf_result["metadata"].update({
                "arxiv_id": arxiv_id,
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.isoformat(),
                "summary": paper.summary,
                "categories": paper.categories,
            })
            pdf_result["title"] = paper.title

            return {
                **pdf_result,
                "file_path": str(file_path),
            }

        except Exception as e:
            logger.error(f"Error processing arXiv paper {arxiv_id}: {e}")
            raise

    def save_document(
        self,
        file_path: str,
        document_type: Optional[DocumentType] = None,
        arxiv_id: Optional[str] = None
    ) -> Document:
        """
        Process and save a document.

        Args:
            file_path: Path to document file
            document_type: Type of document (auto-detected if None)
            arxiv_id: arXiv ID if processing arXiv paper

        Returns:
            Document object with metadata
        """
        # Process based on type
        if arxiv_id:
            result = self.process_arxiv(arxiv_id)
            file_path = result["file_path"]
            document_type = DocumentType.ARXIV
        else:
            if document_type is None:
                document_type = get_document_type(file_path)
                if document_type is None:
                    raise ValueError(f"Unsupported file type: {file_path}")

            if document_type == DocumentType.PDF:
                result = self.process_pdf(file_path)
            else:
                result = self.process_text_file(file_path)

        # Generate document ID
        file_hash = get_file_hash(file_path)
        doc_id = file_hash[:16]

        # Create document object
        document = Document(
            id=doc_id,
            title=result["title"],
            file_path=file_path,
            document_type=document_type,
            file_size=get_file_size(file_path),
            num_pages=result.get("num_pages"),
        )

        # Save metadata
        metadata_file = self.metadata_dir / f"{doc_id}.json"
        metadata = {
            **document.model_dump(mode='json'),
            "extracted_metadata": result.get("metadata", {}),
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

        # Save extracted text
        text_file = self.metadata_dir / f"{doc_id}_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(result["text"])

        logger.info(f"Saved document {doc_id}: {document.title}")
        return document

    def get_document_text(self, doc_id: str) -> Optional[str]:
        """
        Retrieve extracted text for a document.

        Args:
            doc_id: Document ID

        Returns:
            Extracted text or None if not found
        """
        text_file = self.metadata_dir / f"{doc_id}_text.txt"
        if text_file.exists():
            with open(text_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def get_document_metadata(self, doc_id: str) -> Optional[Document]:
        """
        Retrieve metadata for a document.

        Args:
            doc_id: Document ID

        Returns:
            Document object or None if not found
        """
        metadata_file = self.metadata_dir / f"{doc_id}.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Document(**data)
        return None

    def list_documents(self) -> List[Document]:
        """
        List all processed documents.

        Returns:
            List of Document objects
        """
        documents = []
        for metadata_file in self.metadata_dir.glob("*.json"):
            if not metadata_file.stem.endswith("_text"):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    documents.append(Document(**data))
        return documents

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and its metadata.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted successfully
        """
        try:
            metadata_file = self.metadata_dir / f"{doc_id}.json"
            text_file = self.metadata_dir / f"{doc_id}_text.txt"

            if metadata_file.exists():
                metadata_file.unlink()
            if text_file.exists():
                text_file.unlink()

            logger.info(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
