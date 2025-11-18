# AI 论文管理助手 - 完整指南

> **版本**: v0.3.0
> **最后更新**: 2025-01-17
> **文档类型**: 完整使用和部署指南

---

## 📑 目录

1. [系统概述](#1-系统概述)
2. [快速开始](#2-快速开始)
3. [详细配置指南](#3-详细配置指南)
4. [功能使用手册](#4-功能使用手册)
5. [API 参考](#5-api-参考)
6. [故障排除](#6-故障排除)
7. [开发指南](#7-开发指南)
8. [性能优化](#8-性能优化)

---

## 1. 系统概述

### 1.1 项目简介

AI 论文管理助手是一个基于 **RAG (Retrieval-Augmented Generation)** 架构的智能学术资料管理系统，专为学生和研究人员设计。

**核心特性：**
- 🤖 智能论文摘要和关键点提取
- 📚 自动分类和知识图谱可视化
- 🗺️ 个性化学习路径生成
- 📝 考试复习工具（闪卡、速记表、对比表）
- 🔍 语义搜索和智能问答
- 🌐 多语言界面支持（中英文）
- 🦙 本地 LLM 支持（Ollama）
- 🔐 用户认证和权限管理

### 1.2 技术栈

**后端框架：**
- Python 3.9+
- LangChain 0.1.0 - LLM 应用框架
- ChromaDB 0.4.22 - 向量数据库
- OpenAI API / Ollama - 大语言模型

**前端框架：**
- Streamlit 1.29.0 - Web 界面
- Plotly 5.18.0 - 数据可视化
- NetworkX 3.2.1 - 图形算法

**文档处理：**
- PyMuPDF (fitz) - PDF 处理
- python-docx - Word 文档
- python-pptx - PowerPoint
- ebooklib - EPUB 电子书
- arxiv - arXiv 论文下载

**数据处理：**
- NumPy, Pandas - 数据分析
- BeautifulSoup4 - HTML 解析
- sentence-transformers - 文本嵌入

### 1.3 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                      │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │论文总结  │资料管理  │学习路线  │考试复习  │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐              ┌──────▼──────┐
│  Backend Core  │              │   Utilities  │
│ ┌────────────┐ │              │ ┌──────────┐ │
│ │DocumentProc│ │              │ │LLM Utils │ │
│ │Summarizer  │ │◄─────────────┤ │File Utils│ │
│ │Classifier  │ │              │ │i18n      │ │
│ │RAG Engine  │ │              │ │Auth      │ │
│ │LearningPath│ │              │ └──────────┘ │
│ └────────────┘ │              └─────────────┘
└───────┬────────┘
        │
┌───────▼────────────────────────┐
│    Data Storage Layer          │
│ ┌──────────┬─────────────────┐ │
│ │ChromaDB  │ Documents/      │ │
│ │(Vectors) │ Metadata (JSON) │ │
│ └──────────┴─────────────────┘ │
└────────────────────────────────┘
        │
┌───────▼────────┐
│  LLM Provider  │
│ ┌────┬─────┐   │
│ │OpenAI│Ollama│  │
│ └────┴─────┘   │
└────────────────┘
```

### 1.4 数据流

**文档上传流程：**
```
用户上传文档
    ↓
DocumentProcessor 提取文本
    ↓
Classifier 自动分类和打标签
    ↓
文本分块 (Chunk Size: 1000, Overlap: 200)
    ↓
生成向量嵌入 (Embeddings)
    ↓
存储到 ChromaDB
    ↓
保存元数据到 JSON
```

**问答流程 (RAG)：**
```
用户提问
    ↓
生成问题向量
    ↓
向量相似度搜索 (Top-K)
    ↓
检索相关文档片段
    ↓
构建 Prompt (上下文 + 问题)
    ↓
LLM 生成答案
    ↓
返回答案 + 来源
```

---

## 2. 快速开始

### 2.1 环境要求

- **Python**: 3.9 或更高版本
- **操作系统**: Windows, macOS, Linux
- **内存**: 建议 8GB+
- **磁盘**: 至少 2GB 可用空间

### 2.2 安装步骤

#### Step 1: 克隆仓库

```bash
git clone https://github.com/yourusername/PaperManagement.git
cd PaperManagement
```

#### Step 2: 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: 安装依赖

```bash
pip install -r requirements.txt
```

#### Step 4: 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件
# 至少需要设置 OPENAI_API_KEY 或配置 Ollama
```

#### Step 5: 启动应用

```bash
streamlit run frontend/app.py
```

应用将在浏览器中自动打开：http://localhost:8501

### 2.3 5分钟快速体验

1. **上传文档**：进入"📄 论文总结"页面，上传一个 PDF 文件
2. **自动分析**：系统自动提取文本、分类、生成标签
3. **生成摘要**：在"文档分析"标签下选择文档，生成摘要
4. **智能问答**：在"智能问答"标签下提问，获取精准答案
5. **浏览管理**：进入"📚 资料管理"查看知识图谱

---

## 3. 详细配置指南

### 3.1 环境变量配置 (.env)

#### 3.1.1 基础配置

```bash
# ===== LLM 提供商选择 =====
# 可选值: "openai" 或 "ollama"
LLM_PROVIDER=openai
```

#### 3.1.2 OpenAI 配置（默认）

```bash
# OpenAI API Key (必填)
OPENAI_API_KEY=sk-your-api-key-here

# 可选：自定义 API 端点
OPENAI_API_BASE=https://api.openai.com/v1

# 嵌入模型
EMBEDDING_MODEL=text-embedding-3-small

# LLM 模型
LLM_MODEL=gpt-4-turbo-preview
```

**获取 API Key：**
1. 访问 https://platform.openai.com/api-keys
2. 点击 "Create new secret key"
3. 复制密钥到 `.env` 文件

#### 3.1.3 Ollama 配置（本地 LLM）

```bash
# 启用 Ollama
LLM_PROVIDER=ollama

# Ollama 服务地址
OLLAMA_BASE_URL=http://localhost:11434

# Ollama 模型名称
OLLAMA_MODEL=llama2

# Ollama 嵌入模型
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

**Ollama 安装和配置：**

```bash
# 1. 安装 Ollama
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: 访问 ollama.com 下载

# 2. 下载模型
ollama pull llama2
ollama pull nomic-embed-text

# 3. 验证安装
ollama list

# 4. 启动 Ollama (通常自动启动)
ollama serve
```

**推荐模型：**
- **通用**: llama2 (7B), llama3 (8B)
- **编程**: codellama (7B)
- **高性能**: mixtral (8x7B)
- **轻量级**: phi (2.7B), gemma (2B)

#### 3.1.4 存储路径配置

```bash
# 向量数据库路径
VECTOR_DB_PATH=./data/vectorstore

# 文档存储路径
DOCUMENT_PATH=./data/documents

# 元数据存储路径
METADATA_PATH=./data/metadata
```

#### 3.1.5 高级参数

```bash
# RAG 参数
CHUNK_SIZE=1000              # 文档分块大小
CHUNK_OVERLAP=200            # 分块重叠大小
TOP_K_RESULTS=5              # 检索返回结果数

# LLM 参数
TEMPERATURE=0.7              # 生成温度 (0-1)
MAX_TOKENS=2000              # 最大生成 token 数

# 应用设置
MAX_FILE_SIZE_MB=50          # 最大文件大小
SUPPORTED_LANGUAGES=en,zh    # 支持的语言
```

### 3.2 用户认证配置

#### 3.2.1 默认账户

系统首次运行时会自动创建 `config/users.yaml`：

```yaml
credentials:
  usernames:
    admin:
      name: "Administrator"
      password: "<SHA256-hash>"
      role: "admin"
    demo:
      name: "Demo User"
      password: "<SHA256-hash>"
      role: "user"

cookie:
  name: "ai_paper_management"
  key: "random_signature_key_123"
  expiry_days: 30
```

**默认登录信息：**
- 管理员: `admin` / `admin123`
- 普通用户: `demo` / `demo123`

#### 3.2.2 添加新用户

```python
# 生成密码哈希
import hashlib
password = "your_password"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)
```

然后编辑 `config/users.yaml`：

```yaml
credentials:
  usernames:
    newuser:
      name: "New User Name"
      password: "<your-generated-hash>"
      role: "user"  # 或 "admin"
```

#### 3.2.3 修改默认密码

⚠️ **生产环境必须修改默认密码！**

```bash
# 1. 生成新密码哈希
python -c "import hashlib; print(hashlib.sha256('new_password'.encode()).hexdigest())"

# 2. 更新 config/users.yaml 中的 password 字段

# 3. 重启应用
```

#### 3.2.4 Cookie 配置

```yaml
cookie:
  name: "ai_paper_management"  # Cookie 名称
  key: "random_signature_key_123"  # 签名密钥（建议修改）
  expiry_days: 30  # 过期天数
```

**安全建议：**
- 生成随机的 `key`：`python -c "import secrets; print(secrets.token_hex(32))"`
- 在 HTTPS 环境下使用
- 定期更新密钥

---

## 4. 功能使用手册

### 4.1 文档管理

#### 4.1.1 支持的文档格式

| 格式 | 扩展名 | 支持功能 | 备注 |
|------|--------|----------|------|
| PDF | `.pdf` | ✅ 文本、元数据 | 使用 PyMuPDF |
| Word | `.docx` | ✅ 段落、表格 | Office 2007+ |
| PowerPoint | `.pptx` | ✅ 幻灯片文本 | Office 2007+ |
| EPUB | `.epub` | ✅ 电子书内容 | HTML 解析 |
| 纯文本 | `.txt` | ✅ 全文 | UTF-8 编码 |
| Markdown | `.md` | ✅ 全文 | UTF-8 编码 |
| arXiv | arXiv ID | ✅ 自动下载 | 需要网络连接 |

#### 4.1.2 上传文档

**方式一：本地文件上传**

```
1. 进入"📄 论文总结"页面
2. 选择"上传本地文件"
3. 点击"Browse files"选择文件（支持多选）
4. 点击"处理文档"按钮
5. 等待处理完成（显示进度条）
```

**方式二：arXiv 导入**

```
1. 进入"📄 论文总结"页面
2. 选择"从 arXiv 导入"
3. 输入 arXiv ID (例如: 2301.12345)
4. 点击"导入论文"
5. 系统自动下载并处理
```

**自动化处理流程：**
- ✅ 文本提取
- ✅ 元数据解析（作者、标题、日期等）
- ✅ 自动分类（机器学习/密码学/其他）
- ✅ 标签生成（CNN, RNN, RSA 等）
- ✅ 向量化存储（用于语义搜索）

#### 4.1.3 文档浏览和管理

**浏览文档：**

```
进入"📚 资料管理" → "文档浏览"
- 查看所有已上传文档
- 按分类筛选
- 搜索标题
- 删除文档
```

**文档详情显示：**
- 📄 文档 ID（前8位）
- 📝 标题
- 🏷️ 分类
- 🔖 标签（最多5个）
- 📅 上传日期
- 📊 页数（如有）

#### 4.1.4 语义搜索

```
进入"📚 资料管理" → "语义搜索"

1. 输入搜索查询（自然语言）
   例如: "深度学习优化算法"

2. 选择返回结果数量 (1-10)

3. 点击"搜索"

4. 查看相关文档片段
   - 显示相关度评分
   - 高亮匹配内容
   - 显示来源文档
```

**搜索技巧：**
- ✅ 使用完整句子（效果更好）
- ✅ 包含关键术语
- ❌ 避免单个关键词
- ❌ 避免过于宽泛的查询

#### 4.1.5 知识图谱

```
进入"📚 资料管理" → "知识图谱"

点击"生成知识图谱"
- 查看分类节点
- 查看标签节点
- 查看文档节点
- 交互式可视化（可缩放、拖动）
```

**图谱说明：**
- 🔵 蓝色节点 = 分类
- 🟢 绿色节点 = 标签
- 🟡 黄色节点 = 文档
- 线条 = 关联关系

### 4.2 论文分析

#### 4.2.1 生成摘要

```
进入"📄 论文总结" → "文档分析"

1. 选择文档（下拉菜单）
2. 选择输出语言（中文/英文）
3. 勾选"摘要"
4. 点击"开始分析"

生成内容：
- 250-500 字精炼摘要
- 涵盖主要贡献、方法论、结论
```

**摘要示例：**
```
本文提出了一种新的深度学习优化算法 AdamW，
通过解耦权重衰减和梯度更新，有效改善了
Adam 优化器在训练深度网络时的泛化性能...
```

#### 4.2.2 提取关键点

```
1. 选择文档
2. 勾选"关键点"
3. 点击"开始分析"

生成内容：
- 5-10 个要点列表
- 包含创新点、发现、应用
```

**关键点示例：**
```
1. 提出 AdamW 优化器，解耦权重衰减
2. 在 CIFAR-10 上超越 SGD 和 Adam
3. 改进学习率调度策略
4. 理论分析收敛性保证
5. 开源实现可直接使用
```

#### 4.2.3 完整分析

```
1. 选择文档
2. 勾选"完整分析"
3. 点击"开始分析"

生成内容：
- 📊 方法论详述
- 🎯 主要贡献列表
- 📝 结论总结
- 📦 使用的数据集
```

### 4.3 智能问答 (RAG)

#### 4.3.1 提问

```
进入"📄 论文总结" → "智能问答"

1. 可选：选择分类筛选
2. 设置检索文档数量 (Top-K)
3. 输入问题
4. 点击"提问"

示例问题：
- "作者使用了什么数据集？"
- "这篇论文的主要创新点是什么？"
- "实验结果如何？"
- "有哪些局限性？"
```

#### 4.3.2 查看答案和来源

```
答案显示：
💡 答案
[AI 生成的详细回答]

📚 查看来源 (可展开)
来源 1:
[相关文档片段 1]
文档: [文档名称]

来源 2:
[相关文档片段 2]
文档: [文档名称]
```

**RAG 优势：**
- ✅ 答案基于实际文档内容
- ✅ 可追溯来源
- ✅ 减少 AI 幻觉
- ✅ 上下文相关性高

### 4.4 学习路径生成

#### 4.4.1 设定学习目标

```
进入"🗺️ 学习路线" → "设定学习目标"

1. 输入学习目标描述
   例如: "掌握深度学习的基础知识"

2. 选择学习领域
   - 机器学习
   - 密码学
   - 自动检测

3. 勾选"使用我的文档库"（可选）

4. 点击"生成学习路径"
```

#### 4.4.2 查看学习路径

```
生成的学习路径包含：
- 🎯 学习目标
- ⏱️ 预计总时间
- 📋 分步骤学习节点

每个节点包含：
- 标题和描述
- 前置要求
- 推荐资源（来自您的库）
- 预计学习时间
```

#### 4.4.3 导出学习计划

```
点击"导出学习计划"按钮

下载 Markdown 格式文件：
learning_path_YYYYMMDD_HHMMSS.md

可导入到：
- Notion
- Obsidian
- Markdown 编辑器
```

#### 4.4.4 前置知识查询

```
在"前置知识查询"部分：

1. 输入主题
   例如: "卷积神经网络"

2. 点击"查询前置知识"

3. 查看需要掌握的基础知识
```

### 4.5 考试复习

#### 4.5.1 生成闪卡 (Flashcards)

```
进入"📝 考试复习" → "闪卡"

1. 输入主题
   例如: "机器学习基础"

2. 选择闪卡数量 (5-20张)

3. 点击"生成闪卡"

闪卡内容：
- 正面：问题
- 反面：答案（点击显示/隐藏）
- 导航：上一张/下一张
```

**闪卡示例：**
```
问题: 什么是过拟合？
答案: 过拟合是指模型在训练数据上表现很好，
     但在测试数据上表现较差的现象...
```

#### 4.5.2 生成速记表 (Cheat Sheet)

```
1. 输入主题
2. 点击"生成速记表"

速记表内容：
- 📝 关键定义
- 📐 重要公式
- 🔧 核心算法
- 📊 快速参考表
```

#### 4.5.3 概念对比

```
1. 输入要对比的概念（逗号分隔）
   例如: "SVM, 决策树, 神经网络"

2. 点击"生成对比"

对比表内容：
- 相似点
- 差异点
- 使用场景
- 优缺点
```

#### 4.5.4 练习题生成

```
1. 输入主题
2. 选择题目数量
3. 点击"生成练习题"

练习题类型：
- 选择题
- 简答题
- 应用题
```

### 4.6 多语言切换

#### 4.6.1 切换界面语言

```
1. 在侧边栏找到"语言 / Language"选择器
2. 选择：
   - 🇨🇳 中文
   - 🇬🇧 English
3. 页面自动刷新并应用新语言
```

**支持范围：**
- ✅ 所有 UI 文本
- ✅ 菜单和按钮
- ✅ 提示消息
- ✅ 错误信息
- ⚠️ 文档内容保持原始语言

#### 4.6.2 扩展其他语言

编辑 `frontend/i18n.py`：

```python
TRANSLATIONS = {
    "zh": { ... },
    "en": { ... },
    "ja": {  # 添加日语
        "app_title": "AI論文管理アシスタント",
        # ... 更多翻译
    }
}
```

---

## 5. API 参考

### 5.1 核心类和方法

#### 5.1.1 DocumentProcessor

**文件**: `backend/core/document_processor.py`

```python
from backend.core.document_processor import DocumentProcessor

processor = DocumentProcessor()

# 处理 PDF
result = processor.process_pdf("/path/to/file.pdf")
# 返回: {"text": str, "num_pages": int, "metadata": dict, "title": str}

# 处理 DOCX
result = processor.process_docx("/path/to/file.docx")

# 处理 PPTX
result = processor.process_pptx("/path/to/file.pptx")

# 处理 EPUB
result = processor.process_epub("/path/to/file.epub")

# 处理 arXiv
result = processor.process_arxiv("2301.12345")

# 保存文档
doc = processor.save_document("/path/to/file.pdf")
# 返回: Document 对象

# 获取文档文本
text = processor.get_document_text(doc_id)

# 获取文档元数据
metadata = processor.get_document_metadata(doc_id)

# 列出所有文档
docs = processor.list_documents()

# 删除文档
success = processor.delete_document(doc_id)
```

#### 5.1.2 RAGEngine

**文件**: `backend/core/rag_engine.py`

```python
from backend.core.rag_engine import RAGEngine
from backend.models.schemas import Query

rag = RAGEngine()

# 添加文档到向量库
num_chunks = rag.add_document(
    doc_id="abc123",
    text="文档内容...",
    metadata={"title": "论文标题", "category": "machine_learning"}
)

# 语义搜索
results = rag.search(
    query="深度学习",
    top_k=5,
    category="machine_learning"  # 可选
)
# 返回: List[{"content": str, "metadata": dict, "score": float}]

# 问答
query = Query(
    question="什么是深度学习？",
    category="machine_learning",  # 可选
    top_k=5
)
response = rag.query(query, language="zh")
# 返回: QueryResponse(answer=str, sources=List[dict])
```

#### 5.1.3 Summarizer

**文件**: `backend/core/summarizer.py`

```python
from backend.core.summarizer import Summarizer

summarizer = Summarizer()

# 生成摘要 (250-500字)
summary = summarizer.generate_summary(
    doc_id="abc123",
    language="zh"  # "zh" 或 "en"
)

# 提取关键点
key_points = summarizer.extract_key_points(
    doc_id="abc123",
    language="zh"
)
# 返回: List[str]

# 完整分析
analysis = summarizer.generate_full_analysis(
    doc_id="abc123",
    language="zh"
)
# 返回: PaperSummary 对象
# 属性: methodology, contributions, conclusions, datasets_used
```

#### 5.1.4 Classifier

**文件**: `backend/core/classifier.py`

```python
from backend.core.classifier import Classifier

classifier = Classifier()

# 分类文档
result = classifier.classify_document(doc_id="abc123")
# 返回: ClassificationResult
# 属性: category, tags, confidence

# 获取分类统计
stats = classifier.get_category_statistics()
# 返回: {"machine_learning": 10, "cryptography": 5, ...}

# 获取标签统计
tag_stats = classifier.get_tag_statistics()
# 返回: {"CNN": 8, "RNN": 5, ...}

# 生成知识图谱数据
graph_data = classifier.build_knowledge_graph_data()
# 返回: {"nodes": List[dict], "edges": List[dict]}
```

#### 5.1.5 LearningPathGenerator

**文件**: `backend/core/learning_path.py`

```python
from backend.core.learning_path import LearningPathGenerator

generator = LearningPathGenerator()

# 生成学习路径
path = generator.generate_learning_path(
    goal="掌握深度学习基础",
    category="machine_learning",
    use_user_documents=True
)
# 返回: LearningPath 对象

# 查询前置知识
prerequisites = generator.query_prerequisites(
    topic="卷积神经网络"
)
# 返回: List[str]
```

#### 5.1.6 ReviewHelper

**文件**: `backend/core/review_helper.py`

```python
from backend.core.review_helper import ReviewHelper

helper = ReviewHelper()

# 生成闪卡
flashcards = helper.generate_flashcards(
    topic="机器学习基础",
    num_cards=15
)
# 返回: List[Flashcard]

# 生成速记表
cheat_sheet = helper.generate_cheat_sheet(
    topic="优化算法"
)
# 返回: CheatSheet 对象

# 对比概念
comparison = helper.compare_concepts(
    concepts=["SVM", "决策树", "神经网络"]
)
# 返回: ComparisonTable 对象

# 生成练习题
questions = helper.generate_practice_questions(
    topic="深度学习",
    num_questions=10
)
# 返回: List[str]
```

### 5.2 工具函数

#### 5.2.1 LLM 工具

**文件**: `backend/utils/llm_utils.py`

```python
from backend.utils.llm_utils import get_llm, get_embeddings

# 获取 LLM 实例
llm = get_llm(
    temperature=0.7,
    model="gpt-4-turbo-preview",  # 可选
    max_tokens=2000  # 可选
)

# 获取嵌入模型
embeddings = get_embeddings()

# 使用 LLM
response = llm.predict("你好，世界！")
```

#### 5.2.2 文件工具

**文件**: `backend/utils/file_utils.py`

```python
from backend.utils.file_utils import (
    get_file_hash,
    get_document_type,
    get_file_size,
    sanitize_filename
)

# 获取文件哈希
hash_value = get_file_hash("/path/to/file.pdf")

# 检测文档类型
doc_type = get_document_type("/path/to/file.docx")
# 返回: DocumentType.DOCX

# 获取文件大小
size = get_file_size("/path/to/file.pdf")  # 字节

# 清理文件名
clean_name = sanitize_filename("file:name?.pdf")
# 返回: "file_name_.pdf"
```

#### 5.2.3 认证工具

**文件**: `frontend/auth.py`

```python
from frontend.auth import (
    check_authentication,
    get_current_user,
    require_authentication,
    check_permission
)

# 检查是否已认证
if check_authentication():
    print("已登录")

# 获取当前用户
user = get_current_user()
# 返回: {"username": str, "name": str, "role": str} 或 None

# 装饰器保护页面
@require_authentication
def protected_page():
    st.write("这是受保护的内容")

# 检查权限
if check_permission(required_role="admin"):
    st.write("管理员操作")
```

#### 5.2.4 国际化工具

**文件**: `frontend/i18n.py`

```python
from frontend.i18n import t, get_language, set_language

# 翻译文本
text = t("app_title")  # 返回当前语言的翻译

# 带参数的翻译
text = t("showing_documents", count=10)
# 返回: "显示 10 个文档" 或 "Showing 10 documents"

# 获取当前语言
lang = get_language()  # "zh" 或 "en"

# 设置语言
set_language("en")
```

---

## 6. 故障排除

### 6.1 常见问题

#### 问题 1: ModuleNotFoundError

**错误信息：**
```
ModuleNotFoundError: No module named 'langchain'
```

**解决方法：**
```bash
# 确保虚拟环境已激活
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 重新安装依赖
pip install -r requirements.txt
```

#### 问题 2: OpenAI API Key 错误

**错误信息：**
```
AuthenticationError: Invalid API Key
```

**解决方法：**
```bash
# 1. 检查 .env 文件
cat .env | grep OPENAI_API_KEY

# 2. 确保 API Key 正确
# 访问 https://platform.openai.com/api-keys 验证

# 3. 重启应用
```

#### 问题 3: Ollama 连接失败

**错误信息：**
```
ConnectionError: Could not connect to Ollama
```

**解决方法：**
```bash
# 1. 检查 Ollama 是否运行
ollama list

# 2. 启动 Ollama
ollama serve

# 3. 测试连接
curl http://localhost:11434/api/tags

# 4. 检查 .env 配置
OLLAMA_BASE_URL=http://localhost:11434
```

#### 问题 4: ChromaDB 错误

**错误信息：**
```
ValueError: Could not connect to ChromaDB
```

**解决方法：**
```bash
# 1. 删除旧的向量数据库
rm -rf data/vectorstore

# 2. 重新创建
mkdir -p data/vectorstore

# 3. 重启应用
```

#### 问题 5: 文档上传失败

**错误信息：**
```
Error processing document
```

**解决方法：**
```bash
# 1. 检查文件格式是否支持
# 支持: PDF, DOCX, PPTX, EPUB, TXT, MD

# 2. 检查文件大小
# 默认限制: 50MB

# 3. 检查文件编码 (文本文件)
file -I your_file.txt
# 应该是 UTF-8

# 4. 检查日志
tail -f logs/app.log  # 如果有日志
```

#### 问题 6: 内存不足

**错误信息：**
```
MemoryError: Unable to allocate array
```

**解决方法：**
```bash
# 1. 减少 CHUNK_SIZE
CHUNK_SIZE=500  # 在 .env 中

# 2. 减少 TOP_K_RESULTS
TOP_K_RESULTS=3

# 3. 使用更小的 LLM 模型
OLLAMA_MODEL=phi  # 2.7B 参数
```

#### 问题 7: 认证循环

**错误信息：**
```
页面不断重定向到登录页
```

**解决方法：**
```bash
# 1. 清除浏览器 Cookie
# Chrome: 设置 → 隐私 → Cookie → 清除

# 2. 检查 config/users.yaml
cat config/users.yaml

# 3. 重置认证状态
# 在 Streamlit 中: 设置 → 清除缓存
```

### 6.2 日志和调试

#### 6.2.1 启用详细日志

编辑 Python 文件添加日志：

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

#### 6.2.2 Streamlit 调试模式

```bash
streamlit run frontend/app.py --logger.level=debug
```

#### 6.2.3 检查环境变量

```python
from config.settings import settings

print(f"LLM Provider: {settings.llm_provider}")
print(f"LLM Model: {settings.llm_model}")
print(f"Vector DB Path: {settings.vector_db_path}")
```

---

## 7. 开发指南

### 7.1 项目结构

```
PaperManagement/
├── backend/
│   ├── core/
│   │   ├── document_processor.py    # 文档处理
│   │   ├── rag_engine.py           # RAG 引擎
│   │   ├── summarizer.py           # 摘要生成
│   │   ├── classifier.py           # 分类器
│   │   ├── learning_path.py        # 学习路径
│   │   └── review_helper.py        # 复习工具
│   ├── models/
│   │   └── schemas.py              # 数据模型
│   └── utils/
│       ├── llm_utils.py            # LLM 工具
│       └── file_utils.py           # 文件工具
├── config/
│   ├── settings.py                 # 配置管理
│   └── users.yaml                  # 用户配置
├── frontend/
│   ├── app.py                      # 主应用
│   ├── auth.py                     # 认证模块
│   ├── i18n.py                     # 国际化
│   └── pages/
│       ├── 1_📄_论文总结.py
│       ├── 2_📚_资料管理.py
│       ├── 3_🗺️_学习路线.py
│       └── 4_📝_考试复习.py
├── data/
│   ├── documents/                  # 文档存储
│   ├── metadata/                   # 元数据
│   └── vectorstore/                # 向量数据库
├── docs/
│   └── COMPLETE_GUIDE.md           # 完整指南
├── .env                            # 环境变量
├── .env.example                    # 环境变量示例
├── requirements.txt                # 依赖列表
├── CHANGELOG.md                    # 更新日志
└── README.md                       # 项目说明
```

### 7.2 添加新功能

#### 7.2.1 添加新的文档处理器

```python
# 在 backend/core/document_processor.py 中

def process_new_format(self, file_path: str) -> Dict[str, Any]:
    """处理新格式文档"""
    try:
        # 1. 读取文件
        # 2. 提取文本
        # 3. 提取元数据

        return {
            "text": full_text,
            "num_pages": num_pages,
            "metadata": metadata,
            "title": title
        }
    except Exception as e:
        logger.error(f"Error processing new format {file_path}: {e}")
        raise
```

#### 7.2.2 添加新的 Prompt 模板

```python
# 在 backend/utils/llm_utils.py 中

NEW_PROMPT = PromptTemplate(
    input_variables=["input1", "input2"],
    template="""你的 Prompt 模板

    输入1: {input1}
    输入2: {input2}

    输出:"""
)
```

#### 7.2.3 添加新的前端页面

```python
# 创建 frontend/pages/5_🆕_新功能.py

import streamlit as st
from frontend.i18n import t, language_selector

st.set_page_config(page_title="新功能", page_icon="🆕")

language_selector()

st.title(t("new_feature_title"))
st.write(t("new_feature_description"))

# 你的功能代码...
```

### 7.3 测试

#### 7.3.1 单元测试示例

```python
# tests/test_document_processor.py
import pytest
from backend.core.document_processor import DocumentProcessor

def test_process_pdf():
    processor = DocumentProcessor()
    result = processor.process_pdf("test_data/sample.pdf")

    assert "text" in result
    assert "metadata" in result
    assert len(result["text"]) > 0

def test_get_document_type():
    from backend.utils.file_utils import get_document_type
    from backend.models.schemas import DocumentType

    assert get_document_type("file.pdf") == DocumentType.PDF
    assert get_document_type("file.docx") == DocumentType.DOCX
```

#### 7.3.2 运行测试

```bash
# 安装 pytest
pip install pytest

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_document_processor.py

# 显示详细输出
pytest -v
```

### 7.4 代码规范

#### 7.4.1 Python 代码风格

遵循 PEP 8 规范：

```bash
# 安装 black 和 flake8
pip install black flake8

# 格式化代码
black backend/ frontend/

# 检查代码
flake8 backend/ frontend/ --max-line-length=100
```

#### 7.4.2 文档字符串

```python
def my_function(param1: str, param2: int) -> dict:
    """
    函数简短描述。

    详细描述（可选）。

    Args:
        param1: 参数1的描述
        param2: 参数2的描述

    Returns:
        返回值的描述

    Raises:
        ValueError: 何时抛出此异常
    """
    pass
```

### 7.5 贡献指南

#### 7.5.1 Fork 和 Clone

```bash
# 1. Fork 项目到你的 GitHub

# 2. Clone 你的 fork
git clone https://github.com/YOUR_USERNAME/PaperManagement.git

# 3. 添加上游仓库
git remote add upstream https://github.com/ORIGINAL/PaperManagement.git
```

#### 7.5.2 创建分支

```bash
# 创建新分支
git checkout -b feature/my-new-feature

# 或修复 bug
git checkout -b fix/issue-123
```

#### 7.5.3 提交代码

```bash
# 添加文件
git add .

# 提交（遵循约定式提交）
git commit -m "feat: add new document format support"
git commit -m "fix: resolve authentication loop issue"
git commit -m "docs: update API reference"

# 推送
git push origin feature/my-new-feature
```

**提交消息格式：**
- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试
- `chore:` 构建/工具

#### 7.5.4 创建 Pull Request

1. 在 GitHub 上打开 Pull Request
2. 描述你的更改
3. 关联相关 Issue (如 `Fixes #123`)
4. 等待 Review

---

## 8. 性能优化

### 8.1 向量数据库优化

#### 8.1.1 分块策略

```python
# 调整分块大小平衡性能和准确性
CHUNK_SIZE=1000          # 较大: 更多上下文, 较慢
CHUNK_SIZE=500           # 较小: 更快, 上下文少
CHUNK_OVERLAP=200        # 重叠确保连贯性
```

#### 8.1.2 索引优化

```python
# ChromaDB 默认使用 HNSW 索引
# 可以调整参数:

vectorstore = Chroma(
    collection_metadata={
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 100,  # 构建质量
        "hnsw:M": 16                   # 连接数
    }
)
```

### 8.2 LLM 调用优化

#### 8.2.1 缓存策略

```python
import functools
from typing import Dict

@functools.lru_cache(maxsize=128)
def cached_llm_call(prompt: str) -> str:
    """缓存 LLM 调用结果"""
    llm = get_llm()
    return llm.predict(prompt)
```

#### 8.2.2 批处理

```python
# 批量处理文档
def batch_process_documents(file_paths: List[str], batch_size: int = 10):
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i+batch_size]
        # 并行处理批次
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = executor.map(process_document, batch)
```

### 8.3 前端优化

#### 8.3.1 使用 Streamlit 缓存

```python
@st.cache_resource
def load_heavy_model():
    """缓存重量级资源"""
    return RAGEngine()

@st.cache_data(ttl=3600)  # 1小时过期
def get_statistics():
    """缓存统计数据"""
    return classifier.get_category_statistics()
```

#### 8.3.2 延迟加载

```python
# 只在需要时加载组件
if st.button("生成知识图谱"):
    with st.spinner("生成中..."):
        graph_data = classifier.build_knowledge_graph_data()
        # 显示图谱
```

### 8.4 内存管理

#### 8.4.1 限制文本长度

```python
def truncate_text(text: str, max_tokens: int = 8000) -> str:
    """截断文本避免超出限制"""
    # 粗略估算: 1 token ≈ 4 字符
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        return text[:max_chars]
    return text
```

#### 8.4.2 清理资源

```python
import gc

def cleanup():
    """手动触发垃圾回收"""
    gc.collect()
```

### 8.5 数据库优化

#### 8.5.1 定期清理

```bash
# 清理旧的向量数据库
rm -rf data/vectorstore/*

# 重建索引
python scripts/rebuild_index.py
```

#### 8.5.2 备份策略

```bash
# 定期备份元数据和文档
tar -czf backup_$(date +%Y%m%d).tar.gz data/

# 恢复
tar -xzf backup_20250117.tar.gz
```

---

## 附录

### A. 配置文件示例

#### A.1 完整的 .env 文件

```bash
# ===== LLM Provider =====
LLM_PROVIDER=openai

# ===== OpenAI =====
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo-preview

# ===== Ollama =====
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# ===== Paths =====
VECTOR_DB_PATH=./data/vectorstore
DOCUMENT_PATH=./data/documents
METADATA_PATH=./data/metadata

# ===== RAG =====
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# ===== LLM =====
TEMPERATURE=0.7
MAX_TOKENS=2000

# ===== App =====
MAX_FILE_SIZE_MB=50
SUPPORTED_LANGUAGES=en,zh
```

#### A.2 users.yaml 示例

```yaml
credentials:
  usernames:
    admin:
      name: "Administrator"
      password: "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
      role: "admin"

    demo:
      name: "Demo User"
      password: "2a97516c354b68848cdbd8f54a226a0a55b21ed138e207ad6c5cbb9c00aa5aea"
      role: "user"

    researcher:
      name: "Research User"
      password: "<your-hash-here>"
      role: "user"

cookie:
  name: "ai_paper_management"
  key: "random_signature_key_change_this_in_production"
  expiry_days: 30

preauthorized:
  emails:
    - admin@example.com
```

### B. 常用命令速查

```bash
# ===== 环境管理 =====
python -m venv venv                    # 创建虚拟环境
source venv/bin/activate               # 激活 (Linux/Mac)
venv\Scripts\activate                  # 激活 (Windows)
deactivate                             # 退出虚拟环境

# ===== 依赖管理 =====
pip install -r requirements.txt        # 安装依赖
pip freeze > requirements.txt          # 导出依赖
pip list --outdated                    # 查看过时包

# ===== 运行应用 =====
streamlit run frontend/app.py          # 启动应用
streamlit run frontend/app.py --server.port 8502  # 自定义端口

# ===== Git 操作 =====
git status                             # 查看状态
git add .                              # 添加所有文件
git commit -m "message"                # 提交
git push                               # 推送
git pull                               # 拉取

# ===== Ollama 操作 =====
ollama list                            # 列出模型
ollama pull llama2                     # 下载模型
ollama rm llama2                       # 删除模型
ollama serve                           # 启动服务

# ===== 清理操作 =====
find . -type d -name "__pycache__" -exec rm -r {} +  # 清理缓存
rm -rf data/vectorstore/*              # 清空向量库
```

### C. 支持的模型列表

#### C.1 OpenAI 模型

| 模型 | 参数 | 上下文 | 用途 |
|------|------|--------|------|
| gpt-4-turbo-preview | - | 128K | 最强性能 |
| gpt-4 | - | 8K | 高质量推理 |
| gpt-3.5-turbo | - | 16K | 快速响应 |
| text-embedding-3-small | - | 8K | 向量嵌入 |
| text-embedding-3-large | - | 8K | 高质量嵌入 |

#### C.2 Ollama 模型

| 模型 | 参数 | 内存需求 | 特点 |
|------|------|---------|------|
| llama2 | 7B | 8GB | 通用 |
| llama3 | 8B | 8GB | 性能提升 |
| mistral | 7B | 8GB | 高效 |
| mixtral | 8x7B | 32GB | 专家混合 |
| phi | 2.7B | 4GB | 轻量 |
| gemma | 2B/7B | 4-8GB | Google |
| codellama | 7B | 8GB | 编程 |

### D. 错误代码参考

| 错误代码 | 含义 | 解决方法 |
|---------|------|---------|
| AUTH_001 | API Key 无效 | 检查 .env 文件 |
| AUTH_002 | 认证失败 | 验证用户名密码 |
| DOC_001 | 文档格式不支持 | 检查文件类型 |
| DOC_002 | 文档处理失败 | 查看详细错误日志 |
| VEC_001 | 向量库连接失败 | 检查路径配置 |
| VEC_002 | 嵌入生成失败 | 检查 LLM 连接 |
| LLM_001 | LLM 调用失败 | 检查 Provider 配置 |
| LLM_002 | Token 超限 | 减少输入长度 |

---

## 版本历史

- **v0.3.0** (2025-01-17): 本地 LLM + 认证系统
- **v0.2.0** (2025-01-17): 多格式 + i18n + 响应式
- **v0.1.0** (2025-01-15): 初始发布

---

## 许可证

MIT License

---

## 联系方式

- **GitHub**: https://github.com/yourusername/PaperManagement
- **Issues**: https://github.com/yourusername/PaperManagement/issues
- **Email**: your.email@example.com

---

**文档版本**: v0.3.0
**最后更新**: 2025-01-17
