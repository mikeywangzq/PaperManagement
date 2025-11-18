"""
论文总结模块 - 生成论文摘要和提取关键点

Summarizer module for generating paper summaries and key points.

核心功能 (Core Features):
1. 生成摘要: 将长论文压缩为250-500字的简洁摘要
2. 提取关键点: 以列表形式提取论文的核心要点
3. 完整分析: 提取方法论、贡献、结论、数据集等
4. 多语言: 支持中文和英文输出

技术要点 (Technical Points):
- 使用低温度(0.3)确保输出稳定和专注
- 文本截断: 限制输入长度避免超过模型上下文窗口
- 智能解析: 从LLM输出中解析结构化信息(列表、段落等)
"""
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
    """
    论文总结器 - 生成摘要和提取关键信息

    Generate summaries and extract key points from papers.

    设计原则 (Design Principles):
    - 简洁性: 摘要控制在250-500字，突出核心内容
    - 结构化: 将非结构化文本转换为结构化信息
    - 准确性: 使用低温度参数确保输出稳定
    """

    def __init__(self):
        """
        初始化总结器

        Initialize summarizer.

        配置说明 (Configuration):
        - temperature=0.3: 低温度参数，输出更确定、更专注
          (高温度会更有创造性但可能偏离主题)
        """
        self.llm = get_llm(temperature=0.3)  # 低温度确保输出稳定专注
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
        生成论文的简洁摘要

        Generate a concise summary of a paper.

        处理流程 (Processing Flow):
        1. 获取文档全文
        2. 截断文本(如果超过8000 tokens)
        3. 使用预定义提示模板调用LLM
        4. 返回250-500字的摘要

        提示工程 (Prompt Engineering):
        - 明确要求摘要长度(250-500字)
        - 指定包含的内容: 主要贡献、方法论、主要发现
        - 指定输出语言(中文或英文)

        Args:
            doc_id: 文档ID (Document ID)
            language: 输出语言，"en"或"zh" (Output language)

        Returns:
            摘要文本，250-500字 (Summary text, 250-500 words)
        """
        try:
            # 获取文档文本
            text = self.doc_processor.get_document_text(doc_id)
            if not text:
                raise ValueError(f"Document {doc_id} not found")

            # 如果文本过长则截断(避免超过模型上下文限制)
            text = self._truncate_text(text)

            # 使用摘要提示模板生成摘要
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
        从论文中提取关键点

        Extract key points from a paper.

        处理流程 (Processing Flow):
        1. 获取文档全文并截断
        2. 使用关键点提取提示模板
        3. LLM返回项目符号列表
        4. 解析并清理列表格式(去除符号、编号)

        提示要求 (Prompt Requirements):
        - 主要创新和贡献
        - 重要发现
        - 方法论亮点
        - 实践意义

        文本解析 (Text Parsing):
        支持多种列表格式:
        - 项目符号: -, *, •, ·
        - 编号列表: 1. 2. 3.
        自动清理格式保留纯文本

        Args:
            doc_id: 文档ID (Document ID)
            language: 输出语言 (Output language)

        Returns:
            关键点列表 (List of key points)
        """
        try:
            # 获取文档文本
            text = self.doc_processor.get_document_text(doc_id)
            if not text:
                raise ValueError(f"Document {doc_id} not found")

            # 截断过长文本
            text = self._truncate_text(text)

            # 提取关键点
            prompt = KEY_POINTS_PROMPT.format(text=text, language=language)
            response = self.llm.predict(prompt)

            # 解析列表格式的关键点
            key_points = []
            for line in response.split('\n'):
                line = line.strip()
                # 移除项目符号
                if line.startswith(('-', '*', '•', '·')):
                    line = line[1:].strip()
                # 移除编号列表标记
                elif line and line[0].isdigit() and '.' in line[:4]:
                    line = line.split('.', 1)[1].strip()

                # 添加非空行
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
