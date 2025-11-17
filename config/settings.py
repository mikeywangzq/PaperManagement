"""
应用程序设置和配置模块

该模块负责管理整个应用的配置项，包括：
- OpenAI API配置
- 文件路径配置
- RAG系统参数
- LLM模型参数

所有配置都可以通过环境变量(.env文件)进行覆盖。
"""
import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用程序设置类

    使用Pydantic BaseSettings自动从环境变量加载配置。
    支持通过.env文件配置所有参数。
    """

    model_config = SettingsConfigDict(
        env_file=".env",                  # 从.env文件读取配置
        env_file_encoding="utf-8",        # 使用UTF-8编码
        case_sensitive=False,             # 环境变量名不区分大小写
        extra="ignore"                    # 忽略额外的环境变量
    )

    # ===== LLM Provider配置 =====
    llm_provider: str = "openai"          # LLM提供商: "openai" 或 "ollama"

    # ===== OpenAI配置 =====
    openai_api_key: str = ""              # OpenAI API密钥 (必填)
    openai_api_base: str = "https://api.openai.com/v1"  # API基础URL
    embedding_model: str = "text-embedding-3-small"      # 向量化模型
    llm_model: str = "gpt-4-turbo-preview"              # 大语言模型

    # ===== Ollama配置 =====
    ollama_base_url: str = "http://localhost:11434"      # Ollama服务地址
    ollama_model: str = "llama2"                         # Ollama模型名称
    ollama_embedding_model: str = "nomic-embed-text"     # Ollama嵌入模型

    # ===== 文件路径配置 =====
    vector_db_path: str = "./data/vectorstore"   # 向量数据库存储路径
    document_path: str = "./data/documents"      # 文档存储路径
    metadata_path: str = "./data/metadata"       # 元数据存储路径

    # ===== 应用设置 =====
    max_file_size_mb: int = 50                   # 最大文件大小(MB)
    supported_languages: List[str] = ["en", "zh"] # 支持的语言

    # ===== RAG系统配置 =====
    chunk_size: int = 1000        # 文档分块大小(字符数)
    chunk_overlap: int = 200      # 分块重叠大小(字符数)，用于保持上下文连贯性
    top_k_results: int = 5        # 检索返回的相关文档数量

    # ===== LLM生成配置 =====
    temperature: float = 0.7      # 生成温度(0-1)，越高越随机，越低越确定
    max_tokens: int = 2000        # 最大生成token数

    @property
    def max_file_size_bytes(self) -> int:
        """
        将最大文件大小转换为字节数

        Returns:
            int: 最大文件大小(字节)
        """
        return self.max_file_size_mb * 1024 * 1024

    def ensure_directories(self):
        """
        确保所有必需的目录都存在

        如果目录不存在，则自动创建。这样可以避免在运行时出现
        "目录不存在"的错误。
        """
        paths = [
            self.vector_db_path,   # 向量数据库目录
            self.document_path,    # 文档存储目录
            self.metadata_path,    # 元数据目录
        ]
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)


# ===== 全局设置实例 =====
# 在模块导入时创建单例设置对象，整个应用共享此实例
settings = Settings()
# 确保所有必需的目录都存在
settings.ensure_directories()
