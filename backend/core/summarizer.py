"""Summarizer module for generating paper summaries and key points."""
import json
import logging
from typing import List, Optional

from backend.models.schemas import PaperSummary
from backend.utils.llm_utils import (
    get_llm,
    SUMMARY_PROMPT,
    KEY_POINTS_PROMPT
)
from backend.core.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class Summarizer:
    """Generate summaries and extract key points from papers."""

    def __init__(self):
        """Initialize summarizer."""
        self.llm = get_llm(temperature=0.3)  # Lower temperature for more focused output
        self.doc_processor = DocumentProcessor()

    def _truncate_text(self, text: str, max_tokens: int = 8000) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text: Input text
            max_tokens: Maximum tokens (roughly 4 chars per token)

        Returns:
            Truncated text
        """
        max_chars = max_tokens * 4
        if len(text) > max_chars:
            logger.warning(f"Text truncated from {len(text)} to {max_chars} characters")
            return text[:max_chars]
        return text

    def generate_summary(
        self,
        doc_id: str,
        language: str = "en"
    ) -> str:
        """
        Generate a concise summary of a paper.

        Args:
            doc_id: Document ID
            language: Output language (en or zh)

        Returns:
            Summary text (250-500 words)
        """
        try:
            # Get document text
            text = self.doc_processor.get_document_text(doc_id)
            if not text:
                raise ValueError(f"Document {doc_id} not found")

            # Truncate if necessary
            text = self._truncate_text(text)

            # Generate summary
            prompt = SUMMARY_PROMPT.format(text=text, language=language)
            summary = self.llm.predict(prompt)

            logger.info(f"Generated summary for document {doc_id}")
            return summary.strip()

        except Exception as e:
            logger.error(f"Error generating summary for {doc_id}: {e}")
            raise

    def extract_key_points(
        self,
        doc_id: str,
        language: str = "en"
    ) -> List[str]:
        """
        Extract key points from a paper.

        Args:
            doc_id: Document ID
            language: Output language (en or zh)

        Returns:
            List of key points
        """
        try:
            # Get document text
            text = self.doc_processor.get_document_text(doc_id)
            if not text:
                raise ValueError(f"Document {doc_id} not found")

            # Truncate if necessary
            text = self._truncate_text(text)

            # Extract key points
            prompt = KEY_POINTS_PROMPT.format(text=text, language=language)
            response = self.llm.predict(prompt)

            # Parse bullet points
            key_points = []
            for line in response.split('\n'):
                line = line.strip()
                # Remove bullet markers
                if line.startswith(('-', '*', '•', '·')):
                    line = line[1:].strip()
                elif line and line[0].isdigit() and '.' in line[:4]:
                    # Remove numbered list markers
                    line = line.split('.', 1)[1].strip()

                if line:
                    key_points.append(line)

            logger.info(f"Extracted {len(key_points)} key points for document {doc_id}")
            return key_points

        except Exception as e:
            logger.error(f"Error extracting key points for {doc_id}: {e}")
            raise

    def generate_full_analysis(
        self,
        doc_id: str,
        language: str = "en"
    ) -> PaperSummary:
        """
        Generate a comprehensive analysis of a paper.

        Args:
            doc_id: Document ID
            language: Output language (en or zh)

        Returns:
            PaperSummary object with complete analysis
        """
        try:
            # Get document metadata
            doc_metadata = self.doc_processor.get_document_metadata(doc_id)
            if not doc_metadata:
                raise ValueError(f"Document {doc_id} not found")

            # Get document text
            text = self.doc_processor.get_document_text(doc_id)
            if not text:
                raise ValueError(f"Document text for {doc_id} not found")

            # Truncate if necessary
            text = self._truncate_text(text)

            # Extract abstract (usually at the beginning)
            abstract = self._extract_abstract(text)

            # Generate summary
            summary = self.generate_summary(doc_id, language)

            # Extract key points
            key_points = self.extract_key_points(doc_id, language)

            # Extract additional details
            methodology = self._extract_methodology(text, language)
            contributions = self._extract_contributions(text, language)
            conclusions = self._extract_conclusions(text, language)
            datasets = self._extract_datasets(text)

            paper_summary = PaperSummary(
                document_id=doc_id,
                title=doc_metadata.title,
                abstract=abstract,
                summary=summary,
                key_points=key_points,
                methodology=methodology,
                contributions=contributions,
                conclusions=conclusions,
                datasets_used=datasets,
                language=language,
            )

            logger.info(f"Generated full analysis for document {doc_id}")
            return paper_summary

        except Exception as e:
            logger.error(f"Error generating full analysis for {doc_id}: {e}")
            raise

    def _extract_abstract(self, text: str) -> str:
        """Extract abstract from paper text."""
        # Simple heuristic: look for "Abstract" section
        lines = text.split('\n')
        abstract_lines = []
        in_abstract = False

        for line in lines:
            line_lower = line.lower().strip()
            if 'abstract' in line_lower and len(line_lower) < 20:
                in_abstract = True
                continue
            if in_abstract:
                if line_lower.startswith(('introduction', '1.', 'i.')):
                    break
                if line.strip():
                    abstract_lines.append(line.strip())
                if len(abstract_lines) > 20:  # Limit abstract length
                    break

        abstract = ' '.join(abstract_lines)
        return abstract if abstract else text[:500]  # Fallback to first 500 chars

    def _extract_methodology(self, text: str, language: str) -> Optional[str]:
        """Extract methodology section."""
        prompt = f"""Extract the methodology/approach section from this paper in {language}.
        Focus on HOW the research was conducted. Keep it concise (2-3 sentences).

        Paper text:
        {text[:4000]}

        Methodology:"""

        try:
            response = self.llm.predict(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error extracting methodology: {e}")
            return None

    def _extract_contributions(self, text: str, language: str) -> List[str]:
        """Extract main contributions."""
        prompt = f"""List the main contributions/innovations of this paper in {language}.
        Provide 3-5 bullet points.

        Paper text:
        {text[:4000]}

        Contributions:"""

        try:
            response = self.llm.predict(prompt)
            contributions = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith(('-', '*', '•', '·')):
                    contributions.append(line[1:].strip())
                elif line and line[0].isdigit():
                    contributions.append(line.split('.', 1)[1].strip() if '.' in line else line)
            return contributions[:5]
        except Exception as e:
            logger.error(f"Error extracting contributions: {e}")
            return []

    def _extract_conclusions(self, text: str, language: str) -> Optional[str]:
        """Extract conclusions."""
        prompt = f"""Extract the main conclusions from this paper in {language}.
        Keep it concise (2-3 sentences).

        Paper text:
        {text[-3000:]}  # Look at the end of the paper

        Conclusions:"""

        try:
            response = self.llm.predict(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error extracting conclusions: {e}")
            return None

    def _extract_datasets(self, text: str) -> List[str]:
        """Extract dataset names mentioned in the paper."""
        # Common dataset patterns
        common_datasets = [
            'ImageNet', 'CIFAR', 'MNIST', 'COCO', 'Pascal VOC',
            'WikiText', 'SQuAD', 'GLUE', 'SuperGLUE',
            'Common Crawl', 'BookCorpus', 'OpenWebText'
        ]

        datasets = []
        text_lower = text.lower()

        for dataset in common_datasets:
            if dataset.lower() in text_lower:
                datasets.append(dataset)

        return datasets
