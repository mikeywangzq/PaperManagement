"""Learning path generation page."""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.learning_path import LearningPathGenerator
from backend.models.schemas import Category

st.set_page_config(page_title="学习路线", page_icon="🗺️", layout="wide")

# Initialize components
@st.cache_resource
def get_components():
    return {
        "path_generator": LearningPathGenerator()
    }

components = get_components()

st.title("🗺️ 学习路线生成")

st.markdown("""
根据您的学习目标生成结构化的学习路径，包括前置知识、推荐资源和时间估算。
""")

# Main form
st.header("设定学习目标")

col1, col2 = st.columns([2, 1])

with col1:
    goal = st.text_area(
        "学习目标描述",
        placeholder="例如: 我想入门机器学习 或 深入理解RSA算法",
        height=100
    )

with col2:
    category_option = st.selectbox(
        "学习领域 (可选)",
        ["自动检测"] + [cat.value for cat in Category]
    )

    use_library = st.checkbox("使用我的文档库", value=True)

if st.button("生成学习路径", type="primary"):
    if goal:
        with st.spinner("生成中..."):
            try:
                # Convert category
                category = None
                if category_option != "自动检测":
                    category = Category(category_option)

                # Generate learning path
                path = components["path_generator"].generate_learning_path(
                    goal=goal,
                    category=category,
                    use_library=use_library
                )

                # Display results
                st.success("学习路径生成成功!")

                st.markdown(f"### 🎯 目标: {path.goal}")
                if path.total_estimated_time:
                    st.info(f"⏱️ 预计总时间: {path.total_estimated_time}")

                st.markdown("---")

                # Display learning path
                for i, node in enumerate(path.nodes, 1):
                    with st.expander(f"第 {i} 步: {node.title}", expanded=i==1):
                        st.markdown(f"**描述:** {node.description}")

                        if node.prerequisites:
                            st.markdown("**前置要求:**")
                            for prereq in node.prerequisites:
                                st.markdown(f"- {prereq}")

                        if node.resources:
                            st.markdown("**推荐资源:**")
                            for resource in node.resources:
                                st.markdown(f"- {resource}")
                        else:
                            st.markdown("*建议查找相关外部资源*")

                        if node.estimated_time:
                            st.markdown(f"**预计时间:** {node.estimated_time}")

                # Downloadable text version
                st.markdown("---")
                st.subheader("导出学习计划")

                text_output = f"# 学习路径: {path.goal}\n\n"
                text_output += f"预计总时间: {path.total_estimated_time}\n\n"

                for i, node in enumerate(path.nodes, 1):
                    text_output += f"## 第 {i} 步: {node.title}\n\n"
                    text_output += f"{node.description}\n\n"

                    if node.prerequisites:
                        text_output += "**前置要求:**\n"
                        for prereq in node.prerequisites:
                            text_output += f"- {prereq}\n"
                        text_output += "\n"

                    if node.resources:
                        text_output += "**推荐资源:**\n"
                        for resource in node.resources:
                            text_output += f"- {resource}\n"
                        text_output += "\n"

                    if node.estimated_time:
                        text_output += f"**预计时间:** {node.estimated_time}\n\n"

                    text_output += "---\n\n"

                st.download_button(
                    label="下载学习计划 (Markdown)",
                    data=text_output,
                    file_name="learning_path.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"生成失败: {str(e)}")
    else:
        st.warning("请输入学习目标")

# Quick templates
st.markdown("---")
st.header("快速模板")

st.markdown("点击下方模板快速生成常见学习路径：")

col1, col2 = st.columns(2)

with col1:
    if st.button("🤖 机器学习入门"):
        st.session_state['template_goal'] = "我想入门机器学习，从基础开始学习"

    if st.button("🧠 深度学习进阶"):
        st.session_state['template_goal'] = "我想深入学习深度学习，特别是CNN和Transformer"

with col2:
    if st.button("🔐 密码学基础"):
        st.session_state['template_goal'] = "我想学习密码学基础知识"

    if st.button("🔑 现代加密技术"):
        st.session_state['template_goal'] = "我想深入理解RSA、ECC等现代加密算法"

# Check prerequisites tool
st.markdown("---")
st.header("前置知识查询")

topic = st.text_input("输入主题", placeholder="例如: Transformer")

if st.button("查询前置知识"):
    if topic:
        with st.spinner("查询中..."):
            try:
                prerequisites = components["path_generator"].get_prerequisites_for_topic(topic)

                if prerequisites:
                    st.success(f"学习 {topic} 的前置知识：")
                    for i, prereq in enumerate(prerequisites, 1):
                        st.markdown(f"{i}. {prereq}")
                else:
                    st.info("未找到前置知识要求")

            except Exception as e:
                st.error(f"查询失败: {str(e)}")
    else:
        st.warning("请输入主题")

# Sidebar: Tips
with st.sidebar:
    st.markdown("### 💡 使用提示")

    st.markdown("""
    **如何使用:**
    1. 描述您的学习目标
    2. 选择学习领域（可选）
    3. 选择是否使用您的文档库
    4. 点击生成

    **提示:**
    - 目标描述越具体，路径越精准
    - 使用文档库可以匹配您已有的资料
    - 可以导出学习计划为Markdown文件
    """)

    st.markdown("---")

    st.markdown("### 📚 示例目标")

    st.markdown("""
    - "我想入门机器学习"
    - "深入理解注意力机制"
    - "学习对称加密算法"
    - "掌握数字签名技术"
    - "了解零知识证明"
    """)
