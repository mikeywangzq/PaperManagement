"""File handling utilities."""
import hashlib
import os
from pathlib import Path
from typing import Optional

from backend.models.schemas import DocumentType


def get_file_hash(file_path: str) -> str:
    """Generate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_document_type(file_path: str) -> Optional[DocumentType]:
    """Determine document type from file extension."""
    extension = Path(file_path).suffix.lower()
    type_mapping = {
        ".pdf": DocumentType.PDF,
        ".txt": DocumentType.TXT,
        ".md": DocumentType.MD,
        ".docx": DocumentType.DOCX,
        ".pptx": DocumentType.PPTX,
        ".epub": DocumentType.EPUB,
    }
    return type_mapping.get(extension)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove problematic characters."""
    # Remove or replace problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(file_path)


def ensure_directory(directory: str) -> None:
    """Ensure directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)
