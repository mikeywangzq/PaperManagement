"""LLM and AI utilities."""
from typing import Optional, Union
import requests
import logging

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.prompts import PromptTemplate

from config.settings import settings

logger = logging.getLogger(__name__)


def check_ollama_connection(base_url: str, timeout: int = 5) -> bool:
    """
    Check if Ollama service is running and accessible.

    Args:
        base_url: Ollama service URL
        timeout: Connection timeout in seconds

    Returns:
        True if Ollama is accessible, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logger.warning(f"Ollama connection check failed: {e}")
        return False


def get_llm(
    temperature: Optional[float] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None
) -> Union[ChatOpenAI, Ollama]:
    """
    Get configured LLM instance based on provider setting with connection validation.

    Supports both OpenAI and Ollama providers.

    Raises:
        ConnectionError: If Ollama service is not accessible
        ValueError: If OpenAI API key is missing
    """
    if settings.llm_provider == "ollama":
        # Validate Ollama connection
        if not check_ollama_connection(settings.ollama_base_url):
            raise ConnectionError(
                f"无法连接到 Ollama 服务: {settings.ollama_base_url}\n\n"
                f"请确保:\n"
                f"1. Ollama 已安装 (访问 https://ollama.com)\n"
                f"2. Ollama 服务正在运行: ollama serve\n"
                f"3. 已下载所需模型: ollama pull {settings.ollama_model}\n"
                f"4. 服务地址正确 (当前: {settings.ollama_base_url})\n\n"
                f"或者切换到 OpenAI: 在 .env 中设置 LLM_PROVIDER=openai"
            )

        logger.info(f"Using Ollama LLM: {settings.ollama_model}")
        return Ollama(
            model=model or settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=temperature or settings.temperature,
            num_predict=max_tokens or settings.max_tokens,
        )
    else:  # default to openai
        # Validate OpenAI API key
        if not settings.openai_api_key:
            raise ValueError(
                "未设置 OPENAI_API_KEY\n\n"
                "请在 .env 文件中配置:\n"
                "OPENAI_API_KEY=sk-your-api-key-here\n\n"
                "或者切换到 Ollama: 在 .env 中设置 LLM_PROVIDER=ollama"
            )

        logger.info(f"Using OpenAI LLM: {settings.llm_model}")
        return ChatOpenAI(
            model=model or settings.llm_model,
            temperature=temperature or settings.temperature,
            max_tokens=max_tokens or settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )


def get_embeddings() -> Union[OpenAIEmbeddings, OllamaEmbeddings]:
    """
    Get configured embeddings instance based on provider setting with connection validation.

    Supports both OpenAI and Ollama providers.

    Raises:
        ConnectionError: If Ollama service is not accessible
        ValueError: If OpenAI API key is missing
    """
    if settings.llm_provider == "ollama":
        # Validate Ollama connection
        if not check_ollama_connection(settings.ollama_base_url):
            raise ConnectionError(
                f"无法连接到 Ollama 服务: {settings.ollama_base_url}\n\n"
                f"请确保 Ollama 服务正在运行并已下载嵌入模型:\n"
                f"ollama pull {settings.ollama_embedding_model}\n\n"
                f"或切换到 OpenAI: 在 .env 中设置 LLM_PROVIDER=openai"
            )

        logger.info(f"Using Ollama embeddings: {settings.ollama_embedding_model}")
        return OllamaEmbeddings(
            model=settings.ollama_embedding_model,
            base_url=settings.ollama_base_url,
        )
    else:  # default to openai
        # Validate OpenAI API key
        if not settings.openai_api_key:
            raise ValueError(
                "未设置 OPENAI_API_KEY\n\n"
                "请在 .env 文件中配置 OpenAI API Key"
            )

        logger.info(f"Using OpenAI embeddings: {settings.embedding_model}")
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )


# Prompt templates
SUMMARY_PROMPT = PromptTemplate(
    input_variables=["text", "language"],
    template="""You are an expert academic assistant. Please provide a concise summary of the following research paper.

The summary should be 250-500 words and cover:
- Main contributions
- Methodology
- Key findings and conclusions

Output language: {language}

Paper text:
{text}

Summary:"""
)

KEY_POINTS_PROMPT = PromptTemplate(
    input_variables=["text", "language"],
    template="""You are an expert academic assistant. Extract the key points from the following research paper as a bullet list.

Include:
- Main innovations and contributions
- Important findings
- Methodology highlights
- Practical implications

Output language: {language}

Paper text:
{text}

Key Points:"""
)

CLASSIFICATION_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""You are an expert at classifying academic documents. Analyze the following document and:

1. Classify it into one of these categories: "machine_learning", "cryptography", or "other"
2. Extract 3-5 relevant topic tags (e.g., "CNN", "RNN", "SSL/TLS", "RSA", etc.)

Document text:
{text}

Respond in JSON format:
{{
    "category": "<category>",
    "tags": ["<tag1>", "<tag2>", ...],
    "confidence": <0.0-1.0>
}}
"""
)

QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert academic assistant. Answer the following question based on the provided context from research papers.

If the answer cannot be found in the context, say "I cannot find this information in the provided documents."

Context:
{context}

Question: {question}

Answer:"""
)

LEARNING_PATH_PROMPT = PromptTemplate(
    input_variables=["goal", "available_resources"],
    template="""You are an expert educator. Create a structured learning path for the following goal:

Goal: {goal}

Available resources in the user's library:
{available_resources}

Create a step-by-step learning path with:
1. Clear learning nodes/milestones
2. Prerequisites for each node
3. Recommended resources (from user's library or external)
4. Estimated time for each node

Format as a structured plan with numbered steps."""
)

FLASHCARD_PROMPT = PromptTemplate(
    input_variables=["topic", "content"],
    template="""You are an expert educator. Create study flashcards based on the following content.

Topic: {topic}

Content:
{content}

Generate 10-15 flashcards with clear questions and concise answers. Focus on:
- Key definitions
- Important formulas
- Core concepts
- Critical distinctions

Format each flashcard as:
Q: <question>
A: <answer>
---"""
)

CHEAT_SHEET_PROMPT = PromptTemplate(
    input_variables=["topic", "content"],
    template="""You are an expert educator. Create a concise cheat sheet for exam preparation.

Topic: {topic}

Content:
{content}

Create a cheat sheet with:
1. Key definitions
2. Important formulas
3. Core algorithms/concepts
4. Quick reference tables

Make it concise and exam-focused."""
)

COMPARISON_PROMPT = PromptTemplate(
    input_variables=["concepts", "context"],
    template="""You are an expert academic assistant. Compare and contrast the following concepts:

Concepts to compare: {concepts}

Context/Background:
{context}

Create a detailed comparison table showing:
- Similarities
- Differences
- Use cases
- Advantages/disadvantages
- Key characteristics

Present as a structured comparison."""
)
