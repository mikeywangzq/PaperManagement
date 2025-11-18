"""Document management and search page."""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import networkx as nx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.document_processor import DocumentProcessor
from backend.core.classifier import Classifier
from backend.core.rag_engine import RAGEngine
from backend.models.schemas import Category
from frontend.auth import check_authentication, login_page

st.set_page_config(page_title="资料管理", page_icon="📚", layout="wide")

# Authentication check
if not check_authentication():
    login_page()
    st.stop()

# Initialize components
@st.cache_resource
def get_components():
    return {
        "doc_processor": DocumentProcessor(),
        "classifier": Classifier(),
        "rag_engine": RAGEngine()
    }

components = get_components()

st.title("📚 智能资料管理")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["文档浏览", "语义搜索", "知识图谱", "统计分析"])

# Tab 1: Browse documents
with tab1:
    st.header("文档浏览")

    docs = components["doc_processor"].list_documents()

    if not docs:
        st.info("暂无文档。请先上传文档。")
    else:
        # Filter options
        col1, col2 = st.columns(2)

        with col1:
            filter_category = st.selectbox(
                "筛选分类",
                ["全部"] + [cat.value for cat in Category]
            )

        with col2:
            search_title = st.text_input("搜索标题")

        # Filter documents
        filtered_docs = docs
        if filter_category != "全部":
            filtered_docs = [d for d in filtered_docs if d.category and d.category.value == filter_category]
        if search_title:
            filtered_docs = [d for d in filtered_docs if search_title.lower() in d.title.lower()]

        st.markdown(f"**显示 {len(filtered_docs)} 个文档**")

        # Display documents
        for doc in filtered_docs:
            with st.expander(f"📄 {doc.title}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**文档ID:** `{doc.id[:16]}`")
                    st.markdown(f"**分类:** {doc.category.value if doc.category else '未分类'}")
                    if doc.tags:
                        st.markdown(f"**标签:** {', '.join(doc.tags[:8])}")
                    st.markdown(f"**上传时间:** {doc.upload_date.strftime('%Y-%m-%d %H:%M')}")
                    if doc.num_pages:
                        st.markdown(f"**页数:** {doc.num_pages}")

                with col2:
                    if st.button("删除", key=f"del_{doc.id}"):
                        components["doc_processor"].delete_document(doc.id)
                        components["rag_engine"].delete_document(doc.id)
                        st.success("删除成功")
                        st.rerun()

# Tab 2: Semantic search
with tab2:
    st.header("语义搜索")

    st.markdown("""
    使用自然语言搜索文档内容。基于向量相似度，找到最相关的文档片段。
    """)

    search_query = st.text_area("输入搜索查询", placeholder="例如: 卷积神经网络的工作原理")

    col1, col2 = st.columns(2)
    with col1:
        search_category = st.selectbox(
            "限定分类 (可选)",
            ["全部"] + [cat.value for cat in Category],
            key="search_cat"
        )
    with col2:
        num_results = st.slider("结果数量", 1, 20, 5)

    if st.button("搜索"):
        if search_query:
            with st.spinner("搜索中..."):
                try:
                    # Build filter
                    filter_metadata = None
                    if search_category != "全部":
                        filter_metadata = {"category": search_category}

                    # Perform search
                    results = components["rag_engine"].search(
                        search_query,
                        top_k=num_results,
                        filter_metadata=filter_metadata
                    )

                    if results:
                        st.success(f"找到 {len(results)} 个相关结果")

                        for i, result in enumerate(results, 1):
                            with st.expander(f"结果 {i} - 文档 {result['metadata'].get('doc_id', 'Unknown')[:8]}"):
                                st.markdown("**内容:**")
                                st.write(result["content"])

                                st.markdown("**元数据:**")
                                st.json(result["metadata"])
                    else:
                        st.warning("未找到相关结果")

                except Exception as e:
                    st.error(f"搜索失败: {str(e)}")
        else:
            st.warning("请输入搜索查询")

