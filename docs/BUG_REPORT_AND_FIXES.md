# Bug 报告和修复建议

> **生成日期**: 2025-01-17
> **版本**: v0.3.0
> **类型**: 代码审查和潜在问题分析

---

## 🔍 问题概述

本文档列出了代码审查中发现的所有潜在 bug、安全问题和需要改进的地方。

---

## ⚠️ 严重问题 (Critical)

### 1. 认证系统未集成到主应用

**文件**: `frontend/auth.py`, `frontend/app.py`

**问题描述**:
- 创建了 `auth.py` 模块，但没有在 `frontend/app.py` 和其他页面中实际使用
- 用户可以直接访问所有页面，绕过认证
- `login_page()` 函数中使用了 `st.set_page_config()`，这会与主应用冲突

**影响**: 🔴 高 - 安全漏洞，认证形同虚设

**修复建议**:

```python
# frontend/app.py - 在文件开头添加
from frontend.auth import check_authentication, login_page, display_user_info

# 在主内容之前检查认证
if not check_authentication():
    login_page()
    st.stop()  # 停止执行后续代码

# 显示用户信息
display_user_info()

# 其余代码...
```

```python
# frontend/auth.py - 修改 login_page()
def login_page():
    """Display login page without page config."""
    # 移除 st.set_page_config() 调用

    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # 其余代码保持不变...
```

```python
# 每个页面文件都需要添加认证检查
# frontend/pages/1_📄_论文总结.py
from frontend.auth import check_authentication, login_page
import streamlit as st

st.set_page_config(page_title="论文总结", page_icon="📄", layout="wide")

# 认证检查
if not check_authentication():
    login_page()
    st.stop()

# 其余代码...
```

---

### 2. Ollama 连接未验证

**文件**: `backend/utils/llm_utils.py`

**问题描述**:
- 当 `LLM_PROVIDER=ollama` 时，代码直接尝试连接 Ollama
- 没有检查 Ollama 服务是否运行
- 如果 Ollama 未运行，会导致整个应用崩溃

**影响**: 🔴 高 - 应用崩溃

**修复建议**:

```python
import requests
from typing import Union

def check_ollama_connection(base_url: str) -> bool:
    """检查 Ollama 服务是否可用"""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_llm(
    temperature: Optional[float] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None
) -> Union[ChatOpenAI, Ollama]:
    """Get configured LLM instance with connection validation."""

    if settings.llm_provider == "ollama":
        # 验证 Ollama 连接
        if not check_ollama_connection(settings.ollama_base_url):
            raise ConnectionError(
                f"无法连接到 Ollama 服务: {settings.ollama_base_url}\n"
                f"请确保 Ollama 正在运行: ollama serve"
            )

        return Ollama(
            model=model or settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=temperature or settings.temperature,
            num_predict=max_tokens or settings.max_tokens,
        )
    else:
        # OpenAI provider
        if not settings.openai_api_key:
            raise ValueError(
                "未设置 OPENAI_API_KEY\n"
                "请在 .env 文件中配置: OPENAI_API_KEY=sk-..."
            )

        return ChatOpenAI(
            model=model or settings.llm_model,
            temperature=temperature or settings.temperature,
            max_tokens=max_tokens or settings.max_tokens,
            openai_api_key=settings.openai_api_key,
        )
```

---

### 3. EPUB 处理可能抛出异常

**文件**: `backend/core/document_processor.py`

**问题描述**:
- `process_epub()` 方法中访问元数据时使用了 `[0][0]` 索引
- 如果元数据不存在，会抛出 `IndexError`
- 某些 EPUB 文件可能缺少标准元数据

**影响**: 🟡 中 - 某些 EPUB 文件处理失败

**修复建议**:

```python
def process_epub(self, file_path: str) -> Dict[str, Any]:
    """Extract text and metadata from EPUB file with better error handling."""
    try:
        book = epub.read_epub(file_path)
        text_content = []

        # Extract text from all items
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                try:
                    # Parse HTML content
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text(separator='\n', strip=True)
                    if text:
                        text_content.append(text)
                except Exception as e:
                    logger.warning(f"Failed to parse EPUB item: {e}")
                    continue

        full_text = "\n\n".join(text_content)

        # Extract metadata with safe access
        def safe_get_metadata(dc_type, default=None):
            """Safely get metadata from EPUB"""
            try:
                meta = book.get_metadata('DC', dc_type)
                if meta and len(meta) > 0 and len(meta[0]) > 0:
                    return meta[0][0]
            except Exception:
                pass
            return default

        metadata = {
            "title": safe_get_metadata('title', Path(file_path).stem),
            "author": safe_get_metadata('creator'),
            "language": safe_get_metadata('language'),
            "publisher": safe_get_metadata('publisher'),
        }

        return {
            "text": full_text,
            "num_pages": None,
            "metadata": metadata,
            "title": metadata.get("title", Path(file_path).stem),
        }

    except Exception as e:
        logger.error(f"Error processing EPUB {file_path}: {e}")
        raise
```

