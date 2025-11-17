"""Learning path generator for creating structured study plans."""
import logging
from typing import List, Optional, Dict, Any
import json

from backend.models.schemas import (
    LearningPath,
    LearningPathNode,
    Category,
    Document
)
from backend.utils.llm_utils import get_llm, LEARNING_PATH_PROMPT
from backend.core.document_processor import DocumentProcessor
from backend.core.classifier import Classifier

logger = logging.getLogger(__name__)


class LearningPathGenerator:
    """Generate structured learning paths based on user goals."""

    def __init__(self):
        """Initialize learning path generator."""
        self.llm = get_llm(temperature=0.5)
        self.doc_processor = DocumentProcessor()
        self.classifier = Classifier()

        # Predefined learning paths for common topics
        self.template_paths = {
            "machine_learning_basics": {
                "nodes": [
                    {
                        "title": "Mathematics Foundations",
                        "description": "Linear algebra, calculus, and probability theory",
                        "prerequisites": [],
                        "estimated_time": "2-3 weeks"
                    },
                    {
                        "title": "Python Programming",
                        "description": "Python basics and scientific computing libraries (NumPy, Pandas)",
                        "prerequisites": [],
                        "estimated_time": "1-2 weeks"
                    },
                    {
                        "title": "Supervised Learning",
                        "description": "Linear regression, logistic regression, decision trees",
                        "prerequisites": ["Mathematics Foundations", "Python Programming"],
                        "estimated_time": "2 weeks"
                    },
                    {
                        "title": "Neural Networks Basics",
                        "description": "Perceptrons, activation functions, backpropagation",
                        "prerequisites": ["Supervised Learning"],
                        "estimated_time": "2 weeks"
                    },
                    {
                        "title": "Deep Learning",
                        "description": "CNNs, RNNs, optimization techniques",
                        "prerequisites": ["Neural Networks Basics"],
                        "estimated_time": "3-4 weeks"
                    }
                ]
            },
            "cryptography_basics": {
                "nodes": [
                    {
                        "title": "Number Theory Basics",
                        "description": "Modular arithmetic, prime numbers, GCD",
                        "prerequisites": [],
                        "estimated_time": "1-2 weeks"
                    },
                    {
                        "title": "Classical Cryptography",
                        "description": "Caesar cipher, substitution ciphers, historical context",
                        "prerequisites": [],
                        "estimated_time": "1 week"
                    },
                    {
                        "title": "Symmetric Encryption",
                        "description": "DES, AES, block ciphers, stream ciphers",
                        "prerequisites": ["Number Theory Basics"],
                        "estimated_time": "2 weeks"
                    },
                    {
                        "title": "Hash Functions",
                        "description": "SHA family, MD5, collision resistance",
                        "prerequisites": ["Symmetric Encryption"],
                        "estimated_time": "1 week"
                    },
                    {
                        "title": "Public Key Cryptography",
                        "description": "RSA, Diffie-Hellman, ECC",
                        "prerequisites": ["Number Theory Basics", "Hash Functions"],
                        "estimated_time": "2-3 weeks"
                    },
                    {
                        "title": "Applied Cryptography",
                        "description": "SSL/TLS, PKI, digital signatures, certificates",
                        "prerequisites": ["Public Key Cryptography"],
                        "estimated_time": "2 weeks"
                    }
                ]
            }
        }

    def generate_learning_path(
        self,
        goal: str,
        category: Optional[Category] = None,
        use_library: bool = True
    ) -> LearningPath:
        """
        Generate a learning path for a given goal.

        Args:
            goal: Learning goal description
            category: Optional category to focus on
            use_library: Whether to use user's document library

        Returns:
            LearningPath object
        """
        try:
            # Get available resources
            available_resources = []
            if use_library:
                if category:
                    docs = self.classifier.search_by_category(category)
                else:
                    docs = self.doc_processor.list_documents()

                available_resources = [
                    f"- {doc.title} (Tags: {', '.join(doc.tags) if doc.tags else 'None'})"
                    for doc in docs
                ]

            # Check if we have a template for this goal
            template_key = self._match_template(goal, category)
            if template_key:
                logger.info(f"Using template path: {template_key}")
                path = self._build_from_template(
                    template_key,
                    goal,
                    available_resources
                )
            else:
                # Generate custom path using LLM
                logger.info("Generating custom learning path")
                path = self._generate_custom_path(goal, available_resources)

            logger.info(f"Generated learning path with {len(path.nodes)} nodes")
            return path

        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            raise

    def _match_template(
        self,
        goal: str,
        category: Optional[Category]
    ) -> Optional[str]:
        """Match goal to a template path."""
        goal_lower = goal.lower()

        # Check for machine learning
        if any(kw in goal_lower for kw in ["machine learning", "ml", "deep learning", "neural network"]):
            if any(kw in goal_lower for kw in ["basic", "intro", "beginner", "start", "入门"]):
                return "machine_learning_basics"

        # Check for cryptography
        if any(kw in goal_lower for kw in ["cryptography", "crypto", "encryption", "密码"]):
            if any(kw in goal_lower for kw in ["basic", "intro", "beginner", "start", "入门"]):
                return "cryptography_basics"

        # Check by category
        if category == Category.MACHINE_LEARNING:
            return "machine_learning_basics"
        elif category == Category.CRYPTOGRAPHY:
            return "cryptography_basics"

        return None

    def _build_from_template(
        self,
        template_key: str,
        goal: str,
        available_resources: List[str]
    ) -> LearningPath:
        """Build learning path from template."""
        template = self.template_paths[template_key]

        nodes = []
        for i, node_data in enumerate(template["nodes"]):
            # Match resources to this node
            resources = self._match_resources(
                node_data["title"],
                node_data["description"],
                available_resources
            )

            node = LearningPathNode(
                id=f"node_{i}",
                title=node_data["title"],
                description=node_data["description"],
                prerequisites=node_data["prerequisites"],
                resources=resources,
                estimated_time=node_data.get("estimated_time")
            )
            nodes.append(node)

        # Calculate total time
        total_time = self._calculate_total_time([n.estimated_time for n in nodes])

        return LearningPath(
            goal=goal,
            nodes=nodes,
            total_estimated_time=total_time
        )

    def _generate_custom_path(
        self,
        goal: str,
        available_resources: List[str]
    ) -> LearningPath:
        """Generate custom learning path using LLM."""
        resources_text = "\n".join(available_resources) if available_resources else "No resources in library yet."

        prompt = LEARNING_PATH_PROMPT.format(
            goal=goal,
            available_resources=resources_text
        )

        response = self.llm.predict(prompt)

        # Parse the response into nodes
        nodes = self._parse_llm_response(response, available_resources)

        # Calculate total time
        total_time = self._calculate_total_time([n.estimated_time for n in nodes])

        return LearningPath(
            goal=goal,
            nodes=nodes,
            total_estimated_time=total_time
        )

    def _parse_llm_response(
        self,
        response: str,
        available_resources: List[str]
    ) -> List[LearningPathNode]:
        """Parse LLM response into learning path nodes."""
        nodes = []
        current_node = None
        lines = response.split('\n')

        for line in lines:
            line = line.strip()

            # Detect step headers (e.g., "1. Title" or "## Title")
            if line and (
                (line[0].isdigit() and '.' in line[:4]) or
                line.startswith('#')
            ):
                # Save previous node
                if current_node:
                    nodes.append(current_node)

                # Start new node
                title = line.split('.', 1)[1].strip() if '.' in line else line.lstrip('#').strip()
                current_node = {
                    "title": title,
                    "description": "",
                    "prerequisites": [],
                    "resources": [],
                    "estimated_time": None
                }

            elif current_node:
                # Accumulate description
                if line:
                    current_node["description"] += " " + line

        # Add last node
        if current_node:
            nodes.append(current_node)

        # Convert to LearningPathNode objects
        path_nodes = []
        for i, node_data in enumerate(nodes):
            # Extract prerequisites from previous nodes
            prerequisites = [nodes[j]["title"] for j in range(max(0, i-2), i)]

            # Match resources
            resources = self._match_resources(
                node_data["title"],
                node_data["description"],
                available_resources
            )

            node = LearningPathNode(
                id=f"node_{i}",
                title=node_data["title"],
                description=node_data["description"].strip(),
                prerequisites=prerequisites,
                resources=resources,
                estimated_time=node_data.get("estimated_time", "1-2 weeks")
            )
            path_nodes.append(node)

        return path_nodes

    def _match_resources(
        self,
        node_title: str,
        node_description: str,
        available_resources: List[str]
    ) -> List[str]:
        """Match available resources to a learning node."""
        matched = []
        search_text = (node_title + " " + node_description).lower()

        # Extract keywords from node
        keywords = set()
        for word in search_text.split():
            if len(word) > 3:  # Skip short words
                keywords.add(word.lower())

        # Match resources
        for resource in available_resources:
            resource_lower = resource.lower()
            # Check if any keyword matches
            if any(kw in resource_lower for kw in keywords):
                matched.append(resource.strip('- '))

        return matched[:5]  # Limit to top 5 matches

    def _calculate_total_time(self, time_estimates: List[Optional[str]]) -> str:
        """Calculate total estimated time from individual estimates."""
        # Simple heuristic: sum up weeks
        total_weeks = 0

        for estimate in time_estimates:
            if estimate:
                # Extract numbers from strings like "2-3 weeks"
                try:
                    parts = estimate.lower().replace('weeks', '').replace('week', '').strip()
                    if '-' in parts:
                        # Take average of range
                        low, high = parts.split('-')
                        avg = (float(low.strip()) + float(high.strip())) / 2
                        total_weeks += avg
                    else:
                        total_weeks += float(parts)
                except:
                    total_weeks += 1  # Default fallback

        if total_weeks < 1:
            return "Less than 1 week"
        elif total_weeks < 4:
            return f"{int(total_weeks)} weeks"
        else:
            months = total_weeks / 4
            return f"{months:.1f} months"

    def get_prerequisites_for_topic(self, topic: str) -> List[str]:
        """
        Get prerequisites for a specific topic.

        Args:
            topic: Topic name

        Returns:
            List of prerequisite topics
        """
        prompt = f"""What are the essential prerequisites for learning about {topic}?
        List 3-5 key prerequisite topics that someone should understand first.
        Format as a simple bullet list."""

        try:
            response = self.llm.predict(prompt)
            prerequisites = []

            for line in response.split('\n'):
                line = line.strip()
                if line.startswith(('-', '*', '•', '·')):
                    prerequisites.append(line[1:].strip())
                elif line and line[0].isdigit():
                    prerequisites.append(line.split('.', 1)[1].strip())

            return prerequisites

        except Exception as e:
            logger.error(f"Error getting prerequisites: {e}")
            return []
