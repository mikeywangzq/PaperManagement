"""
RAG (检索增强生成) 引擎 - 用于文档问答和语义搜索

RAG (Retrieval-Augmented Generation) engine for document Q&A and search.

核心概念 (Core Concepts):
1. RAG架构: 结合检索和生成，先找相关内容再用LLM生成答案
2. 向量化: 将文本转换为向量表示，支持语义相似度搜索
3. 文档分块: 将长文档切分为小块，提高检索精度
4. 元数据过滤: 支持按分类、标签等元数据筛选文档

工作流程 (Workflow):
用户提问 → 向量化问题 → 检索相似文档片段 → 构建上下文 → LLM生成答案
"""
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter  # 文本分块工具
from langchain_community.vectorstores import Chroma  # 向量数据库
from langchain.chains import RetrievalQA  # RAG链
from langchain.docstore.document import Document as LangchainDocument  # LangChain文档对象

from backend.models.schemas import Query, QueryResponse, Category
from backend.utils.llm_utils import get_llm, get_embeddings, QA_PROMPT
from config.settings import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG引擎 - 提供语义搜索和智能问答功能

    RAG engine for semantic search and Q&A.

    核心组件 (Core Components):
    - vectorstore: ChromaDB向量数据库，存储文档向量
    - embeddings: 嵌入模型，将文本转换为向量
    - text_splitter: 文本分块器，将长文档切分为可管理的小块
    - llm: 大语言模型，用于生成答案
    """

    def __init__(self):
        """
        初始化RAG引擎

        Initialize RAG engine.

        初始化步骤 (Initialization Steps):
        1. 加载嵌入模型(OpenAI或Ollama)
        2. 创建/加载向量数据库(ChromaDB)
        3. 配置文本分块器(1000字符/块，200字符重叠)
        """
        # 获取嵌入模型(用于将文本转换为向量)
        self.embeddings = get_embeddings()

        # 设置向量数据库存储路径
        self.vectorstore_path = Path(settings.vector_db_path)
        self.vectorstore_path.mkdir(parents=True, exist_ok=True)

        # 初始化或加载ChromaDB向量数据库
        # persist_directory: 持久化存储目录，重启后数据不丢失
        self.vectorstore = Chroma(
            persist_directory=str(self.vectorstore_path),
            embedding_function=self.embeddings,
        )

        # 配置文本分块器
        # chunk_size: 每块最大字符数(1000)
        # chunk_overlap: 块之间重叠字符数(200)，保证上下文连贯性
        # separators: 分割优先级，优先在段落、句子边界分割
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        将文档添加到向量数据库

        Add a document to the vector store.

        处理流程 (Processing Flow):
        1. 文本分块: 将长文档切分为小块(1000字符/块)
        2. 向量化: 对每个块调用嵌入模型生成向量
        3. 存储: 将向量和元数据存入ChromaDB
        4. 持久化: 保存到磁盘

        分块策略 (Chunking Strategy):
        - 块大小: 1000字符(平衡检索精度和上下文完整性)
        - 重叠: 200字符(避免信息在块边界丢失)
        - 元数据: 每块记录doc_id, chunk_id, total_chunks

        Args:
            doc_id: 文档ID (Document ID)
            text: 文档全文 (Document text)
            metadata: 额外元数据，如分类、标签 (Additional metadata)

        Returns:
            创建的文档块数量 (Number of chunks created)
        """
        try:
            # 将文本切分为多个块
            chunks = self.text_splitter.split_text(text)

            # 为每个块创建LangChain文档对象，附加元数据
            documents = []
            base_metadata = metadata or {}
            base_metadata["doc_id"] = doc_id

            for i, chunk in enumerate(chunks):
                # 为每个块添加元数据
                doc_metadata = {
                    **base_metadata,
                    "chunk_id": i,  # 块序号
                    "total_chunks": len(chunks),  # 总块数
                }
                documents.append(
                    LangchainDocument(page_content=chunk, metadata=doc_metadata)
                )

            # 批量添加到向量数据库(自动调用嵌入模型)
            self.vectorstore.add_documents(documents)
            # 持久化到磁盘
            self.vectorstore.persist()

            logger.info(f"Added {len(chunks)} chunks from document {doc_id}")
            return len(chunks)

        except Exception as e:
            logger.error(f"Error adding document {doc_id} to vector store: {e}")
            raise

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Filter results by metadata

        Returns:
            List of search results with content and metadata
        """
        try:
            # Perform similarity search
            if filter_metadata:
                results = self.vectorstore.similarity_search(
                    query,
                    k=top_k,
                    filter=filter_metadata
                )
            else:
                results = self.vectorstore.similarity_search(query, k=top_k)

            # Format results
            formatted_results = []
            for doc in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Error performing search: {e}")
            raise

    def query(
        self,
        query: Query,
        language: str = "en"
    ) -> QueryResponse:
        """
        使用RAG回答问题的核心方法

        Answer a question using RAG.

        完整RAG流程 (Complete RAG Workflow):
        1. 构建过滤器: 根据分类、文档ID等筛选范围
        2. 语义检索: 向量化问题，找到最相关的文档片段
        3. 构建上下文: 将检索到的片段组合成提示词
        4. LLM生成: 基于上下文生成答案
        5. 返回结果: 包含答案和引用来源

        为什么使用RAG (Why RAG):
        - 准确性: 基于实际文档内容，而非LLM记忆
        - 可溯源: 提供来源引用，用户可验证
        - 时效性: 支持最新文档，无需重新训练模型
        - 领域性: 专注于用户的文档库

        Args:
            query: 查询对象，包含问题和过滤条件 (Query object)
            language: 回答语言 (Response language)

        Returns:
            QueryResponse对象，包含答案和来源 (QueryResponse with answer and sources)
        """
        try:
            # 构建元数据过滤器
            filter_metadata = {}
            if query.document_ids:
                # 仅在指定文档中搜索
                filter_metadata["doc_id"] = {"$in": query.document_ids}
            if query.category:
                # 仅在指定分类中搜索
                filter_metadata["category"] = query.category.value

            # 执行语义搜索，找到最相关的文档片段
            # top_k: 返回最相关的k个片段
            search_results = self.search(
                query.question,
                top_k=query.top_k,
                filter_metadata=filter_metadata if filter_metadata else None
            )

            # 从搜索结果构建上下文
            # 格式: Source 1:\n<内容>\n\nSource 2:\n<内容>
            context = "\n\n".join([
                f"Source {i+1}:\n{result['content']}"
                for i, result in enumerate(search_results)
            ])

            # 使用LLM生成答案
            llm = get_llm()
            # 使用预定义的问答提示模板
            prompt = QA_PROMPT.format(context=context, question=query.question)
            answer = llm.predict(prompt)

            # 构建响应对象
            response = QueryResponse(
                answer=answer,
                sources=search_results,  # 包含来源以供验证
            )

            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store.

        Args:
            doc_id: Document ID

        Returns:
            True if successful
        """
        try:
            # Get all documents with this doc_id
            results = self.vectorstore.get(where={"doc_id": doc_id})

            if results and "ids" in results and results["ids"]:
                # Delete by IDs
                self.vectorstore.delete(ids=results["ids"])
                self.vectorstore.persist()
                logger.info(f"Deleted {len(results['ids'])} chunks for document {doc_id}")
                return True
            else:
                logger.warning(f"No chunks found for document {doc_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting document {doc_id} from vector store: {e}")
            return False

    def get_document_count(self) -> int:
        """
        Get the number of unique documents in the vector store.

        Returns:
            Number of unique documents
        """
        try:
            # Get all unique doc_ids
            all_data = self.vectorstore.get()
            if all_data and "metadatas" in all_data:
                doc_ids = set()
                for metadata in all_data["metadatas"]:
                    if "doc_id" in metadata:
                        doc_ids.add(metadata["doc_id"])
                return len(doc_ids)
            return 0
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0

    def clear_all(self) -> bool:
        """
        Clear all documents from the vector store.

        Returns:
            True if successful
        """
        try:
            # Get all IDs and delete
            all_data = self.vectorstore.get()
            if all_data and "ids" in all_data and all_data["ids"]:
                self.vectorstore.delete(ids=all_data["ids"])
                self.vectorstore.persist()
                logger.info(f"Cleared {len(all_data['ids'])} chunks from vector store")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False