---

### 4. 密码哈希安全性不足

**文件**: `frontend/auth.py`

**问题描述**:
- 使用简单的 SHA-256 哈希存储密码
- 没有使用盐值 (salt)
- 容易受到彩虹表攻击

**影响**: 🔴 高 - 安全漏洞

**修复建议**:

```python
import hashlib
import secrets

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash a password with salt using PBKDF2.

    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)

    # 使用 PBKDF2 而不是简单的 SHA-256
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 迭代次数
    ).hex()

    return password_hash, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """验证密码"""
    new_hash, _ = hash_password(password, salt)
    return new_hash == hashed
```

更新 `users.yaml` 格式:
```yaml
credentials:
  usernames:
    admin:
      name: "Administrator"
      password: "<hashed-password>"
      salt: "<random-salt>"
      role: "admin"
```

---

## 🟡 中等问题 (Medium)

### 5. i18n 未集成到所有页面

**文件**: `frontend/pages/*.py`

**问题描述**:
- `i18n.py` 模块已创建，但只在 `app.py` 中使用
- 其他页面（论文总结、资料管理等）仍然是硬编码的中文文本
- 语言切换不会影响这些页面

**影响**: 🟡 中 - 功能不完整

**修复建议**:

```python
# frontend/pages/1_📄_论文总结.py
import streamlit as st
from frontend.i18n import t, language_selector

st.set_page_config(page_title=t("paper_summary"), page_icon="📄", layout="wide")

# 添加语言选择器
language_selector()

st.title(f"📄 {t('paper_summary')}")

# 使用翻译函数替换所有硬编码文本
tab1, tab2, tab3 = st.tabs([
    t("upload_document"),
    t("document_analysis"),
    t("intelligent_qa")
])

# 所有文本都使用 t() 函数
uploaded_files = st.file_uploader(
    t("select_files"),
    type=["pdf", "txt", "md", "docx", "pptx", "epub"],
    accept_multiple_files=True
)
```

需要更新的页面:
- ✅ `frontend/app.py` (已完成)
- ❌ `frontend/pages/1_📄_论文总结.py`
- ❌ `frontend/pages/2_📚_资料管理.py`
- ❌ `frontend/pages/3_🗺️_学习路线.py`
- ❌ `frontend/pages/4_📝_考试复习.py`

---

### 6. 文档大小限制未实施

**文件**: `config/settings.py`, `backend/core/document_processor.py`

**问题描述**:
- 配置中定义了 `MAX_FILE_SIZE_MB=50`
- 但在文档处理时没有实际检查文件大小
- 可能导致内存溢出

**影响**: 🟡 中 - 性能和稳定性问题

**修复建议**:

```python
# backend/core/document_processor.py

def save_document(
    self,
    file_path: str,
    document_type: Optional[DocumentType] = None,
    arxiv_id: Optional[str] = None
) -> Document:
    """Process and save a document with size validation."""

    # 检查文件大小
    if not arxiv_id:  # arXiv 文件在下载后检查
        file_size_mb = get_file_size(file_path) / (1024 * 1024)
        max_size = getattr(settings, 'max_file_size_mb', 50)

        if file_size_mb > max_size:
            raise ValueError(
                f"文件过大: {file_size_mb:.2f}MB\n"
                f"最大允许: {max_size}MB\n"
                f"请在 .env 中调整 MAX_FILE_SIZE_MB"
            )

    # 其余代码...
```

在前端也添加检查:
```python
# frontend/pages/1_📄_论文总结.py

for uploaded_file in uploaded_files:
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > 50:
        st.error(f"❌ 文件 {uploaded_file.name} 过大: {file_size_mb:.2f}MB (最大 50MB)")
        continue

    # 处理文件...
```

---

### 7. DOCX/PPTX 表格提取可能失败

**文件**: `backend/core/document_processor.py`

**问题描述**:
- `process_docx()` 和 `process_pptx()` 假设所有形状都有 `text` 属性
- 某些形状（如图片、图表）没有 `text` 属性
- 可能导致 `AttributeError`

**影响**: 🟡 中 - 某些文档处理失败

**修复建议**:

