"""Exam review helper page."""
import streamlit as st
import sys
from pathlib import Path
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.review_helper import ReviewHelper
from backend.core.document_processor import DocumentProcessor
from backend.models.schemas import Category

st.set_page_config(page_title="考试复习", page_icon="📝", layout="wide")

# Initialize components
@st.cache_resource
def get_components():
    return {
        "review_helper": ReviewHelper(),
        "doc_processor": DocumentProcessor()
    }

components = get_components()

st.title("📝 考试复习助手")

st.markdown("""
生成各种复习材料帮助您高效备考，包括闪卡、速记表、概念对比和练习题。
""")

# Tabs for different review materials
tab1, tab2, tab3, tab4 = st.tabs(["闪卡", "速记表", "概念对比", "练习题"])

# Common filters
def get_filter_options():
    col1, col2 = st.columns(2)

    with col1:
        category = st.selectbox(
            "选择分类 (可选)",
            ["全部"] + [cat.value for cat in Category]
        )

    with col2:
        docs = components["doc_processor"].list_documents()
        doc_options = ["使用所有文档"] + [f"{doc.title[:40]}..." for doc in docs]
        selected_docs = st.multiselect("选择文档 (可选)", doc_options)

    return category, selected_docs, docs

# Tab 1: Flashcards
with tab1:
    st.header("📇 生成闪卡")

    topic = st.text_input("主题", placeholder="例如: 卷积神经网络")

    category, selected_docs, docs = get_filter_options()

    num_cards = st.slider("闪卡数量", 5, 30, 15)

    if st.button("生成闪卡"):
        if topic:
            with st.spinner("生成中..."):
                try:
                    # Get doc IDs
                    doc_ids = None
                    if "使用所有文档" not in selected_docs and selected_docs:
                        doc_ids = [
                            docs[doc_options.index(doc) - 1].id
                            for doc in selected_docs
                            if doc in doc_options[1:]
                        ]

                    # Get category
                    cat = Category(category) if category != "全部" else None

                    # Generate flashcards
                    flashcards = components["review_helper"].generate_flashcards(
                        topic=topic,
                        doc_ids=doc_ids,
                        category=cat,
                        num_cards=num_cards
                    )

                    if flashcards:
                        st.success(f"生成了 {len(flashcards)} 张闪卡")

                        # Initialize session state for flashcard review
                        if 'current_card' not in st.session_state:
                            st.session_state.current_card = 0
                        if 'show_answer' not in st.session_state:
                            st.session_state.show_answer = False

                        # Display current flashcard
                        card_idx = st.session_state.current_card % len(flashcards)
                        card = flashcards[card_idx]

                        st.markdown(f"### 闪卡 {card_idx + 1} / {len(flashcards)}")

                        st.info(f"**问题:** {card.question}")

                        if st.session_state.show_answer:
                            st.success(f"**答案:** {card.answer}")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            if st.button("显示/隐藏答案"):
                                st.session_state.show_answer = not st.session_state.show_answer
                                st.rerun()

                        with col2:
                            if st.button("上一张") and card_idx > 0:
                                st.session_state.current_card -= 1
                                st.session_state.show_answer = False
                                st.rerun()

                        with col3:
                            if st.button("下一张") and card_idx < len(flashcards) - 1:
                                st.session_state.current_card += 1
                                st.session_state.show_answer = False
                                st.rerun()

                        # Download all flashcards
                        st.markdown("---")
                        flashcard_text = f"# {topic} - 闪卡\n\n"
                        for i, card in enumerate(flashcards, 1):
                            flashcard_text += f"## 卡片 {i}\n\n"
                            flashcard_text += f"**问:** {card.question}\n\n"
                            flashcard_text += f"**答:** {card.answer}\n\n"
                            flashcard_text += "---\n\n"

                        st.download_button(
                            label="下载所有闪卡",
                            data=flashcard_text,
                            file_name="flashcards.md",
                            mime="text/markdown"
                        )

                    else:
                        st.warning("未能生成闪卡")

                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
        else:
            st.warning("请输入主题")

# Tab 2: Cheat sheet
with tab2:
    st.header("📄 生成速记表")

    topic = st.text_input("主题", placeholder="例如: 密码学期末复习", key="cheat_topic")

    category, selected_docs, docs = get_filter_options()

    if st.button("生成速记表"):
        if topic:
            with st.spinner("生成中..."):
                try:
                    # Get doc IDs and category
                    doc_ids = None
                    if "使用所有文档" not in selected_docs and selected_docs:
                        doc_ids = [
                            docs[doc_options.index(doc) - 1].id
                            for doc in selected_docs
                            if doc in doc_options[1:]
                        ]

                    cat = Category(category) if category != "全部" else None

                    # Generate cheat sheet
                    cheat_sheet = components["review_helper"].generate_cheat_sheet(
                        topic=topic,
                        doc_ids=doc_ids,
                        category=cat
                    )

                    st.success("速记表生成成功!")

                    st.markdown(f"## {cheat_sheet.title}")

                    for section in cheat_sheet.sections:
                        st.markdown(f"### {section['title']}")
                        st.markdown(section['content'])

                    # Download
                    st.markdown("---")
                    cheat_text = f"# {cheat_sheet.title}\n\n"
                    for section in cheat_sheet.sections:
                        cheat_text += f"## {section['title']}\n\n"
                        cheat_text += f"{section['content']}\n\n"

                    st.download_button(
                        label="下载速记表",
                        data=cheat_text,
                        file_name="cheat_sheet.md",
                        mime="text/markdown"
                    )

                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
        else:
            st.warning("请输入主题")

