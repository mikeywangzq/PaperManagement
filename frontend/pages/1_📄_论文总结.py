"""Paper summarization page."""
import streamlit as st
import sys
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.document_processor import DocumentProcessor
from backend.core.summarizer import Summarizer
from backend.core.classifier import Classifier
from backend.core.rag_engine import RAGEngine
from backend.models.schemas import Query
from config.settings import settings

st.set_page_config(page_title="论文总结", page_icon="📄", layout="wide")

# Initialize components
@st.cache_resource
def get_components():
    return {
        "doc_processor": DocumentProcessor(),
        "summarizer": Summarizer(),
        "classifier": Classifier(),
        "rag_engine": RAGEngine()
    }

components = get_components()

st.title("📄 论文总结与分析")

# Tabs for different functions
tab1, tab2, tab3 = st.tabs(["上传文档", "文档分析", "智能问答"])

# Tab 1: Upload documents
with tab1:
    st.header("上传文档")

    upload_method = st.radio(
        "选择上传方式",
        ["上传本地文件", "从 arXiv 导入"]
    )

    if upload_method == "上传本地文件":
        uploaded_files = st.file_uploader(
            "选择文件 (PDF, TXT, MD, DOCX, PPTX, EPUB)",
            type=["pdf", "txt", "md", "docx", "pptx", "epub"],
            accept_multiple_files=True
        )

        if uploaded_files:
            if st.button("处理文档"):
                progress_bar = st.progress(0)
                status = st.empty()

                for i, uploaded_file in enumerate(uploaded_files):
                    status.text(f"处理中: {uploaded_file.name}")

                    # Save file
                    file_path = Path(settings.document_path) / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    try:
                        # Process document
                        doc = components["doc_processor"].save_document(str(file_path))

                        # Classify
                        classification = components["classifier"].classify_document(doc.id)

                        # Add to RAG
                        text = components["doc_processor"].get_document_text(doc.id)
                        components["rag_engine"].add_document(
                            doc.id,
                            text,
                            {
                                "title": doc.title,
                                "category": classification.category.value,
                                "tags": classification.tags
                            }
                        )

                        st.success(f"✅ {uploaded_file.name} 处理完成")
                        st.info(f"分类: {classification.category.value} | 标签: {', '.join(classification.tags[:5])}")

                    except Exception as e:
                        st.error(f"❌ 处理失败: {str(e)}")

                    progress_bar.progress((i + 1) / len(uploaded_files))

                status.text("所有文档处理完成!")

    else:  # arXiv import
        arxiv_id = st.text_input("输入 arXiv ID (例如: 2301.12345)")

        if st.button("导入论文"):
            if arxiv_id:
                try:
                    with st.spinner("正在从 arXiv 下载..."):
                        doc = components["doc_processor"].save_document(
                            "",
                            arxiv_id=arxiv_id
                        )

                        # Classify
                        classification = components["classifier"].classify_document(doc.id)

                        # Add to RAG
                        text = components["doc_processor"].get_document_text(doc.id)
                        components["rag_engine"].add_document(
                            doc.id,
                            text,
                            {
                                "title": doc.title,
                                "category": classification.category.value,
                                "tags": classification.tags
                            }
                        )

                        st.success(f"✅ 论文导入成功: {doc.title}")
                        st.info(f"分类: {classification.category.value} | 标签: {', '.join(classification.tags[:5])}")

                except Exception as e:
                    st.error(f"❌ 导入失败: {str(e)}")
            else:
                st.warning("请输入有效的 arXiv ID")

