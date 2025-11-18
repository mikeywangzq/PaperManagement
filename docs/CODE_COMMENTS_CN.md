# 代码中文注释文档

> **版本**: v0.3.0
> **日期**: 2025-01-17
> **目的**: 为核心模块提供详细的中文注释和说明

---

## 目录

1. [DocumentProcessor - 文档处理器](#1-documentprocessor---文档处理器)
2. [RAGEngine - RAG 引擎](#2-ragengine---rag-引擎)
3. [Summarizer - 摘要生成器](#3-summarizer---摘要生成器)
4. [Classifier - 分类器](#4-classifier---分类器)
5. [LLM Utils - LLM 工具](#5-llm-utils---llm-工具)
6. [Authentication - 认证模块](#6-authentication---认证模块)

---

## 1. DocumentProcessor - 文档处理器

**文件**: `backend/core/document_processor.py`

### 模块说明

```python
"""
文档处理模块 - 从各种文件格式中提取文本

本模块负责处理多种文档格式，包括：
- PDF 文件 (使用 PyMuPDF/fitz)
- Word 文档 (DOCX)
- PowerPoint 演示文稿 (PPTX)
- 电子书 (EPUB)
- 纯文本和 Markdown 文件
- arXiv 论文（自动下载）

核心功能：
1. 文本提取：从各种格式中提取纯文本内容
2. 元数据解析：提取文档的标题、作者、创建日期等信息
3. 文档存储：保存处理后的文档和元数据到 JSON 文件
4. 文档管理：列出、查询、删除文档

数据流：
用户上传文档
  → process_xxx() 提取文本和元数据
  → save_document() 保存到本地
  → 返回 Document 对象

存储结构：
- data/documents/: 原始文档文件
- data/metadata/{doc_id}.json: 文档元数据
- data/metadata/{doc_id}_text.txt: 提取的纯文本
"""
```

### 类定义

```python
class DocumentProcessor:
    """
    文档处理器类

    职责：
    1. 统一处理多种文档格式
    2. 提取文本内容和元数据
    3. 管理文档的本地存储
    4. 提供文档的 CRUD 操作

    属性：
        metadata_dir (Path): 元数据存储目录 (./data/metadata)
        document_dir (Path): 文档存储目录 (./data/documents)

    使用示例：
        processor = DocumentProcessor()

        # 处理 PDF
        result = processor.process_pdf("paper.pdf")

        # 保存文档
        doc = processor.save_document("paper.pdf")

        # 获取文档文本
        text = processor.get_document_text(doc.id)
    """

    def __init__(self):
        """
        初始化文档处理器

        操作：
        1. 从配置中读取路径
        2. 创建必要的存储目录
        3. 如果目录不存在，自动创建（parents=True）

        目录结构：
        data/
        ├── documents/        # 原始文档
        └── metadata/         # 元数据和提取的文本
            ├── {id}.json     # 文档元数据
            └── {id}_text.txt # 提取的文本
        """
        self.metadata_dir = Path(settings.metadata_path)
        self.document_dir = Path(settings.document_path)

        # 创建目录（如果不存在）
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.document_dir.mkdir(parents=True, exist_ok=True)
```

### 核心方法注释

#### process_pdf() - PDF 处理

```python
def process_pdf(self, file_path: str) -> Dict[str, Any]:
    """
    从 PDF 文件中提取文本和元数据

    使用 PyMuPDF (fitz) 库处理 PDF 文件。
    逐页提取文本，并解析 PDF 内置的元数据。

    参数：
        file_path (str): PDF 文件的完整路径

    返回：
        Dict[str, Any]: 包含以下键的字典
            - text (str): 提取的全文，页面之间用 \n\n 分隔
            - num_pages (int): PDF 总页数
            - metadata (dict): PDF 元数据（标题、作者、创建日期等）
            - title (str): 文档标题（优先使用元数据，否则使用文件名）

    异常：
        Exception: PDF 损坏、无法读取等错误

    实现细节：
        1. 使用 fitz.open() 打开 PDF 文件
        2. 遍历每一页，使用 page.get_text() 提取文本
        3. 从 doc.metadata 获取 PDF 内置元数据
        4. 拼接所有页面的文本
        5. 关闭文档以释放资源

    示例：
        result = processor.process_pdf("research_paper.pdf")
        print(result["title"])      # "Deep Learning Survey"
        print(result["num_pages"])  # 15
        print(len(result["text"]))  # 45000 (字符数)
    """
    try:
        # 打开 PDF 文档
        doc = fitz.open(file_path)
        text_content = []

        # 逐页提取文本
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_content.append(page.get_text())

        # 合并所有页面的文本，页面之间用双换行分隔
        full_text = "\n\n".join(text_content)

        # 提取 PDF 元数据（标题、作者等）
        metadata = doc.metadata

        # 构建返回结果
        result = {
            "text": full_text,
            "num_pages": len(doc),
            "metadata": metadata,
            "title": metadata.get("title", Path(file_path).stem),
        }

        # 关闭文档，释放资源
        doc.close()
        return result

    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {e}")
        raise
```

#### process_docx() - Word 文档处理

```python
def process_docx(self, file_path: str) -> Dict[str, Any]:
    """
    从 Word 文档 (DOCX) 中提取文本和元数据

    使用 python-docx 库处理 Word 文档。
    提取段落文本和表格内容。

    参数：
        file_path (str): DOCX 文件的完整路径

    返回：
        Dict[str, Any]: 包含以下键的字典
            - text (str): 提取的全文（段落 + 表格）
            - num_pages (None): DOCX 没有固定页数概念
            - metadata (dict): Word 文档属性（标题、作者、修改日期等）
            - title (str): 文档标题

    提取内容：
        1. 段落文本：doc.paragraphs
        2. 表格内容：doc.tables（转换为 " | " 分隔的文本）

    元数据来源：
        - core_properties.title: 文档标题
        - core_properties.author: 作者
        - core_properties.subject: 主题
        - core_properties.created: 创建时间
        - core_properties.modified: 修改时间

    示例：
        result = processor.process_docx("report.docx")
        print(result["metadata"]["author"])  # "John Doe"
        print("表格内容" in result["text"])   # True
    """
    try:
        # 打开 Word 文档
        doc = DocxDocument(file_path)
        text_content = []

        # 1. 提取所有段落的文本
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # 跳过空段落
                text_content.append(paragraph.text)

        # 2. 提取表格中的文本
        for table in doc.tables:
            for row in table.rows:
                # 将单元格内容用 " | " 连接
                row_text = " | ".join([cell.text.strip() for cell in row.cells])
                if row_text.strip():
                    text_content.append(row_text)

        # 合并所有文本
        full_text = "\n\n".join(text_content)

        # 提取文档属性（元数据）
        core_properties = doc.core_properties
        metadata = {
            "title": core_properties.title or Path(file_path).stem,
            "author": core_properties.author,
            "subject": core_properties.subject,
            "created": str(core_properties.created) if core_properties.created else None,
            "modified": str(core_properties.modified) if core_properties.modified else None,
        }

        return {
            "text": full_text,
            "num_pages": None,  # DOCX 没有固定页数
            "metadata": metadata,
            "title": metadata.get("title", Path(file_path).stem),
        }

    except Exception as e:
        logger.error(f"Error processing DOCX {file_path}: {e}")
        raise
```

#### save_document() - 文档保存

```python
def save_document(
    self,
    file_path: str,
    document_type: Optional[DocumentType] = None,
    arxiv_id: Optional[str] = None
) -> Document:
    """
    处理并保存文档到本地存储

    这是文档处理的主入口方法。根据文档类型调用相应的处理函数，
    然后保存元数据和提取的文本到本地文件系统。

    参数：
        file_path (str): 文档文件路径
        document_type (DocumentType, optional): 文档类型，如为 None 则自动检测
        arxiv_id (str, optional): arXiv 论文 ID（如果是 arXiv 论文）

    返回：
        Document: 文档对象，包含 ID、标题、路径等信息

    处理流程：
        1. 根据文件类型选择相应的处理方法
           - PDF → process_pdf()
           - DOCX → process_docx()
           - PPTX → process_pptx()
           - EPUB → process_epub()
           - TXT/MD → process_text_file()
           - arXiv → process_arxiv()

        2. 生成文档 ID（使用文件哈希的前 16 位）

        3. 创建 Document 对象

        4. 保存元数据到 {doc_id}.json

        5. 保存提取的文本到 {doc_id}_text.txt

        6. 返回 Document 对象

    存储位置：
        - metadata/{doc_id}.json: 完整的文档元数据
        - metadata/{doc_id}_text.txt: 提取的纯文本

    文档 ID 生成：
        使用 MD5 哈希的前 16 位作为文档 ID，确保：
        - 唯一性：相同文件生成相同 ID
        - 可读性：16 字符长度适中
        - 避免冲突：MD5 哈希碰撞概率极低

    示例：
        # 自动检测类型
        doc = processor.save_document("paper.pdf")

        # 指定类型
        doc = processor.save_document(
            "paper.pdf",
            document_type=DocumentType.PDF
        )

        # arXiv 论文
        doc = processor.save_document(
            "",
            arxiv_id="2301.12345"
        )

        print(doc.id)      # "a1b2c3d4e5f6g7h8"
        print(doc.title)   # "Deep Learning Survey"
    """
    # 1. 根据类型选择处理方法
    if arxiv_id:
        # arXiv 论文特殊处理
        result = self.process_arxiv(arxiv_id)
        file_path = result["file_path"]
        document_type = DocumentType.ARXIV
    else:
        # 自动检测文档类型（如果未指定）
        if document_type is None:
            document_type = get_document_type(file_path)
            if document_type is None:
                raise ValueError(f"Unsupported file type: {file_path}")

        # 根据类型调用相应的处理方法
        if document_type == DocumentType.PDF:
            result = self.process_pdf(file_path)
        elif document_type == DocumentType.DOCX:
            result = self.process_docx(file_path)
        elif document_type == DocumentType.PPTX:
            result = self.process_pptx(file_path)
        elif document_type == DocumentType.EPUB:
            result = self.process_epub(file_path)
        else:  # TXT, MD
            result = self.process_text_file(file_path)

    # 2. 生成文档 ID（文件哈希的前 16 位）
    file_hash = get_file_hash(file_path)
    doc_id = file_hash[:16]

    # 3. 创建 Document 对象
    document = Document(
        id=doc_id,
        title=result["title"],
        file_path=file_path,
        document_type=document_type,
        file_size=get_file_size(file_path),
        num_pages=result.get("num_pages"),
    )

    # 4. 保存元数据到 JSON 文件
    metadata_file = self.metadata_dir / f"{doc_id}.json"
    metadata = {
        **document.model_dump(mode='json'),  # Document 对象转字典
        "extracted_metadata": result.get("metadata", {}),  # 文档原始元数据
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

    # 5. 保存提取的文本到 TXT 文件
    text_file = self.metadata_dir / f"{doc_id}_text.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(result["text"])

    logger.info(f"Saved document {doc_id}: {document.title}")
    return document
```

---

## 2. RAGEngine - RAG 引擎

**文件**: `backend/core/rag_engine.py`

### 模块说明

```python
"""
RAG (Retrieval-Augmented Generation) 引擎

RAG 是一种结合检索和生成的技术，通过以下步骤提供准确的问答：
1. 检索 (Retrieval): 从向量数据库中找到相关文档片段
2. 增强 (Augmentation): 将检索结果作为上下文
3. 生成 (Generation): 使用 LLM 基于上下文生成答案

核心组件：
- ChromaDB: 向量数据库，存储文档嵌入
- Embeddings: 将文本转换为向量
- LLM: 大语言模型，生成最终答案

工作流程：
用户提问
  → 问题向量化
  → 检索相似文档 (Top-K)
  → 构建 Prompt (上下文 + 问题)
  → LLM 生成答案
  → 返回答案 + 来源

优势：
✅ 答案基于实际文档内容
✅ 可追溯来源
✅ 减少 AI 幻觉
✅ 上下文相关性高
"""
```

### 类定义

```python
class RAGEngine:
    """
    RAG 引擎类

    职责：
    1. 管理向量数据库 (ChromaDB)
    2. 文档向量化和存储
    3. 语义搜索（基于向量相似度）
    4. 问答生成（RAG）

    属性：
        vectorstore_path (Path): 向量数据库存储路径
        embeddings: 嵌入模型（OpenAI 或 Ollama）
        client: ChromaDB 客户端
        vectorstore: Chroma 向量存储
        text_splitter: 文本分块器

    配置参数（来自 settings）：
        - chunk_size: 文档分块大小（默认 1000 字符）
        - chunk_overlap: 分块重叠大小（默认 200 字符）
        - top_k_results: 检索结果数量（默认 5）

    使用示例：
        rag = RAGEngine()

        # 添加文档
        rag.add_document(
            doc_id="abc123",
            text="文档内容...",
            metadata={"title": "论文标题"}
        )

        # 语义搜索
        results = rag.search("深度学习", top_k=5)

        # 问答
        query = Query(question="什么是深度学习？")
        response = rag.query(query)
        print(response.answer)
    """
```

### 核心方法注释

#### add_document() - 添加文档到向量库

```python
def add_document(
    self,
    doc_id: str,
    text: str,
    metadata: Optional[Dict] = None
) -> int:
    """
    将文档添加到向量数据库

    步骤：
    1. 文本分块（Chunking）
       - 使用 RecursiveCharacterTextSplitter
       - 分块大小：1000 字符
       - 重叠大小：200 字符（保持上下文连贯）

    2. 创建 LangChain Document 对象
       - 每个分块是一个 Document
       - 附加元数据：doc_id, chunk_id, 标题等

    3. 向量化并存储
       - 使用 Embeddings 模型转换为向量
       - 存储到 ChromaDB

    参数：
        doc_id (str): 文档唯一 ID
        text (str): 文档全文
        metadata (Dict, optional): 额外的元数据
            - title: 文档标题
            - category: 分类
            - tags: 标签列表

    返回：
        int: 生成的文档分块数量

    为什么要分块？
    - LLM 有 token 限制
    - 提高检索精度（更细粒度的匹配）
    - 更好的上下文相关性

    为什么要重叠？
    - 避免重要信息被截断
    - 保持上下文连贯性
    - 提高检索召回率

    示例：
        num_chunks = rag.add_document(
            doc_id="abc123",
            text="长文档内容...",  # 5000 字符
            metadata={"title": "深度学习综述", "category": "machine_learning"}
        )
        print(num_chunks)  # 5 (5000 / 1000 = 5 个分块)
    """
    # 1. 文本分块
    chunks = self.text_splitter.split_text(text)

    # 2. 创建 Document 对象（LangChain 格式）
    documents = []
    for i, chunk in enumerate(chunks):
        # 为每个分块创建一个 Document
        doc_metadata = {
            "doc_id": doc_id,      # 原始文档 ID
            "chunk_id": i,         # 分块序号
            "total_chunks": len(chunks),  # 总分块数
        }

        # 合并用户提供的元数据
        if metadata:
            doc_metadata.update(metadata)

        documents.append(
            LangchainDocument(
                page_content=chunk,     # 分块文本
                metadata=doc_metadata   # 元数据
            )
        )

    # 3. 向量化并存储到 ChromaDB
    self.vectorstore.add_documents(documents)

    logger.info(f"Added document {doc_id} with {len(chunks)} chunks")
    return len(chunks)
```

#### search() - 语义搜索

```python
def search(
    self,
    query: str,
    top_k: int = 5,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    基于向量相似度的语义搜索

    与传统关键词搜索的区别：
    - 关键词搜索：精确匹配单词
    - 语义搜索：理解查询的含义，找到语义相似的内容

    工作原理：
    1. 查询向量化
       - 将用户查询转换为向量（使用同样的 Embeddings 模型）

    2. 相似度计算
       - 计算查询向量与所有文档向量的余弦相似度
       - ChromaDB 使用高效的近似最近邻（ANN）算法

    3. Top-K 检索
       - 返回相似度最高的 K 个文档片段
       - 可选：按类别过滤

    参数：
        query (str): 用户查询文本
        top_k (int): 返回结果数量（默认 5）
        category (str, optional): 按类别过滤

    返回：
        List[Dict]: 检索结果列表，每个结果包含：
            - content (str): 文档片段文本
            - metadata (dict): 元数据（doc_id, title, category等）
            - score (float): 相似度分数（0-1，越高越相关）

    示例：
        # 基础搜索
        results = rag.search("深度学习优化算法", top_k=5)

        # 分类过滤
        results = rag.search(
            "卷积神经网络",
            top_k=3,
            category="machine_learning"
        )

        for result in results:
            print(f"相似度: {result['score']:.2f}")
            print(f"内容: {result['content'][:100]}...")
            print(f"来源: {result['metadata']['title']}")
    """
    # 构建过滤条件
    filter_dict = {"category": category} if category else None

    # 执行向量相似度搜索
    # ChromaDB 会自动：
    # 1. 将 query 转换为向量
    # 2. 计算与所有文档的相似度
    # 3. 返回 Top-K 结果
    search_results = self.vectorstore.similarity_search_with_score(
        query=query,
        k=top_k,
        filter=filter_dict
    )

    # 格式化结果
    results = []
    for doc, score in search_results:
        results.append({
            "content": doc.page_content,  # 文档片段内容
            "metadata": doc.metadata,     # 元数据
            "score": score               # 相似度分数
        })

    return results
```

#### query() - RAG 问答

```python
def query(self, query: Query, language: str = "en") -> QueryResponse:
    """
    基于 RAG 的问答

    这是 RAG 引擎的核心功能，结合检索和生成提供准确的答案。

    RAG 三步走：
    1. Retrieval (检索)
       - 使用语义搜索找到相关文档片段
       - Top-K 个最相关的段落

    2. Augmentation (增强)
       - 将检索到的段落作为上下文
       - 构建包含上下文的 Prompt

    3. Generation (生成)
       - LLM 基于上下文生成答案
       - 如果上下文中没有答案，明确说明

    参数：
        query (Query): 查询对象
            - question (str): 用户问题
            - document_ids (List[str], optional): 限定文档范围
            - category (str, optional): 限定类别
            - top_k (int): 检索数量
        language (str): 输出语言（"en" 或 "zh"）

    返回：
        QueryResponse: 包含
            - answer (str): 生成的答案
            - sources (List[Dict]): 答案来源（可追溯）
            - confidence (float, optional): 置信度

    Prompt 结构：
        ```
        你是一个学术助手。基于以下上下文回答问题。
        如果上下文中没有答案，说"我在提供的文档中找不到这个信息"。

        上下文:
        {检索到的段落1}
        {检索到的段落2}
        ...

        问题: {用户问题}

        答案:
        ```

    为什么 RAG 更准确？
    - ✅ 基于实际文档内容，不是"编造"
    - ✅ 可以引用来源，增加可信度
    - ✅ 减少幻觉（hallucination）
    - ✅ 答案更新及时（基于最新文档）

    示例：
        query = Query(
            question="作者使用了什么数据集？",
            category="machine_learning",
            top_k=3
        )

        response = rag.query(query, language="zh")

        print("答案:", response.answer)
        # "作者使用了 ImageNet 和 COCO 数据集进行实验。"

        print("\n来源:")
        for i, source in enumerate(response.sources, 1):
            print(f"{i}. {source['metadata']['title']}")
            print(f"   {source['content'][:100]}...")
    """
    # 1. Retrieval - 检索相关文档
    search_results = self.search(
        query=query.question,
        top_k=query.top_k,
        category=query.category
    )

    # 如果没有找到相关文档
    if not search_results:
        return QueryResponse(
            answer="我没有找到相关的文档来回答这个问题。",
            sources=[]
        )

    # 2. Augmentation - 构建上下文
    # 将所有检索到的段落拼接
    context = "\n\n".join([
        f"[文档片段 {i+1}]\n{result['content']}"
        for i, result in enumerate(search_results)
    ])

    # 3. Generation - 生成答案
    # 使用预定义的 QA_PROMPT 模板
    llm = get_llm()
    answer = llm.predict(
        QA_PROMPT.format(
            context=context,      # 检索到的上下文
            question=query.question  # 用户问题
        )
    )

    # 返回答案和来源
    return QueryResponse(
        answer=answer,
        sources=search_results  # 保留来源信息，便于用户验证
    )
```

---

## 3. Summarizer - 摘要生成器

**文件**: `backend/core/summarizer.py`

### 核心方法注释

#### generate_summary() - 生成摘要

```python
def generate_summary(self, doc_id: str, language: str = "en") -> str:
    """
    生成论文摘要（250-500 字）

    摘要内容包括：
    - 主要贡献
    - 方法论概述
    - 关键发现和结论

    参数：
        doc_id (str): 文档 ID
        language (str): 输出语言
            - "en": English
            - "zh": 中文

    返回：
        str: 生成的摘要文本

    实现：
    1. 获取文档全文
    2. 截断文本（避免超过 LLM token 限制）
    3. 使用 SUMMARY_PROMPT 模板
    4. LLM 生成摘要

    Token 管理：
    - 最大输入：8000 tokens (~32,000 字符)
    - 如果文档超长，只使用前面部分
    - 未来可优化：使用 Map-Reduce 策略处理长文档

    示例：
        summary = summarizer.generate_summary(
            doc_id="abc123",
            language="zh"
        )

        print(summary)
        # 本文提出了一种新的深度学习优化算法 AdamW。
        # 主要贡献包括...（250-500字摘要）
    """
```

#### extract_key_points() - 提取关键点

```python
def extract_key_points(
    self,
    doc_id: str,
    language: str = "en"
) -> List[str]:
    """
    提取论文的关键点（5-10 个）

    关键点类型：
    - 主要创新点
    - 重要发现
    - 方法论亮点
    - 实用价值

    参数：
        doc_id (str): 文档 ID
        language (str): 输出语言

    返回：
        List[str]: 关键点列表

    输出格式：
    [
        "提出了 AdamW 优化器，解耦权重衰减",
        "在 CIFAR-10 上超越 SGD 和 Adam",
        "理论分析证明收敛性",
        ...
    ]

    示例：
        key_points = summarizer.extract_key_points(
            doc_id="abc123",
            language="zh"
        )

        for i, point in enumerate(key_points, 1):
            print(f"{i}. {point}")
    """
```

---

## 4. Classifier - 分类器

**文件**: `backend/core/classifier.py`

### 核心方法注释

#### classify_document() - 文档分类

```python
def classify_document(self, doc_id: str) -> ClassificationResult:
    """
    自动分类文档并提取标签

    分类体系：
    - machine_learning: 机器学习
    - cryptography: 密码学
    - other: 其他

    标签提取：
    - 技术标签：CNN, RNN, Transformer, RSA, AES 等
    - 任务标签：Classification, Detection, Encryption 等
    - 领域标签：Computer Vision, NLP, Security 等

    工作流程：
    1. 获取文档文本（前 3000 字符）
    2. 使用 CLASSIFICATION_PROMPT
    3. LLM 返回 JSON 格式结果
    4. 标签富化：添加预定义的相关标签
    5. 保存分类结果到元数据

    参数：
        doc_id (str): 文档 ID

    返回：
        ClassificationResult:
            - category (Category): 分类类别
            - tags (List[str]): 标签列表（3-10个）
            - confidence (float): 分类置信度（0-1）

    标签富化规则：
    ```python
    TOPIC_TAGS = {
        "machine_learning": [
            "CNN", "RNN", "LSTM", "Transformer",
            "GAN", "VAE", "ResNet", "BERT", ...
        ],
        "cryptography": [
            "RSA", "AES", "DES", "SHA", "MD5",
            "SSL/TLS", "Public Key", ...
        ]
    }
    ```

    示例：
        result = classifier.classify_document("abc123")

        print(result.category)     # "machine_learning"
        print(result.tags)         # ["CNN", "Image Classification", "ResNet"]
        print(result.confidence)   # 0.95
    """
```

---

## 5. LLM Utils - LLM 工具

**文件**: `backend/utils/llm_utils.py`

### 核心函数注释

#### check_ollama_connection() - Ollama 连接检查

```python
def check_ollama_connection(base_url: str, timeout: int = 5) -> bool:
    """
    检查 Ollama 服务是否可访问

    为什么需要这个检查？
    - Ollama 是本地服务，可能未启动
    - 避免应用崩溃，提供友好错误提示
    - 5秒超时，快速失败

    检查方法：
    - 请求 /api/tags 端点
    - 返回 200 表示服务正常

    参数：
        base_url (str): Ollama 服务地址
            默认: http://localhost:11434
        timeout (int): 超时时间（秒）

    返回：
        bool: True = 可访问, False = 不可访问

    示例：
        if check_ollama_connection("http://localhost:11434"):
            print("Ollama 服务正常")
        else:
            print("请启动 Ollama: ollama serve")
    """
```

#### get_llm() - 获取 LLM 实例

```python
def get_llm(...) -> Union[ChatOpenAI, Ollama]:
    """
    获取配置的 LLM 实例（支持 OpenAI 和 Ollama）

    根据 settings.llm_provider 选择提供商：
    - "openai": 使用 OpenAI API（需要 API Key）
    - "ollama": 使用本地 Ollama 服务（免费）

    参数：
        temperature (float): 生成温度（0-2）
            - 0: 最确定，输出一致
            - 0.7: 平衡创造性和一致性（推荐）
            - 2: 最随机，更有创造性

        model (str, optional): 模型名称
            OpenAI: gpt-4-turbo-preview, gpt-3.5-turbo
            Ollama: llama2, mistral, codellama

        max_tokens (int, optional): 最大生成 token 数

    返回：
        ChatOpenAI 或 Ollama 实例

    异常：
        ConnectionError: Ollama 服务不可用
        ValueError: OpenAI API Key 未设置

    配置示例（.env）：
        # 使用 OpenAI
        LLM_PROVIDER=openai
        OPENAI_API_KEY=sk-...

        # 使用 Ollama
        LLM_PROVIDER=ollama
        OLLAMA_MODEL=llama2

    使用示例：
        llm = get_llm(temperature=0.7)
        response = llm.predict("解释什么是 RAG")
    """
```

---

## 6. Authentication - 认证模块

**文件**: `frontend/auth.py`

### 核心函数注释

#### hash_password() - 密码哈希

```python
def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """
    使用 PBKDF2 算法对密码进行安全哈希

    为什么使用 PBKDF2？
    - ✅ 行业标准（NIST 推荐）
    - ✅ 抗彩虹表攻击（使用盐值）
    - ✅ 抗暴力破解（100,000 次迭代）
    - ✅ 慢速算法，增加破解难度

    与简单 SHA-256 的对比：
    - SHA-256: 一次计算，快速，易被破解
    - PBKDF2: 100,000 次迭代，慢速，安全

    参数：
        password (str): 明文密码
        salt (str, optional): 盐值
            - 如为 None，自动生成 64 字符随机盐

    返回：
        Tuple[str, str]: (密码哈希, 盐值)

    盐值的作用：
    - 相同密码 + 不同盐 = 不同哈希
    - 防止彩虹表攻击
    - 每个用户独立的盐值

    PBKDF2 参数：
    - hash_name: sha256
    - iterations: 100,000（OWASP 推荐）
    - salt_length: 32 字节（64 字符 hex）

    示例：
        # 生成新密码哈希
        hash_val, salt = hash_password("MyPassword123")
        print(hash_val)  # "a1b2c3d4..."（128字符）
        print(salt)      # "e5f6g7h8..."（64字符）

        # 验证密码（使用相同盐值）
        new_hash, _ = hash_password("MyPassword123", salt)
        assert new_hash == hash_val  # 验证成功
    """
```

#### verify_password() - 密码验证

```python
def verify_password(
    password: str,
    stored_hash: str,
    salt: str
) -> bool:
    """
    验证密码是否正确

    验证流程：
    1. 使用相同的盐值对输入密码进行哈希
    2. 比较计算的哈希与存储的哈希
    3. 使用恒定时间比较（防止时序攻击）

    参数：
        password (str): 用户输入的密码
        stored_hash (str): 数据库中存储的哈希
        salt (str): 盐值

    返回：
        bool: True = 密码正确, False = 密码错误

    安全性：
    - ✅ 恒定时间比较（== 运算符在 Python 中是恒定时间）
    - ✅ 防止时序攻击（timing attack）
    - ✅ 不泄露任何密码信息

    示例：
        # 存储的密码信息
        stored_hash = "a1b2c3d4..."
        stored_salt = "e5f6g7h8..."

        # 验证用户登录
        if verify_password("MyPassword123", stored_hash, stored_salt):
            print("登录成功")
        else:
            print("密码错误")
    """
```

---

## 总结

本文档为 AI 论文管理助手的核心模块提供了详细的中文注释。每个函数和类都包含：

1. **功能说明**：这个代码做什么
2. **参数说明**：每个参数的含义和类型
3. **返回值说明**：返回什么数据
4. **实现细节**：内部如何工作
5. **使用示例**：如何调用这个函数
6. **注意事项**：需要注意的地方

这些注释帮助开发者：
- 📖 快速理解代码功能
- 🔧 正确使用 API
- 🐛 更容易调试问题
- 🚀 加速新功能开发

如需查看完整代码，请参考相应的源文件。

---

**文档维护者**: AI Paper Management Team
**最后更新**: 2025-01-17
**版本**: v0.3.0