# Tab 3: Concept comparison
with tab3:
    st.header("⚖️ 概念对比")

    st.markdown("输入多个概念（用逗号分隔）进行对比分析")

    concepts_input = st.text_input(
        "概念列表",
        placeholder="例如: SVM, 逻辑回归, 决策树"
    )

    category, selected_docs, docs = get_filter_options()

    if st.button("生成对比"):
        if concepts_input:
            concepts = [c.strip() for c in concepts_input.split(',')]

            if len(concepts) >= 2:
                with st.spinner("生成中..."):
                    try:
                        # Get doc IDs and category
                        doc_ids = None
                        if "使用所有文档" not in selected_docs and selected_docs:
                            doc_ids = [
                                docs[doc_options.index(doc) - 1].id
                                for doc in selected_docs
                                if doc in doc_options[1:]
                            ]

                        cat = Category(category) if category != "全部" else None

                        # Generate comparison
                        comparison = components["review_helper"].compare_concepts(
                            concepts=concepts,
                            doc_ids=doc_ids,
                            category=cat
                        )

                        st.success("对比表生成成功!")

                        # Display as table
                        st.markdown("### 对比表")

                        # Create header
                        header = "| " + " | ".join(["维度"] + comparison.concepts) + " |"
                        separator = "|" + "|".join(["---"] * (len(comparison.concepts) + 1)) + "|"

                        table = header + "\n" + separator + "\n"

                        # Add rows
                        for i, dimension in enumerate(comparison.dimensions):
                            if i < len(comparison.data):
                                row_data = comparison.data[i]
                                row = "| " + " | ".join([dimension] + row_data[1:]) + " |"
                            else:
                                row = "| " + " | ".join([dimension] + [""] * len(comparison.concepts)) + " |"
                            table += row + "\n"

                        st.markdown(table)

                        # Download
                        st.download_button(
                            label="下载对比表",
                            data=table,
                            file_name="comparison.md",
                            mime="text/markdown"
                        )

                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
            else:
                st.warning("请至少输入2个概念")
        else:
            st.warning("请输入概念")

# Tab 4: Practice questions
with tab4:
    st.header("✍️ 练习题")

    topic = st.text_input("主题", placeholder="例如: 机器学习基础", key="practice_topic")

    category, selected_docs, docs = get_filter_options()

    num_questions = st.slider("题目数量", 5, 20, 10)

    if st.button("生成练习题"):
        if topic:
            with st.spinner("生成中..."):
                try:
                    # Get doc IDs and category
                    doc_ids = None
                    if "使用所有文档" not in selected_docs and selected_docs:
                        doc_ids = [
                            docs[doc_options.index(doc) - 1].id
                            for doc in selected_docs
                            if doc in doc_options[1:]
                        ]

                    cat = Category(category) if category != "全部" else None

                    # Generate questions
                    questions = components["review_helper"].generate_practice_questions(
                        topic=topic,
                        doc_ids=doc_ids,
                        category=cat,
                        num_questions=num_questions
                    )

                    if questions:
                        st.success(f"生成了 {len(questions)} 道练习题")

                        # Display questions
                        for i, q in enumerate(questions, 1):
                            with st.expander(f"第 {i} 题"):
                                st.markdown(f"**问题:** {q['question']}")

                                if st.checkbox(f"显示答案", key=f"ans_{i}"):
                                    st.info(f"**答案:** {q['answer']}")

                        # Download
                        st.markdown("---")
                        questions_text = f"# {topic} - 练习题\n\n"
                        for i, q in enumerate(questions, 1):
                            questions_text += f"## 第 {i} 题\n\n"
                            questions_text += f"**问:** {q['question']}\n\n"
                            questions_text += f"**答:** {q['answer']}\n\n"
                            questions_text += "---\n\n"

                        st.download_button(
                            label="下载所有练习题",
                            data=questions_text,
                            file_name="practice_questions.md",
                            mime="text/markdown"
                        )

                    else:
                        st.warning("未能生成练习题")

                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
        else:
            st.warning("请输入主题")

# Sidebar: Quick topics
with st.sidebar:
    st.markdown("### 💡 常见复习主题")

    st.markdown("""
    **机器学习:**
    - 监督学习算法
    - 深度学习基础
    - CNN和RNN
    - 优化算法

    **密码学:**
    - 对称加密
    - 公钥加密
    - 哈希函数
    - 数字签名
    """)

    st.markdown("---")

    st.markdown("### 📝 使用建议")

    st.markdown("""
    1. 先生成闪卡进行快速记忆
    2. 使用速记表整理核心知识
    3. 通过概念对比加深理解
    4. 用练习题进行自我检测
    """)
