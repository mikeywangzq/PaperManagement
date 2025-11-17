"""LLM and AI utilities."""
from typing import Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate

from config.settings import settings


def get_llm(
    temperature: Optional[float] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None
) -> ChatOpenAI:
    """Get configured LLM instance."""
    return ChatOpenAI(
        model=model or settings.llm_model,
        temperature=temperature or settings.temperature,
        max_tokens=max_tokens or settings.max_tokens,
        openai_api_key=settings.openai_api_key,
    )


def get_embeddings() -> OpenAIEmbeddings:
    """Get configured embeddings instance."""
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