```python
def process_docx(self, file_path: str) -> Dict[str, Any]:
    """Extract text from DOCX with better error handling."""
    try:
        doc = DocxDocument(file_path)
        text_content = []

        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text and paragraph.text.strip():
                text_content.append(paragraph.text)

        # Extract text from tables with error handling
        for table in doc.tables:
            try:
                for row in table.rows:
                    row_text = " | ".join([
                        cell.text.strip() if hasattr(cell, 'text') else ''
                        for cell in row.cells
                    ])
                    if row_text.strip():
                        text_content.append(row_text)
            except Exception as e:
                logger.warning(f"Failed to process table in DOCX: {e}")
                continue

        # 其余代码...
    except Exception as e:
        logger.error(f"Error processing DOCX {file_path}: {e}")
        raise

def process_pptx(self, file_path: str) -> Dict[str, Any]:
    """Extract text from PPTX with better error handling."""
    try:
        prs = Presentation(file_path)
        text_content = []

        for slide_num, slide in enumerate(prs.slides, 1):
            slide_text = [f"=== Slide {slide_num} ==="]

            for shape in slide.shapes:
                try:
                    # 安全检查 text 属性
                    if hasattr(shape, "text"):
                        text = shape.text.strip()
                        if text:
                            slide_text.append(text)
                    # 检查表格
                    elif hasattr(shape, "table"):
                        table = shape.table
                        for row in table.rows:
                            row_text = " | ".join([
                                cell.text.strip() if hasattr(cell, 'text') else ''
                                for cell in row.cells
                            ])
                            if row_text.strip():
                                slide_text.append(row_text)
                except Exception as e:
                    logger.warning(f"Failed to process shape in slide {slide_num}: {e}")
                    continue

            if len(slide_text) > 1:
                text_content.append("\n".join(slide_text))

        # 其余代码...
    except Exception as e:
        logger.error(f"Error processing PPTX {file_path}: {e}")
        raise
```

---

### 8. ChromaDB 并发访问问题

**文件**: `backend/core/rag_engine.py`

**问题描述**:
- Streamlit 是多线程应用
- ChromaDB 的 PersistentClient 可能在并发访问时出问题
- 没有使用线程锁保护

**影响**: 🟡 中 - 可能的数据竞争

**修复建议**:

```python
import threading
from typing import Optional, List, Dict, Any

class RAGEngine:
    """RAG engine with thread-safe ChromaDB access."""

    _lock = threading.Lock()  # 类级别的锁

    def __init__(self):
        """Initialize RAG engine with thread-safe client."""
        with self._lock:
            self.vectorstore_path = Path(settings.vector_db_path)
            self.vectorstore_path.mkdir(parents=True, exist_ok=True)

            # Initialize embeddings
            self.embeddings = get_embeddings()

            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.vectorstore_path)
            )

            # Get or create collection
            self.collection_name = "documents"
            self.vectorstore = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )

            # Text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                length_function=len,
            )

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict] = None) -> int:
        """Add document with thread safety."""
        with self._lock:
            # 其余代码...
            pass

    def search(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search with thread safety."""
        with self._lock:
            # 其余代码...
            pass
```

---

## 🔵 次要问题 (Minor)

### 9. 缺少输入验证

**文件**: 多个文件

**问题描述**:
- 用户输入没有进行充分验证
- 可能导致注入攻击或程序错误

**修复建议**:

```python
# 验证 arXiv ID 格式
import re

def validate_arxiv_id(arxiv_id: str) -> bool:
    """验证 arXiv ID 格式"""
    pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
    return bool(re.match(pattern, arxiv_id))

# 在使用前验证
if arxiv_id:
    if not validate_arxiv_id(arxiv_id):
        st.error("无效的 arXiv ID 格式。示例: 2301.12345")
    else:
        # 处理...
```

```python
# 验证文件路径
from pathlib import Path

def is_safe_path(path: str, base_dir: str) -> bool:
    """检查路径是否在基础目录内（防止路径遍历）"""
    try:
        base_path = Path(base_dir).resolve()
        file_path = Path(path).resolve()
        return file_path.is_relative_to(base_path)
    except (ValueError, OSError):
        return False
```

---

### 10. 错误消息不够友好

**文件**: 多个文件

**问题描述**:
- 抛出的异常消息是技术性的
- 普通用户难以理解

**修复建议**:

```python
# 创建自定义异常类
class UserFriendlyError(Exception):
    """用户友好的错误类"""
    def __init__(self, user_message: str, technical_message: str = None):
        self.user_message = user_message
        self.technical_message = technical_message or user_message
        super().__init__(self.technical_message)

# 使用示例
try:
    result = processor.process_pdf(file_path)
except Exception as e:
    logger.error(f"PDF processing failed: {e}")
    raise UserFriendlyError(
        user_message="无法处理此 PDF 文件。请确保文件未损坏且包含可提取的文本。",
        technical_message=str(e)
    )
```

