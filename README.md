<div align="center">

# 📚 AI 论文/文献管理助手

### AI Paper Management Assistant

*智能学术资料管理 | 论文分析 | 学习路径规划 | 考试复习助手*

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-orange.svg)](https://github.com/langchain-ai/langchain)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[功能特点](#-功能特点) • [快速开始](#-快速开始) • [使用指南](#-使用指南) • [技术架构](#-技术架构) • [示例](#-使用示例)

---

</div>

## 📖 简介

**AI 论文/文献管理助手**是一个智能化的学术资料管理系统，专为学生和研究人员设计。基于先进的 **RAG (Retrieval-Augmented Generation)** 架构，结合大语言模型的强大能力，帮助您高效管理论文、自动生成摘要、规划学习路径、准备考试复习。

### ✨ 核心亮点

<table>
<tr>
<td width="50%">

🤖 **基于 RAG 架构**
- 检索增强生成技术
- 确保答案准确可靠
- 减少AI幻觉问题

📄 **智能论文分析**
- 自动摘要生成
- 关键点提取
- 多语言支持

</td>
<td width="50%">

📚 **智能资料整理**
- 自动分类打标签
- 知识图谱可视化
- 语义搜索引擎

🗺️ **学习路径规划**
- 个性化学习计划
- 前置知识识别
- 资源智能推荐

</td>
</tr>
</table>

## 🎯 功能特点

<details open>
<summary><b>📄 功能模块 1：自动总结论文要点</b></summary>

<br>

| 功能 | 描述 | 特点 |
|------|------|------|
| 📝 **摘要生成** | 自动生成250-500字精炼摘要 | • 涵盖主要贡献<br>• 方法论总结<br>• 核心结论 |
| 🔑 **关键点提取** | 以列表形式展示核心论点 | • 创新点识别<br>• 主要发现<br>• 实用价值 |
| 💬 **智能问答** | 基于论文内容精准回答 | • RAG技术支持<br>• 来源可追溯<br>• 准确度高 |
| 🌍 **多语言支持** | 中英文双语输出 | • 智能翻译<br>• 术语准确<br>• 可切换 |

</details>

<details>
<summary><b>📚 功能模块 2：智能资料整理</b></summary>

<br>

| 功能 | 描述 | 应用场景 |
|------|------|----------|
| 🏷️ **自动分类** | AI驱动的文档分类 | 机器学习、密码学等领域 |
| 🔖 **主题标签** | 智能提取二级标签 | CNN、RNN、RSA、AES等 |
| 🕸️ **知识图谱** | 可视化概念关系网络 | 理解知识结构和依赖 |
| 🔍 **语义搜索** | 向量化语义检索 | 自然语言查询文档 |

**支持的分类领域**：
- 🤖 机器学习 (Machine Learning)
- 🔐 密码学 (Cryptography)
- 📊 其他学术领域 (Extensible)

</details>

<details>
<summary><b>🗺️ 功能模块 3：生成学习路线图</b></summary>

<br>

**智能规划您的学习之旅**

```mermaid
graph LR
    A[设定目标] --> B[分析资料库]
    B --> C[生成路线]
    C --> D[推荐资源]
    D --> E[时间估算]
    E --> F[开始学习]
```

**核心特性**：
- ✅ **路径规划**：结构化学习步骤，循序渐进
- ✅ **前置知识**：自动识别必备基础知识
- ✅ **资源链接**：匹配您的文档库内容
- ✅ **时间估算**：合理的学习时间预估
- ✅ **可导出**：Markdown格式便于分享

</details>

<details>
<summary><b>📝 功能模块 4：辅助考试复习</b></summary>

<br>

| 复习工具 | 用途 | 特点 |
|----------|------|------|
| 🗂️ **闪卡** | 快速记忆核心概念 | • 问答格式<br>• 支持翻页<br>• 可下载 |
| 📄 **速记表** | 考前快速浏览 | • 定义公式<br>• 关键算法<br>• 精炼表格 |
| ⚖️ **概念对比** | 理解相似概念差异 | • 对比表格<br>• 多维度分析<br>• 清晰直观 |
| ✍️ **练习题** | 自我检测学习效果 | • 自动生成<br>• 含答案解析<br>• 可定制 |

</details>

---

## 🏗️ 技术架构

<div align="center">

```
┌─────────────────────────────────────────────────────────┐
│                     Streamlit 前端                       │
│          (交互式UI + 数据可视化 + 知识图谱)              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      核心业务层                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │文档处理  │ │  RAG引擎 │ │ 智能分类 │ │学习路径  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      数据存储层                          │
│     ChromaDB向量库  +  文档存储  +  元数据管理          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      AI服务层                            │
│             OpenAI API (LLM + Embeddings)               │
└─────────────────────────────────────────────────────────┘
```

</div>

### 🔧 技术栈详情

<table>
<tr>
<td width="50%" valign="top">

#### 后端技术
- ![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white) **Python 3.9+**
- ![LangChain](https://img.shields.io/badge/LangChain-0.1.0-2C5F2D?style=flat) **LangChain** - RAG框架
- ![ChromaDB](https://img.shields.io/badge/ChromaDB-Latest-FF6B6B?style=flat) **ChromaDB** - 向量数据库
- ![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat&logo=openai&logoColor=white) **OpenAI API** - LLM服务
- 📄 **PyMuPDF** - PDF处理
- 🔗 **arXiv API** - 论文下载

</td>
<td width="50%" valign="top">

#### 前端技术
- ![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-FF4B4B?style=flat&logo=streamlit&logoColor=white) **Streamlit** - Web框架
- 📊 **Plotly** - 数据可视化
- 🕸️ **NetworkX** - 图算法
- 🎨 **Custom CSS** - 界面美化

</td>
</tr>
</table>

### 📁 项目结构

```
PaperManagement/
├── backend/                    # 后端核心逻辑
│   ├── core/                   # 核心业务模块
│   │   ├── document_processor.py   # 文档处理
│   │   ├── rag_engine.py          # RAG系统
│   │   ├── classifier.py          # 自动分类
│   │   ├── summarizer.py          # 摘要生成
│   │   ├── learning_path.py       # 学习路径
│   │   └── review_helper.py       # 复习助手
│   ├── models/                 # 数据模型
│   └── utils/                  # 工具函数
├── frontend/                   # Streamlit前端
│   ├── app.py                  # 主应用
│   └── pages/                  # 功能页面
│       ├── 1_📄_论文总结.py
│       ├── 2_📚_资料管理.py
│       ├── 3_🗺️_学习路线.py
│       └── 4_📝_考试复习.py
├── data/                       # 数据存储
│   ├── documents/              # 上传的文档
│   ├── vectorstore/            # 向量数据库
│   └── metadata/               # 元数据
├── config/                     # 配置
│   └── settings.py
├── requirements.txt            # 依赖
└── README.md                   # 项目文档
```

---

## 🚀 快速开始

### 📋 前置要求

在开始之前，请确保您的系统满足以下要求：

- 💻 **操作系统**: Windows / macOS / Linux
- 🐍 **Python**: 3.9 或更高版本
- 🔑 **OpenAI API Key**: [获取API密钥](https://platform.openai.com/api-keys)
- 💾 **磁盘空间**: 至少 500MB 可用空间

### ⚡ 三步快速部署

<table>
<tr>
<td width="33%" valign="top">

#### 步骤 1️⃣: 克隆项目

```bash
# 克隆仓库
git clone https://github.com/yourusername/PaperManagement.git

# 进入项目目录
cd PaperManagement
```

</td>
<td width="33%" valign="top">

#### 步骤 2️⃣: 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt
```

</td>
<td width="33%" valign="top">

#### 步骤 3️⃣: 配置运行

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 添加API密钥
# OPENAI_API_KEY=sk-...

# 启动应用
cd frontend
streamlit run app.py
```

</td>
</tr>
</table>

### 🎉 完成！

浏览器将自动打开应用界面（默认地址：`http://localhost:8501`）

如果没有自动打开，请手动访问该地址。

> 💡 **提示**: 首次运行可能需要几秒钟来初始化向量数据库。

---

## 📖 使用指南

### 🎬 使用流程

```
上传文档 → 自动分类 → 智能分析 → 知识管理 → 学习规划 → 考试复习
```

<details open>
<summary><b>📤 Step 1: 上传文档</b></summary>

<br>

**方式一：本地文件上传**
1. 进入 `📄 论文总结` 页面
2. 选择 **上传本地文件**
3. 支持格式：`PDF` / `TXT` / `MD` / `DOCX` / `PPTX` / `EPUB`
4. 点击 **处理文档** 开始解析

**方式二：arXiv 直接导入**
1. 进入 `📄 论文总结` 页面
2. 选择 **从 arXiv 导入**
3. 输入论文ID（例如：`2301.12345`）
4. 系统自动下载并处理

> ✨ **自动化处理**: 上传后系统将自动完成文本提取、分类、标签生成和向量化

</details>

<details>
<summary><b>🔍 Step 2: 分析论文</b></summary>

<br>

| 操作 | 说明 |
|------|------|
| 1️⃣ 选择文档 | 在文档列表中选择要分析的论文 |
| 2️⃣ 选择语言 | 中文 (zh) / 英文 (en) |
| 3️⃣ 选择分析类型 | • 摘要 - 250-500字概述<br>• 关键点 - 核心论点列表<br>• 完整分析 - 包含方法论、贡献、结论等 |
| 4️⃣ 生成结果 | 点击"开始分析"获取结果 |

</details>

<details>
<summary><b>💬 Step 3: 智能问答</b></summary>

<br>

**RAG驱动的精准问答系统**

```
用户提问 → 向量检索 → 找到相关片段 → LLM生成答案 → 返回结果+来源
```

**使用技巧**：
- 📝 具体明确的问题效果更好
- 🎯 可筛选特定分类提高准确度
- 🔢 调整检索数量平衡速度和质量
- 📚 查看来源了解答案依据

</details>

<details>
<summary><b>📚 Step 4: 管理资料</b></summary>

<br>

**功能概览**

| 功能 | 描述 | 使用场景 |
|------|------|----------|
| 📑 **文档浏览** | 查看所有上传的文档 | 快速查找和管理 |
| 🔍 **语义搜索** | 自然语言搜索文档内容 | 找到相关信息 |
| 🕸️ **知识图谱** | 可视化概念关系网络 | 理解知识结构 |
| 📊 **统计分析** | 分类分布、标签统计 | 了解资料库全貌 |

</details>

<details>
<summary><b>🗺️ Step 5: 生成学习路线</b></summary>

<br>

**操作步骤**：
1. 📝 描述学习目标（例如："我想入门机器学习"）
2. 🎯 选择学习领域（可选）
3. 📚 选择是否使用文档库
4. 🚀 点击生成学习路径
5. 💾 导出为 Markdown 文件

**快速模板**：
- 🤖 机器学习入门
- 🧠 深度学习进阶
- 🔐 密码学基础
- 🔑 现代加密技术

</details>

<details>
<summary><b>📝 Step 6: 准备考试</b></summary>

<br>

**四大复习工具**

<table>
<tr>
<td width="50%">

**🗂️ 闪卡 (Flashcards)**
- 问答格式
- 支持翻页浏览
- 可导出为Markdown

**⚖️ 概念对比**
- 多维度对比分析
- 表格化呈现
- 清晰展示差异

</td>
<td width="50%">

**📄 速记表 (Cheat Sheet)**
- 核心定义和公式
- 关键算法总结
- 考前快速浏览

**✍️ 练习题**
- 自动生成题目
- 包含答案解析
- 自我检测效果

</td>
</tr>
</table>

</details>

---

## ⚙️ 配置说明

### 环境变量配置 (`.env`)

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | *(必填)* | `sk-...` |
| `LLM_MODEL` | 使用的LLM模型 | `gpt-4-turbo-preview` | `gpt-3.5-turbo` |
| `EMBEDDING_MODEL` | 向量化模型 | `text-embedding-3-small` | `text-embedding-ada-002` |
| `MAX_FILE_SIZE_MB` | 最大文件大小(MB) | `50` | `100` |

### 应用配置 (`config/settings.py`)

```python
# RAG配置
chunk_size = 1000           # 文档分块大小
chunk_overlap = 200         # 分块重叠大小
top_k_results = 5           # 检索结果数量

# LLM配置
temperature = 0.7           # 生成温度 (0-1)
max_tokens = 2000          # 最大生成token数
```

### 📁 支持的文件格式

| 格式 | 类型 | 说明 | 典型用途 |
|------|------|------|----------|
| 📕 **PDF** | 学术论文 | 完整支持文本提取 | 期刊论文、会议论文 |
| 📄 **TXT** | 纯文本 | UTF-8编码 | 笔记、代码文档 |
| 📝 **MD** | Markdown | 保留格式结构 | 课程讲义、博客 |
| 🔗 **arXiv** | 在线论文 | 自动下载 | 预印本论文 |

---

## ❓ 常见问题

<details>
<summary><b>Q1: 如何获取 OpenAI API Key？</b></summary>

<br>

1. 访问 [OpenAI 平台](https://platform.openai.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 点击 "Create new secret key"
5. 复制密钥到 `.env` 文件

💡 **提示**: 保管好您的API密钥，不要泄露给他人

</details>

<details>
<summary><b>Q2: 如何更换 LLM 模型？</b></summary>

<br>

编辑 `.env` 文件，修改 `LLM_MODEL` 参数：

```bash
# 使用 GPT-3.5 (更快、更便宜)
LLM_MODEL=gpt-3.5-turbo

# 使用 GPT-4 (更强大、更准确)
LLM_MODEL=gpt-4-turbo-preview

# 使用 GPT-4o (最新、最优化)
LLM_MODEL=gpt-4o
```

</details>

<details>
<summary><b>Q3: 文档处理速度慢怎么办？</b></summary>

<br>

**优化建议**：

✅ **减少分块大小**
```python
# config/settings.py
chunk_size = 500  # 从1000减到500
```

✅ **使用更快的模型**
```bash
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
```

✅ **限制文件大小**
```bash
MAX_FILE_SIZE_MB=20  # 限制为20MB
```

✅ **处理前预处理文档**
- 移除图片密集的页面
- 压缩PDF文件

</details>

<details>
<summary><b>Q4: 数据存储在哪里？是否安全？</b></summary>

<br>

📂 **本地存储位置**：
```
data/
├── documents/      # 原始文档
├── vectorstore/    # 向量数据库
└── metadata/       # 元数据和提取的文本
```

🔒 **安全性保证**：
- ✅ 所有文档存储在本地
- ✅ 不上传到第三方服务器
- ✅ 仅文本片段发送给OpenAI API用于生成
- ✅ 可完全离线浏览已处理文档

</details>

<details>
<summary><b>Q5: 如何清空所有数据？</b></summary>

<br>

**方法一：通过界面**
1. 进入 `📚 资料管理` 页面
2. 在侧边栏找到"批量操作"
3. 点击"清空所有文档"
4. 确认删除

**方法二：手动删除**
```bash
# 删除所有数据文件
rm -rf data/documents/*
rm -rf data/vectorstore/*
rm -rf data/metadata/*
```

⚠️ **注意**: 此操作不可恢复，请谨慎操作

</details>

<details>
<summary><b>Q6: 支持本地 LLM 吗？</b></summary>

<br>

**现已支持 Ollama！** 🎉

系统支持两种 LLM 提供商：
1. **OpenAI** (默认) - 需要 API Key
2. **Ollama** (本地) - 完全免费，隐私保护

**使用 Ollama 的步骤**：

1. **安装 Ollama**:
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Windows: 访问 ollama.com 下载安装
   ```

2. **下载模型**:
   ```bash
   ollama pull llama2
   ollama pull nomic-embed-text
   ```

3. **配置系统**:
   在 `.env` 文件中设置：
   ```bash
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=llama2
   OLLAMA_EMBEDDING_MODEL=nomic-embed-text
   OLLAMA_BASE_URL=http://localhost:11434
   ```

4. **启动应用** - 系统将自动使用 Ollama！

**支持的模型**：
- 🦙 LLaMA 2, LLaMA 3
- 🌟 Mistral, Mixtral
- 💻 CodeLlama
- 🔬 Phi, Gemma
- 更多模型请访问 [ollama.com/library](https://ollama.com/library)

</details>

<details>
<summary><b>Q7: 报错 "Connection Error" 怎么办？</b></summary>

<br>

**可能原因和解决方案**：

1️⃣ **网络问题**
```bash
# 测试网络连接
curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_API_KEY"
```

2️⃣ **API密钥错误**
- 检查 `.env` 文件中的 `OPENAI_API_KEY`
- 确保没有多余的空格或引号

3️⃣ **代理设置**
```bash
# 如果使用代理
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

4️⃣ **API额度不足**
- 检查 OpenAI 账户余额
- 访问 [OpenAI Usage](https://platform.openai.com/usage)

</details>

<details>
<summary><b>Q8: 如何使用用户认证功能？</b></summary>

<br>

系统内置了用户认证和权限管理系统：

**默认账户**：
- 管理员: `admin` / `admin123`
- 普通用户: `demo` / `demo123`

**修改密码**：
编辑 `config/users.yaml` 文件（首次运行会自动生成）

**添加新用户**：
```yaml
credentials:
  usernames:
    newuser:
      name: "新用户"
      password: "<SHA256-hashed-password>"
      role: "user"  # 或 "admin"
```

**角色权限**：
- 👤 **user**: 普通用户，访问所有功能
- 👑 **admin**: 管理员，额外权限（未来扩展）

⚠️ **生产环境**: 请务必修改默认密码！

</details>

<details>
<summary><b>Q9: 如何切换语言？</b></summary>

<br>

系统支持 **中文** 🇨🇳 和 **英文** 🇬🇧 双语界面：

**切换方法**：
1. 打开任意页面
2. 在左侧边栏找到"语言/Language"选择器
3. 选择您需要的语言
4. 页面将自动刷新并应用新语言

**支持范围**：
- ✅ 所有UI界面文本
- ✅ 菜单和按钮
- ✅ 提示信息
- ⚠️ 文档内容保持原始语言（不自动翻译）

**扩展其他语言**：
可以在 `frontend/i18n.py` 中添加新语言翻译

</details>

---

## 🗺️ 开发路线图

### ✅ 已完成 (v0.1.0 - v0.3.0)

**核心功能 (v0.1.0):**
- [x] 🤖 基于 RAG 的智能问答系统
- [x] 📄 论文自动摘要和分析
- [x] 🏷️ 智能分类和标签系统
- [x] 🕸️ 知识图谱可视化
- [x] 🗺️ 学习路径生成器
- [x] 📝 考试复习工具套件
- [x] 🔍 语义搜索引擎
- [x] 📚 文档管理系统

**增强功能 (v0.2.0):**
- [x] 📊 支持更多文档格式 (DOCX, PPTX, EPUB)
- [x] 🌐 多语言界面支持 (中英文切换)
- [x] 📱 响应式移动端适配

**高级功能 (v0.3.0):**
- [x] 🦙 本地 LLM 支持 (Ollama)
- [x] 🔐 用户认证和权限管理
- [x] 👤 多用户角色系统

### 🚀 计划中 (v0.4.0+)

- [ ] 👥 多用户协作功能
- [ ] ☁️ 云端同步
- [ ] 📥 批量导入导出
- [ ] 🔔 智能提醒和推荐
- [ ] 📈 学习进度追踪
- [ ] 🎨 自定义主题和样式
- [ ] 🔌 插件系统
- [ ] 🔄 文档版本控制
- [ ] 📊 高级数据分析仪表板

---

## 🤝 贡献指南

我们热烈欢迎各种形式的贡献！无论是报告 bug、提出新功能建议，还是直接贡献代码。

### 如何贡献

<table>
<tr>
<td width="33%" valign="top">

#### 🐛 报告 Bug

1. 检查是否已有相关 Issue
2. 创建新 Issue
3. 详细描述问题
4. 提供复现步骤
5. 附上环境信息

</td>
<td width="33%" valign="top">

#### 💡 提出建议

1. 在 Issues 中描述想法
2. 说明使用场景
3. 提供设计思路
4. 讨论实现方案
5. 等待社区反馈

</td>
<td width="33%" valign="top">

#### 💻 贡献代码

1. Fork 本仓库
2. 创建特性分支
3. 编写代码和测试
4. 提交 Pull Request
5. 等待代码审查

</td>
</tr>
</table>

### 开发流程

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/YOUR_USERNAME/PaperManagement.git
cd PaperManagement

# 2. 创建新分支
git checkout -b feature/your-feature-name

# 3. 进行开发
# ... 编写代码 ...

# 4. 提交更改
git add .
git commit -m "feat: add your feature description"

# 5. 推送到远程
git push origin feature/your-feature-name

# 6. 创建 Pull Request
# 在 GitHub 上点击 "New Pull Request"
```

### 代码规范

- 🐍 Python 代码遵循 PEP 8
- 📝 添加必要的注释和文档字符串
- ✅ 编写单元测试
- 🔍 通过代码检查 (`black`, `flake8`)

---

## 📄 许可证

本项目采用 **MIT 许可证**，详情请参阅 [LICENSE](LICENSE) 文件。

```
MIT License - 您可以自由地：
✅ 商业使用
✅ 修改代码
✅ 分发副本
✅ 私人使用

⚠️ 需要保留版权声明
```

---

## 📮 联系方式

<div align="center">

### 有问题或建议？

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-green?style=for-the-badge&logo=github)](https://github.com/mikeywangzq/PaperManagement/issues)
[![Email](https://img.shields.io/badge/Email-Contact-blue?style=for-the-badge&logo=gmail)](mailto:your.email@example.com)

</div>

---

## 🙏 致谢

感谢以下开源项目和服务的支持：

<table align="center">
<tr>
<td align="center" width="25%">
<img src="https://www.langchain.com/favicon.ico" width="50" height="50"><br>
<b>LangChain</b><br>
<sub>RAG 框架</sub>
</td>
<td align="center" width="25%">
<img src="https://www.trychroma.com/favicon.png" width="50" height="50"><br>
<b>ChromaDB</b><br>
<sub>向量数据库</sub>
</td>
<td align="center" width="25%">
<img src="https://streamlit.io/favicon.svg" width="50" height="50"><br>
<b>Streamlit</b><br>
<sub>Web 框架</sub>
</td>
<td align="center" width="25%">
<img src="https://openai.com/favicon.ico" width="50" height="50"><br>
<b>OpenAI</b><br>
<sub>LLM 服务</sub>
</td>
</tr>
</table>

---

<div align="center">

## ⭐ Star History

如果这个项目对您有帮助，请给我们一个 ⭐️ Star！

[![Star History Chart](https://api.star-history.com/svg?repos=mikeywangzq/PaperManagement&type=Date)](https://star-history.com/#mikeywangzq/PaperManagement&Date)

---

### 📚 AI Paper Management Assistant

**Version 0.1.0** | Made with ❤️ by the Community

基于 RAG (Retrieval-Augmented Generation) 架构，为学术研究提供智能支持

[🏠 Homepage](#-ai-论文文献管理助手) • [📖 Documentation](#-使用指南) • [🐛 Report Bug](https://github.com/mikeywangzq/PaperManagement/issues) • [✨ Request Feature](https://github.com/mikeywangzq/PaperManagement/issues)

---

© 2024 AI Paper Management Assistant. All rights reserved.

</div>
