"""Classifier module for automatic document categorization and tagging."""
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

from backend.models.schemas import ClassificationResult, Category, Document
from backend.utils.llm_utils import get_llm, CLASSIFICATION_PROMPT
from backend.core.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class Classifier:
    """Automatically classify and tag documents."""

    def __init__(self):
        """Initialize classifier."""
        self.llm = get_llm(temperature=0.2)  # Low temperature for consistent classification
        self.doc_processor = DocumentProcessor()

        # Predefined topic tags for each category
        self.category_tags = {
            Category.MACHINE_LEARNING: [
                "CNN", "RNN", "LSTM", "GRU", "Transformer", "BERT", "GPT",
                "Reinforcement Learning", "Supervised Learning", "Unsupervised Learning",
                "Deep Learning", "Neural Networks", "Computer Vision", "NLP",
                "Optimization", "Regularization", "Transfer Learning", "GANs",
                "Autoencoders", "Attention Mechanism", "Gradient Descent",
                "Backpropagation", "Feature Engineering", "Model Selection"
            ],
            Category.CRYPTOGRAPHY: [
                "AES", "DES", "3DES", "RSA", "ECC", "Diffie-Hellman",
                "SSL/TLS", "PKI", "Hash Functions", "SHA", "MD5",
                "Digital Signatures", "Public Key", "Private Key", "Symmetric Encryption",
                "Asymmetric Encryption", "Block Cipher", "Stream Cipher",
                "Key Exchange", "Certificate Authority", "Zero-Knowledge Proof",
                "Homomorphic Encryption", "Quantum Cryptography", "Blockchain"
            ]
        }

    def classify_document(self, doc_id: str) -> ClassificationResult:
        """
        Classify a document into a category and extract tags.

        Args:
            doc_id: Document ID

        Returns:
            ClassificationResult with category, tags, and confidence
        """
        try:
            # Get document text
            text = self.doc_processor.get_document_text(doc_id)
            if not text:
                raise ValueError(f"Document {doc_id} not found")

            # Use first 3000 characters for classification
            text_sample = text[:3000]

            # Generate classification using LLM
            prompt = CLASSIFICATION_PROMPT.format(text=text_sample)
            response = self.llm.predict(prompt)

            # Parse JSON response
            try:
                result = json.loads(response.strip())
                category_str = result.get("category", "other")
                tags = result.get("tags", [])
                confidence = result.get("confidence", 0.5)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response, using fallback classification")
                category_str = "other"
                tags = []
                confidence = 0.3

            # Convert category string to enum
            try:
                category = Category(category_str.lower())
            except ValueError:
                category = Category.OTHER

            # Enrich tags with keyword-based detection
            enriched_tags = self._enrich_tags(text, category, tags)

            classification = ClassificationResult(
                document_id=doc_id,
                category=category,
                tags=enriched_tags,
                confidence=confidence
            )

            # Update document metadata
            self._update_document_metadata(doc_id, classification)

            logger.info(f"Classified document {doc_id} as {category.value} with {len(enriched_tags)} tags")
            return classification

        except Exception as e:
            logger.error(f"Error classifying document {doc_id}: {e}")
            raise

    def _enrich_tags(
        self,
        text: str,
        category: Category,
        existing_tags: List[str]
    ) -> List[str]:
        """
        Enrich tags with keyword-based detection.

        Args:
            text: Document text
            category: Detected category
            existing_tags: Tags from LLM

        Returns:
            Enriched list of tags
        """
        tags = set(existing_tags)
        text_lower = text.lower()

        # Add tags based on keyword detection
        if category in self.category_tags:
            for tag in self.category_tags[category]:
                if tag.lower() in text_lower:
                    tags.add(tag)

        # Limit to top 10 most relevant tags
        return list(tags)[:10]

    def _update_document_metadata(
        self,
        doc_id: str,
        classification: ClassificationResult
    ) -> None:
        """Update document metadata with classification results."""
        try:
            metadata_file = Path(self.doc_processor.metadata_dir) / f"{doc_id}.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                # Update with classification
                metadata["category"] = classification.category.value
                metadata["tags"] = classification.tags

                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

                logger.info(f"Updated metadata for document {doc_id}")
        except Exception as e:
            logger.error(f"Error updating metadata for {doc_id}: {e}")

    def search_by_tags(self, tags: List[str]) -> List[Document]:
        """
        Search documents by tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of matching documents
        """
        try:
            all_docs = self.doc_processor.list_documents()
            matching_docs = []

            for doc in all_docs:
                # Check if document has any of the search tags
                if doc.tags and any(tag.lower() in [t.lower() for t in doc.tags] for tag in tags):
                    matching_docs.append(doc)

            logger.info(f"Found {len(matching_docs)} documents matching tags: {tags}")
            return matching_docs

        except Exception as e:
            logger.error(f"Error searching by tags: {e}")
            return []

    def search_by_category(self, category: Category) -> List[Document]:
        """
        Search documents by category.

        Args:
            category: Category to search for

        Returns:
            List of matching documents
        """
        try:
            all_docs = self.doc_processor.list_documents()
            matching_docs = [doc for doc in all_docs if doc.category == category]

            logger.info(f"Found {len(matching_docs)} documents in category {category.value}")
            return matching_docs

        except Exception as e:
            logger.error(f"Error searching by category: {e}")
            return []

    def get_tag_statistics(self) -> Dict[str, int]:
        """
        Get statistics on tag usage across all documents.

        Returns:
            Dictionary mapping tags to their frequency
        """
        try:
            all_docs = self.doc_processor.list_documents()
            tag_counts = {}

            for doc in all_docs:
                if doc.tags:
                    for tag in doc.tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Sort by frequency
            sorted_tags = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))

            return sorted_tags

        except Exception as e:
            logger.error(f"Error getting tag statistics: {e}")
            return {}

    def get_category_statistics(self) -> Dict[str, int]:
        """
        Get statistics on category distribution.

        Returns:
            Dictionary mapping categories to their frequency
        """
        try:
            all_docs = self.doc_processor.list_documents()
            category_counts = {}

            for doc in all_docs:
                if doc.category:
                    cat_name = doc.category.value
                    category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

            return category_counts

        except Exception as e:
            logger.error(f"Error getting category statistics: {e}")
            return {}

    def build_knowledge_graph_data(self) -> Dict[str, Any]:
        """
        Build data structure for knowledge graph visualization.

        Returns:
            Dictionary containing nodes and edges for graph visualization
        """
        try:
            all_docs = self.doc_processor.list_documents()

            # Nodes: categories, tags, documents
            nodes = []
            edges = []

            # Add category nodes
            for category in Category:
                nodes.append({
                    "id": f"cat_{category.value}",
                    "label": category.value.replace('_', ' ').title(),
                    "type": "category",
                    "size": 30
                })

            # Add document and tag nodes
            tag_docs = {}  # Map tags to documents
            for doc in all_docs:
                # Add document node
                nodes.append({
                    "id": f"doc_{doc.id}",
                    "label": doc.title[:30] + "..." if len(doc.title) > 30 else doc.title,
                    "type": "document",
                    "size": 15
                })

                # Link document to category
                if doc.category:
                    edges.append({
                        "source": f"doc_{doc.id}",
                        "target": f"cat_{doc.category.value}"
                    })

                # Track tags
                if doc.tags:
                    for tag in doc.tags:
                        if tag not in tag_docs:
                            tag_docs[tag] = []
                        tag_docs[tag].append(doc.id)

            # Add tag nodes (only for tags with 2+ documents)
            for tag, doc_ids in tag_docs.items():
                if len(doc_ids) >= 2:
                    nodes.append({
                        "id": f"tag_{tag}",
                        "label": tag,
                        "type": "tag",
                        "size": 20
                    })

                    # Link tag to documents
                    for doc_id in doc_ids:
                        edges.append({
                            "source": f"tag_{tag}",
                            "target": f"doc_{doc_id}"
                        })

            return {
                "nodes": nodes,
                "edges": edges
            }

        except Exception as e:
            logger.error(f"Error building knowledge graph: {e}")
            return {"nodes": [], "edges": []}