```python
# 在 Streamlit 中捕获和显示
try:
    doc = components["doc_processor"].save_document(str(file_path))
except UserFriendlyError as e:
    st.error(f"❌ {e.user_message}")
    with st.expander("技术详情"):
        st.code(e.technical_message)
except Exception as e:
    st.error(f"❌ 处理失败: {str(e)}")
```

---

### 11. 日志配置不完整

**文件**: 所有 Python 文件

**问题描述**:
- 使用了 `logging.getLogger(__name__)`
- 但没有配置日志格式和输出
- 日志信息难以追踪

**修复建议**:

创建 `backend/utils/logging_config.py`:

```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """配置应用日志"""

    # 创建日志格式
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # 文件处理器（可选）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        root_logger.addHandler(file_handler)

    return root_logger
```

在 `frontend/app.py` 开头:
```python
from backend.utils.logging_config import setup_logging

# 设置日志
setup_logging(log_level="INFO", log_file="logs/app.log")
```

---

### 12. 缺少进度指示

**文件**: `backend/core/document_processor.py`, `backend/core/rag_engine.py`

**问题描述**:
- 长时间运行的操作没有进度反馈
- 用户不知道操作是否在进行中

**修复建议**:

```python
# 在处理大文档时添加进度回调
from typing import Callable

def process_large_document(
    file_path: str,
    progress_callback: Callable[[float], None] = None
) -> Dict[str, Any]:
    """处理大文档并报告进度"""

    total_steps = 4
    current_step = 0

    def update_progress():
        nonlocal current_step
        current_step += 1
        if progress_callback:
            progress_callback(current_step / total_steps)

    # Step 1: 读取文件
    doc = fitz.open(file_path)
    update_progress()

    # Step 2: 提取文本
    text_content = []
    for page in doc:
        text_content.append(page.get_text())
    update_progress()

    # Step 3: 提取元数据
    metadata = doc.metadata
    update_progress()

    # Step 4: 组装结果
    result = {...}
    update_progress()

    return result
```

在 Streamlit 中使用:
```python
progress_bar = st.progress(0)

def update_progress(value):
    progress_bar.progress(value)

result = process_large_document(file_path, progress_callback=update_progress)
```

---

### 13. 缺少配置验证

**文件**: `config/settings.py`

**问题描述**:
- 没有验证配置的有效性
- 错误的配置可能导致运行时错误

**修复建议**:

```python
from pydantic import field_validator, ValidationError

class Settings(BaseSettings):
    # ... 现有字段 ...

    @field_validator('llm_provider')
    @classmethod
    def validate_llm_provider(cls, v):
        """验证 LLM 提供商"""
        if v not in ['openai', 'ollama']:
            raise ValueError(f"Invalid LLM_PROVIDER: {v}. Must be 'openai' or 'ollama'")
        return v

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        """验证温度参数"""
        if not 0 <= v <= 2:
            raise ValueError(f"Temperature must be between 0 and 2, got {v}")
        return v

    @field_validator('chunk_size')
    @classmethod
    def validate_chunk_size(cls, v):
        """验证分块大小"""
        if v < 100 or v > 10000:
            raise ValueError(f"Chunk size must be between 100 and 10000, got {v}")
        return v

    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v, info):
        """验证 OpenAI API Key（如果使用 OpenAI）"""
        provider = info.data.get('llm_provider', 'openai')
        if provider == 'openai' and not v:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai\n"
                "Please set it in your .env file"
            )
        return v

# 在应用启动时验证
try:
    settings = Settings()
except ValidationError as e:
    print("❌ 配置错误:")
    for error in e.errors():
        print(f"  - {error['loc'][0]}: {error['msg']}")
    sys.exit(1)
```

---

### 14. st.rerun() 可能导致问题

**文件**: `frontend/i18n.py`

**问题描述**:
- 使用了 `st.rerun()` 在语言切换时刷新页面
- 在某些 Streamlit 版本中可能不稳定
- 可能导致状态丢失

**修复建议**:

