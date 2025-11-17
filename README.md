# AI 论文/文献管理助手 (AI Paper Management Assistant)

一个智能AI助手，旨在帮助学生和研究人员高效管理、理解和学习学术论文及课程资料。

## 项目特点

- 🤖 **基于 RAG 架构**: 采用检索增强生成技术，确保答案准确可靠
- 📄 **智能论文分析**: 自动生成摘要、提取关键点、支持多语言
- 📚 **智能资料整理**: 自动分类、标签提取、知识图谱可视化
- 🗺️ **学习路径生成**: 个性化学习计划，包含前置知识和资源推荐
- 📝 **考试复习助手**: 自动生成闪卡、速记表、概念对比和练习题

## 核心功能

### 1. 自动总结论文要点 (F1)

- **摘要生成**: 生成250-500字的精炼摘要
- **关键点提取**: 以列表形式展示核心论点和创新点
- **智能问答**: 基于论文内容回答问题
- **多语言支持**: 支持中英文输出

### 2. 智能资料整理 (F2)

- **自动分类**: 自动识别并分类为"机器学习"或"密码学"
- **主题标签**: 智能提取二级主题标签（如CNN、RSA等）
- **知识图谱**: 可视化展示概念之间的关系
- **语义搜索**: 强大的语义搜索功能

### 3. 生成学习路线图 (F3)

- **路径规划**: 根据目标生成结构化学习步骤
- **资源链接**: 链接到用户资料库中的相关文件
- **前置知识**: 自动识别学习某概念所需的前置知识

### 4. 辅助考试复习 (F4)

- **闪卡生成**: 生成学习闪卡用于快速记忆
- **速记表**: 创建包含核心定义、公式的速记表
- **概念对比**: 生成清晰的概念对比表格
- **练习题**: 自动生成练习题进行自我检测

## 技术架构

### 后端技术栈

- **Python 3.9+**
- **LangChain**: RAG框架
- **ChromaDB**: 向量数据库
- **OpenAI API**: LLM和Embeddings
- **PyMuPDF**: PDF文档处理

### 前端技术栈

- **Streamlit**: 交互式Web界面
- **Plotly**: 数据可视化
- **NetworkX**: 知识图谱生成

### 项目结构

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

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/yourusername/PaperManagement.git
cd PaperManagement

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加您的 OpenAI API Key：

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 运行应用

```bash
# 进入前端目录
cd frontend

# 运行 Streamlit 应用
streamlit run app.py
```

应用将在浏览器中自动打开（通常是 http://localhost:8501）。

## 使用指南

### 上传文档

1. 导航到"📄 论文总结"页面
2. 选择上传方式：
   - **本地文件**: 上传 PDF、TXT 或 MD 文件
   - **arXiv**: 输入论文ID直接导入

### 分析论文

1. 在"论文总结"页面的"文档分析"标签中选择文档
2. 选择分析类型（摘要、关键点、完整分析）
3. 选择输出语言（中文/英文）
4. 点击"开始分析"

### 智能问答

1. 在"论文总结"页面的"智能问答"标签中输入问题
2. 可选择性地筛选分类和调整检索数量
3. 查看答案和来源

### 管理资料

1. 在"📚 资料管理"页面浏览所有文档
2. 使用语义搜索查找相关内容
3. 查看知识图谱了解概念关系
4. 查看统计分析了解文档分布

### 生成学习路线

1. 在"🗺️ 学习路线"页面描述学习目标
2. 选择学习领域（可选）
3. 选择是否使用文档库
4. 生成并查看学习路径
5. 可导出为Markdown文件

### 准备考试

1. 在"📝 考试复习"页面选择复习材料类型：
   - **闪卡**: 快速记忆核心概念
   - **速记表**: 整理关键知识点
   - **概念对比**: 对比相似概念
   - **练习题**: 自我检测
2. 输入主题并选择相关文档
3. 生成并下载复习材料

## 配置说明

主要配置在 `config/settings.py` 中：

- `llm_model`: LLM模型名称（默认: gpt-4-turbo-preview）
- `embedding_model`: Embedding模型（默认: text-embedding-3-small）
- `chunk_size`: 文档分块大小（默认: 1000）
- `chunk_overlap`: 分块重叠大小（默认: 200）
- `top_k_results`: 检索结果数量（默认: 5）

## 支持的文件格式

- **PDF**: 学术论文、讲义
- **TXT**: 纯文本文件
- **MD**: Markdown文档
- **arXiv**: 通过arXiv ID直接导入

## 注意事项

1. **API密钥**: 确保在 `.env` 文件中正确配置 OpenAI API Key
2. **文件大小**: 默认最大文件大小为50MB
3. **数据隐私**: 所有文档和向量数据存储在本地
4. **网络连接**: 需要网络连接访问 OpenAI API

## 常见问题

### Q: 如何更换LLM模型？

编辑 `.env` 文件，修改 `LLM_MODEL` 参数：

```
LLM_MODEL=gpt-3.5-turbo  # 使用更便宜的模型
```

### Q: 文档处理速度慢？

- 减少 `chunk_size` 可以加快处理速度
- 使用更小的embedding模型
- 限制上传的文档大小

### Q: 如何清空所有数据？

在"资料管理"页面的侧边栏点击"清空所有文档"。

### Q: 支持本地LLM吗？

当前版本使用 OpenAI API。如需使用本地模型，可以修改 `backend/utils/llm_utils.py` 中的配置。

## 开发计划

- [ ] 支持更多文档格式（DOCX、PPT等）
- [ ] 添加用户认证系统
- [ ] 支持本地LLM模型（Ollama等）
- [ ] 移动端适配
- [ ] 导出功能增强（PDF、DOCX等）
- [ ] 协作功能

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/yourusername/PaperManagement/issues)
- 邮件: your.email@example.com

## 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - RAG框架
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Streamlit](https://streamlit.io/) - Web应用框架
- [OpenAI](https://openai.com/) - LLM服务

---

**AI Paper Management Assistant v0.1.0**

基于 RAG (Retrieval-Augmented Generation) 架构，为学术研究提供智能支持。