# Tab 2: Analyze documents
with tab2:
    st.header("文档分析")

    docs = components["doc_processor"].list_documents()

    if not docs:
        st.info("暂无文档。请先上传文档。")
    else:
        # Select document
        doc_options = {f"{doc.title} ({doc.id[:8]})": doc.id for doc in docs}
        selected_doc_label = st.selectbox("选择文档", list(doc_options.keys()))
        selected_doc_id = doc_options[selected_doc_label]

        # Analysis options
        st.subheader("分析选项")

        col1, col2 = st.columns(2)

        with col1:
            language = st.selectbox("输出语言", ["中文 (zh)", "英文 (en)"])
            lang_code = "zh" if "中文" in language else "en"

        with col2:
            analysis_type = st.multiselect(
                "选择分析类型",
                ["摘要", "关键点", "完整分析"],
                default=["摘要", "关键点"]
            )

        if st.button("开始分析"):
            with st.spinner("分析中..."):
                try:
                    if "摘要" in analysis_type:
                        st.subheader("📝 摘要")
                        summary = components["summarizer"].generate_summary(
                            selected_doc_id,
                            language=lang_code
                        )
                        st.write(summary)

                    if "关键点" in analysis_type:
                        st.subheader("🔑 关键点")
                        key_points = components["summarizer"].extract_key_points(
                            selected_doc_id,
                            language=lang_code
                        )
                        for i, point in enumerate(key_points, 1):
                            st.markdown(f"{i}. {point}")

                    if "完整分析" in analysis_type:
                        st.subheader("📊 完整分析")
                        analysis = components["summarizer"].generate_full_analysis(
                            selected_doc_id,
                            language=lang_code
                        )

                        st.markdown("**方法论:**")
                        st.write(analysis.methodology or "未提取")

                        st.markdown("**主要贡献:**")
                        for contrib in analysis.contributions:
                            st.markdown(f"- {contrib}")

                        st.markdown("**结论:**")
                        st.write(analysis.conclusions or "未提取")

                        if analysis.datasets_used:
                            st.markdown("**使用的数据集:**")
                            st.write(", ".join(analysis.datasets_used))

                except Exception as e:
                    st.error(f"分析失败: {str(e)}")

# Tab 3: Q&A
with tab3:
    st.header("智能问答")

    st.markdown("""
    基于已上传的文档回答问题。使用 RAG (Retrieval-Augmented Generation) 技术确保答案准确。
    """)

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        filter_category = st.selectbox(
            "筛选分类 (可选)",
            ["全部", "机器学习", "密码学", "其他"]
        )

    with col2:
        top_k = st.slider("检索文档数量", 1, 10, 5)

    # Question input
    question = st.text_area("输入问题", placeholder="例如: 作者使用了什么数据集?")

    if st.button("提问"):
        if question:
            with st.spinner("思考中..."):
                try:
                    # Build query
                    category_map = {
                        "机器学习": "machine_learning",
                        "密码学": "cryptography",
                        "其他": "other"
                    }

                    query = Query(
                        question=question,
                        category=category_map.get(filter_category) if filter_category != "全部" else None,
                        top_k=top_k
                    )

                    # Get answer
                    response = components["rag_engine"].query(query)

                    st.subheader("💡 答案")
                    st.write(response.answer)

                    # Show sources
                    with st.expander("📚 查看来源"):
                        for i, source in enumerate(response.sources, 1):
                            st.markdown(f"**来源 {i}:**")
                            st.text(source["content"][:300] + "...")
                            st.caption(f"文档: {source['metadata'].get('doc_id', 'Unknown')}")
                            st.markdown("---")

                except Exception as e:
                    st.error(f"查询失败: {str(e)}")
        else:
            st.warning("请输入问题")

# Sidebar: Document stats
with st.sidebar:
    st.markdown("### 📊 文档统计")

    docs = components["doc_processor"].list_documents()
    st.metric("文档总数", len(docs))

    category_stats = components["classifier"].get_category_statistics()
    if category_stats:
        st.markdown("**分类分布:**")
        for cat, count in category_stats.items():
            st.text(f"- {cat}: {count}")

    tag_stats = components["classifier"].get_tag_statistics()
    if tag_stats:
        st.markdown("**热门标签:**")
        for tag, count in list(tag_stats.items())[:5]:
            st.text(f"- {tag}: {count}")