```python
def language_selector():
    """Display language selector with stable state management."""
    with st.sidebar:
        st.markdown("---")
        current_lang = get_language()

        lang_options = {
            "zh": "🇨🇳 中文",
            "en": "🇬🇧 English"
        }

        # 使用 on_change 回调而不是手动检查
        def on_language_change():
            """语言改变时的回调"""
            # 清除某些缓存（如果需要）
            st.cache_data.clear()

        selected_lang_label = st.selectbox(
            t("language"),
            options=list(lang_options.values()),
            index=0 if current_lang == "zh" else 1,
            key="language_selector",
            on_change=on_language_change
        )

        selected_lang = "zh" if "中文" in selected_lang_label else "en"

        if selected_lang != current_lang:
            set_language(selected_lang)
            # 使用 experimental_rerun 作为后备
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
```

---

## 📋 测试建议

### 单元测试

创建 `tests/test_document_processor.py`:

```python
import pytest
from backend.core.document_processor import DocumentProcessor
from backend.models.schemas import DocumentType

@pytest.fixture
def processor():
    return DocumentProcessor()

def test_process_pdf_with_valid_file(processor):
    """测试处理有效的 PDF 文件"""
    result = processor.process_pdf("tests/fixtures/sample.pdf")
    assert "text" in result
    assert len(result["text"]) > 0

def test_process_pdf_with_invalid_file(processor):
    """测试处理无效的 PDF 文件"""
    with pytest.raises(Exception):
        processor.process_pdf("nonexistent.pdf")

def test_process_docx(processor):
    """测试处理 DOCX 文件"""
    result = processor.process_docx("tests/fixtures/sample.docx")
    assert result["text"]
    assert result["metadata"]

def test_file_size_limit(processor):
    """测试文件大小限制"""
    # 创建一个超大文件的测试
    pass
```

### 集成测试

创建 `tests/test_integration.py`:

```python
def test_full_document_workflow():
    """测试完整的文档工作流"""
    # 1. 上传文档
    processor = DocumentProcessor()
    doc = processor.save_document("tests/fixtures/sample.pdf")

    # 2. 添加到 RAG
    rag = RAGEngine()
    rag.add_document(doc.id, processor.get_document_text(doc.id))

    # 3. 分类
    classifier = Classifier()
    result = classifier.classify_document(doc.id)
    assert result.category

    # 4. 问答
    from backend.models.schemas import Query
    query = Query(question="What is this about?")
    response = rag.query(query)
    assert response.answer

def test_authentication_flow():
    """测试认证流程"""
    from frontend.auth import hash_password, verify_password

    password = "test123"
    hashed, salt = hash_password(password)

    assert verify_password(password, hashed, salt)
    assert not verify_password("wrong", hashed, salt)
```

---

## 🔧 性能优化建议

### 1. 缓存优化

```python
# 使用更精细的缓存控制
@st.cache_data(ttl=3600, show_spinner=False)
def get_document_list():
    """缓存文档列表 1 小时"""
    return processor.list_documents()

@st.cache_resource
def get_rag_engine():
    """缓存 RAG 引擎（全局单例）"""
    return RAGEngine()
```

### 2. 批处理优化

```python
def batch_add_documents(documents: List[Tuple[str, str]], batch_size: int = 10):
    """批量添加文档到向量数据库"""
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        # 批量处理
        rag.add_documents_batch(batch)
```

### 3. 异步处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_documents_async(files: List[str]):
    """异步处理多个文档"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [
            loop.run_in_executor(executor, processor.save_document, f)
            for f in files
        ]
        results = await asyncio.gather(*tasks)
    return results
```

---

## ✅ 修复优先级

### 立即修复 (P0)
1. ✅ 集成认证系统到所有页面
2. ✅ 添加 Ollama 连接验证
3. ✅ 修复密码哈希安全问题

### 高优先级 (P1)
4. ⬜ 修复 EPUB 元数据访问
5. ⬜ 添加文件大小检查
6. ⬜ 修复 DOCX/PPTX 处理异常

### 中优先级 (P2)
7. ⬜ 完成 i18n 集成
8. ⬜ 添加线程安全锁
9. ⬜ 改进错误消息
10. ⬜ 配置日志系统

### 低优先级 (P3)
11. ⬜ 添加输入验证
12. ⬜ 添加进度指示
13. ⬜ 配置验证
14. ⬜ 改进 rerun 处理

---

## 📝 总结

**发现的问题总数**: 14

**严重程度分布**:
- 🔴 严重 (Critical): 4
- 🟡 中等 (Medium): 4
- 🔵 次要 (Minor): 6

**建议的修复时间**:
- P0 (立即): ~4小时
- P1 (高): ~6小时
- P2 (中): ~8小时
- P3 (低): ~6小时

**总计**: ~24小时工作量

---

**生成者**: Claude AI
**审查日期**: 2025-01-17
**版本**: v0.3.0
