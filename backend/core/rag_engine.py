"""RAG (Retrieval-Augmented Generation) engine for document Q&A and search."""
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document as LangchainDocument

from backend.models.schemas import Query, QueryResponse, Category
from backend.utils.llm_utils import get_llm, get_embeddings, QA_PROMPT
from config.settings import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine for semantic search and Q&A."""

    def __init__(self):
        """Initialize RAG engine."""
        self.embeddings = get_embeddings()
        self.vectorstore_path = Path(settings.vector_db_path)
        self.vectorstore_path.mkdir(parents=True, exist_ok=True)

        # Initialize or load vector store
        self.vectorstore = Chroma(
            persist_directory=str(self.vectorstore_path),
            embedding_function=self.embeddings,
        )

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
        Add a document to the vector store.

        Args:
            doc_id: Document ID
            text: Document text
            metadata: Additional metadata

        Returns:
            Number of chunks created
        """
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)

            # Create Langchain documents with metadata
            documents = []
            base_metadata = metadata or {}
            base_metadata["doc_id"] = doc_id

            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    **base_metadata,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                }
                documents.append(
                    LangchainDocument(page_content=chunk, metadata=doc_metadata)
                )

            # Add to vector store
            self.vectorstore.add_documents(documents)
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
        Answer a question using RAG.

        Args:
            query: Query object
            language: Response language

        Returns:
            QueryResponse with answer and sources
        """
        try:
            # Build filter if needed
            filter_metadata = {}
            if query.document_ids:
                filter_metadata["doc_id"] = {"$in": query.document_ids}
            if query.category:
                filter_metadata["category"] = query.category.value

            # Search for relevant context
            search_results = self.search(
                query.question,
                top_k=query.top_k,
                filter_metadata=filter_metadata if filter_metadata else None
            )

            # Build context from search results
            context = "\n\n".join([
                f"Source {i+1}:\n{result['content']}"
                for i, result in enumerate(search_results)
            ])

            # Generate answer using LLM
            llm = get_llm()
            prompt = QA_PROMPT.format(context=context, question=query.question)
            answer = llm.predict(prompt)

            # Build response
            response = QueryResponse(
                answer=answer,
                sources=search_results,
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
