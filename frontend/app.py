"""Main Streamlit application for AI Paper Management Assistant."""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings

# Page configuration
st.set_page_config(
    page_title="AI Paper Management Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-header">📚 AI Paper Management Assistant</h1>', unsafe_allow_html=True)

st.markdown("""
### 欢迎使用 AI 论文/文献管理助手

这是一个智能AI助手，旨在帮助学生和研究人员高效管理、理解和学习学术论文及课程资料。
""")

# Features overview
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-title">📄 论文总结</div>
        <p>自动生成论文摘要、提取关键点、支持Q&A问答</p>
        <ul>
            <li>智能摘要生成 (250-500字)</li>
            <li>关键论点提取</li>
            <li>基于论文内容的问答</li>
            <li>中英文双语支持</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-box">
        <div class="feature-title">🗺️ 学习路线</div>
        <p>生成结构化的学习路径和知识图谱</p>
        <ul>
            <li>个性化学习路径规划</li>
            <li>前置知识识别</li>
            <li>资源推荐</li>
            <li>时间估算</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <div class="feature-title">📚 资料管理</div>
        <p>智能分类和整理学术资料</p>
        <ul>
            <li>自动分类 (机器学习/密码学)</li>
            <li>主题标签提取</li>
            <li>知识图谱可视化</li>
            <li>语义搜索</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-box">
        <div class="feature-title">📝 考试复习</div>
        <p>生成复习材料和练习题</p>
        <ul>
            <li>闪卡 (Flashcards)</li>
            <li>速记表 (Cheat Sheet)</li>
            <li>概念对比</li>
            <li>练习题生成</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Quick start guide
st.markdown("---")
st.markdown("### 🚀 快速开始")

st.markdown("""
1. **上传文档**: 在侧边栏选择"论文总结"页面上传PDF、文本或通过arXiv链接添加论文
2. **自动分类**: 系统会自动分类文档并提取主题标签
3. **智能问答**: 基于上传的文档提问，获得精准回答
4. **生成学习路径**: 设定学习目标，获取个性化学习计划
5. **准备考试**: 生成闪卡、速记表等复习材料
""")

# Sidebar info
with st.sidebar:
    st.markdown("### 系统信息")
    st.info(f"""
    **模型**: {settings.llm_model}

    **向量数据库**: ChromaDB

    **支持格式**: PDF, TXT, MD, arXiv
    """)

    st.markdown("### 导航")
    st.markdown("""
    - 📄 **论文总结**: 上传和分析论文
    - 📚 **资料管理**: 管理和搜索文档库
    - 🗺️ **学习路线**: 生成学习路径
    - 📝 **考试复习**: 生成复习材料
    """)

    st.markdown("---")
    st.markdown("### 使用提示")
    st.markdown("""
    💡 **提示**:
    - 确保已在 `.env` 文件中配置 OpenAI API Key
    - 支持上传多个文档建立知识库
    - 使用语义搜索查找相关内容
    - 生成的材料可用于快速复习
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>AI Paper Management Assistant v0.1.0</p>
    <p>基于 RAG (Retrieval-Augmented Generation) 架构</p>
</div>
""", unsafe_allow_html=True)
