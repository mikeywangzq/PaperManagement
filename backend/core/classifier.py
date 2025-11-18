"""
文档分类模块 - 自动分类和标记文档

Classifier module for automatic document categorization and tagging.

核心功能 (Core Features):
1. 自动分类: 将文档分类为机器学习、密码学或其他
2. 标签提取: 从文档中识别相关技术标签
3. 混合策略: 结合LLM智能分析和关键词匹配
4. 统计分析: 提供分类和标签的统计信息

分类策略 (Classification Strategy):
- LLM分析: 理解语义，识别主题
- 关键词匹配: 补充LLM遗漏的专业术语
- 置信度评分: 评估分类的可信度
"""
import json
import logging
from typing import List, Dict, Any
from pathlib import Path

from backend.models.schemas import ClassificationResult, Category, Document
from backend.utils.llm_utils import get_llm, CLASSIFICATION_PROMPT
from backend.core.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class Classifier:
    """
    文档分类器 - 自动分类和标记文档

    Automatically classify and tag documents.

    工作原理 (How It Works):
    1. LLM初步分析: 基于文档内容理解主题
    2. 标签提取: LLM提取相关技术术语
    3. 标签增强: 使用预定义词典补充遗漏的标签
    4. 元数据更新: 将分类结果写入文档元数据
    """

    def __init__(self):
        """
        初始化分类器

        Initialize classifier.

        配置说明 (Configuration):
        - temperature=0.2: 极低温度确保分类一致性
          (分类任务需要稳定输出，不需要创造性)
        - 预定义标签库: 为每个类别维护专业术语词典
        """
        self.llm = get_llm(temperature=0.2)  # 极低温度确保分类一致
        self.doc_processor = DocumentProcessor()

        # 为每个类别预定义主题标签词典
        # 用于标签增强，补充LLM可能遗漏的专业术语
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
        对文档进行分类并提取标签

        Classify a document into a category and extract tags.

        完整分类流程 (Complete Classification Flow):
        1. 文本采样: 取前3000字符(足够识别主题，避免超限)
        2. LLM分类: 调用LLM进行语义分析
        3. JSON解析: 提取类别、标签、置信度
        4. 标签增强: 使用关键词匹配补充标签
        5. 元数据更新: 将结果写入文档元数据

        为什么只用前3000字符 (Why First 3000 Characters):
        - 论文的摘要和引言通常包含足够的主题信息
        - 减少Token消耗，降低API成本
        - 加快处理速度

        容错处理 (Error Handling):
        - JSON解析失败: 降级为"other"类别，置信度0.3
        - 类别识别失败: 使用OTHER作为默认类别
        - 完全失败: 抛出异常，由调用者处理

        Args:
            doc_id: 文档ID (Document ID)

        Returns:
            ClassificationResult对象，包含类别、标签、置信度
        """
        try:
            # 获取文档文本
            text = self.doc_processor.get_document_text(doc_id)
            if not text:
                raise ValueError(f"Document {doc_id} not found")

            # 使用前3000字符进行分类(通常足够且节省成本)
            text_sample = text[:3000]

            # 使用LLM生成分类
            prompt = CLASSIFICATION_PROMPT.format(text=text_sample)
            response = self.llm.predict(prompt)

            # 解析JSON响应
            try:
                result = json.loads(response.strip())
                category_str = result.get("category", "other")
                tags = result.get("tags", [])
                confidence = result.get("confidence", 0.5)
            except json.JSONDecodeError:
                # JSON解析失败时的降级处理
                logger.warning(f"Failed to parse JSON response, using fallback classification")
                category_str = "other"
                tags = []
                confidence = 0.3

            # 将类别字符串转换为枚举
            try:
                category = Category(category_str.lower())
            except ValueError:
                category = Category.OTHER

            # 使用关键词匹配增强标签
            enriched_tags = self._enrich_tags(text, category, tags)

            # 构建分类结果
            classification = ClassificationResult(
                document_id=doc_id,
                category=category,
                tags=enriched_tags,
                confidence=confidence
            )

            # 更新文档元数据
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
        使用关键词匹配增强标签

        Enrich tags with keyword-based detection.

        增强策略 (Enrichment Strategy):
        1. 保留LLM提取的标签(语义理解)
        2. 遍历预定义标签库
        3. 简单字符串匹配检测是否出现
        4. 合并去重，限制数量

        为什么需要增强 (Why Enrichment):
        - LLM可能遗漏明显的专业术语
        - 确保关键技术标签被捕获
        - 提高标签的完整性

        Args:
            text: 文档文本 (Document text)
            category: 检测到的类别 (Detected category)
            existing_tags: LLM提取的标签 (Tags from LLM)

        Returns:
            增强后的标签列表(最多10个) (Enriched list of tags)
        """
        tags = set(existing_tags)  # 使用集合自动去重
        text_lower = text.lower()

        # 根据类别匹配相应的标签库
        if category in self.category_tags:
            for tag in self.category_tags[category]:
                # 简单字符串匹配(不区分大小写)
                if tag.lower() in text_lower:
                    tags.add(tag)

        # 限制为前10个最相关的标签(避免标签过多)
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