# Tab 3: Knowledge graph
with tab3:
    st.header("知识图谱")

    st.markdown("""
    可视化展示文档、分类和标签之间的关系。
    """)

    if st.button("生成知识图谱"):
        with st.spinner("生成中..."):
            try:
                graph_data = components["classifier"].build_knowledge_graph_data()

                if graph_data["nodes"]:
                    # Create network graph using networkx
                    G = nx.Graph()

                    # Add nodes
                    for node in graph_data["nodes"]:
                        G.add_node(
                            node["id"],
                            label=node["label"],
                            node_type=node["type"],
                            size=node["size"]
                        )

                    # Add edges
                    for edge in graph_data["edges"]:
                        G.add_edge(edge["source"], edge["target"])

                    # Generate layout
                    pos = nx.spring_layout(G, k=0.5, iterations=50)

                    # Create plotly figure
                    edge_trace = go.Scatter(
                        x=[],
                        y=[],
                        line=dict(width=0.5, color='#888'),
                        hoverinfo='none',
                        mode='lines'
                    )

                    for edge in G.edges():
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        edge_trace['x'] += tuple([x0, x1, None])
                        edge_trace['y'] += tuple([y0, y1, None])

                    # Node traces (different colors for different types)
                    node_traces = {}
                    for node in G.nodes():
                        node_type = G.nodes[node]['node_type']
                        if node_type not in node_traces:
                            node_traces[node_type] = go.Scatter(
                                x=[],
                                y=[],
                                text=[],
                                mode='markers+text',
                                hoverinfo='text',
                                marker=dict(
                                    size=[],
                                    color={
                                        'category': '#1f77b4',
                                        'tag': '#ff7f0e',
                                        'document': '#2ca02c'
                                    }.get(node_type, '#666'),
                                    line_width=2
                                ),
                                textposition="top center",
                                name=node_type
                            )

                        x, y = pos[node]
                        node_traces[node_type]['x'] += tuple([x])
                        node_traces[node_type]['y'] += tuple([y])
                        node_traces[node_type]['text'] += tuple([G.nodes[node]['label']])
                        node_traces[node_type]['marker']['size'] += tuple([G.nodes[node]['size']])

                    # Create figure
                    fig = go.Figure(
                        data=[edge_trace] + list(node_traces.values()),
                        layout=go.Layout(
                            title='知识图谱',
                            showlegend=True,
                            hovermode='closest',
                            margin=dict(b=0, l=0, r=0, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            height=600
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Legend
                    st.markdown("""
                    **图例:**
                    - 🔵 蓝色: 分类
                    - 🟠 橙色: 标签
                    - 🟢 绿色: 文档
                    """)
                else:
                    st.info("暂无数据生成知识图谱")

            except Exception as e:
                st.error(f"生成失败: {str(e)}")

# Tab 4: Statistics
with tab4:
    st.header("统计分析")

    # Category distribution
    st.subheader("分类分布")
    category_stats = components["classifier"].get_category_statistics()

    if category_stats:
        fig = go.Figure(data=[
            go.Bar(
                x=list(category_stats.keys()),
                y=list(category_stats.values()),
                marker_color='lightblue'
            )
        ])
        fig.update_layout(
            title="文档分类分布",
            xaxis_title="分类",
            yaxis_title="文档数量",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # Tag cloud
    st.subheader("标签统计")
    tag_stats = components["classifier"].get_tag_statistics()

    if tag_stats:
        # Top 20 tags
        top_tags = dict(list(tag_stats.items())[:20])

        df = pd.DataFrame({
            "标签": list(top_tags.keys()),
            "频率": list(top_tags.values())
        })

        st.dataframe(df, use_container_width=True)

        # Bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(top_tags.values()),
                y=list(top_tags.keys()),
                orientation='h',
                marker_color='lightgreen'
            )
        ])
        fig.update_layout(
            title="热门标签 (Top 20)",
            xaxis_title="使用次数",
            yaxis_title="标签",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    # Document timeline
    st.subheader("上传时间线")
    docs = components["doc_processor"].list_documents()

    if docs:
        df_docs = pd.DataFrame([
            {
                "日期": doc.upload_date.date(),
                "文档数": 1
            }
            for doc in docs
        ])

        df_timeline = df_docs.groupby("日期").sum().reset_index()

        fig = go.Figure(data=[
            go.Scatter(
                x=df_timeline["日期"],
                y=df_timeline["文档数"],
                mode='lines+markers',
                marker_color='purple'
            )
        ])
        fig.update_layout(
            title="文档上传时间线",
            xaxis_title="日期",
            yaxis_title="文档数量",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# Sidebar
with st.sidebar:
    st.markdown("### 快速操作")

    if st.button("🔄 刷新数据"):
        st.rerun()

    st.markdown("---")

    st.markdown("### 批量操作")

    if st.button("🗑️ 清空所有文档", type="secondary"):
        if st.checkbox("确认删除所有文档"):
            components["rag_engine"].clear_all()
            st.success("所有文档已清空")
            st.rerun()
