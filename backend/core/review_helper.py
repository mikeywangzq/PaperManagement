"""Review helper module for exam preparation."""
import logging
from typing import List, Optional, Dict, Any

from backend.models.schemas import (
    Flashcard,
    CheatSheet,
    ComparisonTable,
    Category
)
from backend.utils.llm_utils import (
    get_llm,
    FLASHCARD_PROMPT,
    CHEAT_SHEET_PROMPT,
    COMPARISON_PROMPT
)
from backend.core.document_processor import DocumentProcessor
from backend.core.classifier import Classifier

logger = logging.getLogger(__name__)


class ReviewHelper:
    """Generate study materials for exam preparation."""

    def __init__(self):
        """Initialize review helper."""
        self.llm = get_llm(temperature=0.4)
        self.doc_processor = DocumentProcessor()
        self.classifier = Classifier()

    def generate_flashcards(
        self,
        topic: str,
        doc_ids: Optional[List[str]] = None,
        category: Optional[Category] = None,
        num_cards: int = 15
    ) -> List[Flashcard]:
        """
        Generate flashcards for a topic.

        Args:
            topic: Topic name
            doc_ids: Optional list of document IDs to use
            category: Optional category to filter documents
            num_cards: Number of flashcards to generate

        Returns:
            List of flashcards
        """
        try:
            # Gather content
            content = self._gather_content(doc_ids, category, topic)

            # Generate flashcards
            prompt = FLASHCARD_PROMPT.format(topic=topic, content=content)
            response = self.llm.predict(prompt)

            # Parse flashcards
            flashcards = self._parse_flashcards(response, category, topic)

            logger.info(f"Generated {len(flashcards)} flashcards for topic: {topic}")
            return flashcards[:num_cards]

        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            raise

    def generate_cheat_sheet(
        self,
        topic: str,
        doc_ids: Optional[List[str]] = None,
        category: Optional[Category] = None
    ) -> CheatSheet:
        """
        Generate a cheat sheet for exam preparation.

        Args:
            topic: Topic name
            doc_ids: Optional list of document IDs to use
            category: Optional category to filter documents

        Returns:
            CheatSheet object
        """
        try:
            # Gather content
            content = self._gather_content(doc_ids, category, topic)

            # Generate cheat sheet
            prompt = CHEAT_SHEET_PROMPT.format(topic=topic, content=content)
            response = self.llm.predict(prompt)

            # Parse cheat sheet
            sections = self._parse_cheat_sheet(response)

            cheat_sheet = CheatSheet(
                title=f"{topic} - Quick Reference",
                category=category or Category.OTHER,
                sections=sections
            )

            logger.info(f"Generated cheat sheet for topic: {topic}")
            return cheat_sheet

        except Exception as e:
            logger.error(f"Error generating cheat sheet: {e}")
            raise

    def compare_concepts(
        self,
        concepts: List[str],
        doc_ids: Optional[List[str]] = None,
        category: Optional[Category] = None
    ) -> ComparisonTable:
        """
        Generate comparison table for multiple concepts.

        Args:
            concepts: List of concepts to compare
            doc_ids: Optional list of document IDs to use
            category: Optional category to filter documents

        Returns:
            ComparisonTable object
        """
        try:
            # Gather content
            concepts_str = ", ".join(concepts)
            content = self._gather_content(doc_ids, category, concepts_str)

            # Generate comparison
            prompt = COMPARISON_PROMPT.format(
                concepts=concepts_str,
                context=content
            )
            response = self.llm.predict(prompt)

            # Parse comparison table
            table = self._parse_comparison_table(response, concepts)

            logger.info(f"Generated comparison for concepts: {concepts}")
            return table

        except Exception as e:
            logger.error(f"Error generating comparison: {e}")
            raise

    def generate_practice_questions(
        self,
        topic: str,
        doc_ids: Optional[List[str]] = None,
        category: Optional[Category] = None,
        num_questions: int = 10
    ) -> List[Dict[str, str]]:
        """
        Generate practice questions for self-testing.

        Args:
            topic: Topic name
            doc_ids: Optional list of document IDs to use
            category: Optional category to filter documents
            num_questions: Number of questions to generate

        Returns:
            List of questions with answers
        """
        try:
            # Gather content
            content = self._gather_content(doc_ids, category, topic)

            # Generate questions
            prompt = f"""Based on the following content about {topic}, generate {num_questions} practice questions.

            Include a mix of:
            - Definition questions
            - Conceptual questions
            - Application questions

            Format each question as:
            Q: <question>
            A: <answer>
            ---

            Content:
            {content}

            Practice Questions:"""

            response = self.llm.predict(prompt)

            # Parse questions
            questions = self._parse_practice_questions(response)

            logger.info(f"Generated {len(questions)} practice questions for topic: {topic}")
            return questions[:num_questions]

        except Exception as e:
            logger.error(f"Error generating practice questions: {e}")
            raise

    def _gather_content(
        self,
        doc_ids: Optional[List[str]],
        category: Optional[Category],
        topic: str
    ) -> str:
        """Gather relevant content from documents."""
        contents = []

        if doc_ids:
            # Use specific documents
            for doc_id in doc_ids:
                text = self.doc_processor.get_document_text(doc_id)
                if text:
                    contents.append(text[:3000])  # Limit per document
        elif category:
            # Use all documents in category
            docs = self.classifier.search_by_category(category)
            for doc in docs[:5]:  # Limit to 5 documents
                text = self.doc_processor.get_document_text(doc.id)
                if text:
                    contents.append(text[:2000])
        else:
            # Search by topic
            all_docs = self.doc_processor.list_documents()
            topic_lower = topic.lower()
            for doc in all_docs:
                if (topic_lower in doc.title.lower() or
                    (doc.tags and any(topic_lower in tag.lower() for tag in doc.tags))):
                    text = self.doc_processor.get_document_text(doc.id)
                    if text:
                        contents.append(text[:2000])
                        if len(contents) >= 5:
                            break

        combined = "\n\n---\n\n".join(contents)
        return combined[:10000]  # Limit total content

    def _parse_flashcards(
        self,
        response: str,
        category: Optional[Category],
        topic: str
    ) -> List[Flashcard]:
        """Parse LLM response into flashcards."""
        flashcards = []
        current_q = None
        current_a = []

        for line in response.split('\n'):
            line = line.strip()

            if line.startswith('Q:'):
                # Save previous flashcard
                if current_q and current_a:
                    flashcards.append(Flashcard(
                        question=current_q,
                        answer=' '.join(current_a),
                        category=category or Category.OTHER,
                        tags=[topic]
                    ))

                # Start new flashcard
                current_q = line[2:].strip()
                current_a = []

            elif line.startswith('A:'):
                current_a = [line[2:].strip()]

            elif line == '---':
                # End of flashcard
                if current_q and current_a:
                    flashcards.append(Flashcard(
                        question=current_q,
                        answer=' '.join(current_a),
                        category=category or Category.OTHER,
                        tags=[topic]
                    ))
                current_q = None
                current_a = []

            elif current_a and line:
                # Continue answer
                current_a.append(line)

        # Add last flashcard
        if current_q and current_a:
            flashcards.append(Flashcard(
                question=current_q,
                answer=' '.join(current_a),
                category=category or Category.OTHER,
                tags=[topic]
            ))

        return flashcards

    def _parse_cheat_sheet(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into cheat sheet sections."""
        sections = []
        current_section = None
        current_content = []

        for line in response.split('\n'):
            line = line.strip()

            # Detect section headers
            if line and (line.startswith('#') or (line.endswith(':') and len(line) < 50)):
                # Save previous section
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content)
                    })

                # Start new section
                current_section = line.lstrip('#').rstrip(':').strip()
                current_content = []

            elif line:
                # Add to content
                current_content.append(line)

        # Add last section
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content)
            })

        return sections

    def _parse_comparison_table(
        self,
        response: str,
        concepts: List[str]
    ) -> ComparisonTable:
        """Parse LLM response into comparison table."""
        lines = [line.strip() for line in response.split('\n') if line.strip()]

        # Try to extract table structure
        dimensions = []
        data = []

        for line in lines:
            # Skip markdown table separators
            if set(line.replace('|', '').replace('-', '').strip()) == set():
                continue

            # Parse table rows
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]

                if not dimensions and cells:
                    # First row is header (dimensions)
                    dimensions = cells[1:] if cells[0].lower() in concepts[0].lower() else cells
                else:
                    # Data rows
                    data.append(cells)

        # Fallback: simple text parsing
        if not dimensions:
            dimensions = ["Description", "Use Cases", "Advantages", "Disadvantages"]
            # Create placeholder data
            data = [[concept] + ["See detailed comparison above"] * len(dimensions)
                   for concept in concepts]

        return ComparisonTable(
            concepts=concepts,
            dimensions=dimensions,
            data=data
        )

    def _parse_practice_questions(self, response: str) -> List[Dict[str, str]]:
        """Parse practice questions from LLM response."""
        questions = []
        current_q = None
        current_a = []

        for line in response.split('\n'):
            line = line.strip()

            if line.startswith('Q:'):
                # Save previous question
                if current_q and current_a:
                    questions.append({
                        "question": current_q,
                        "answer": ' '.join(current_a)
                    })

                # Start new question
                current_q = line[2:].strip()
                current_a = []

            elif line.startswith('A:'):
                current_a = [line[2:].strip()]

            elif line == '---':
                # End of question
                if current_q and current_a:
                    questions.append({
                        "question": current_q,
                        "answer": ' '.join(current_a)
                    })
                current_q = None
                current_a = []

            elif current_a and line:
                # Continue answer
                current_a.append(line)

        # Add last question
        if current_q and current_a:
            questions.append({
                "question": current_q,
                "answer": ' '.join(current_a)
            })

        return questions
