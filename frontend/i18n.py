"""Internationalization (i18n) support for the application."""
import streamlit as st
from typing import Dict, Any


# Translation dictionaries
TRANSLATIONS = {
    "zh": {
        # Common
        "language": "语言",
        "chinese": "中文",
        "english": "English",
        "home": "首页",
        "back": "返回",
        "submit": "提交",
        "cancel": "取消",
        "save": "保存",
        "delete": "删除",
        "refresh": "刷新",
        "download": "下载",
        "search": "搜索",
        "loading": "加载中...",
        "processing": "处理中...",
        "success": "成功",
        "error": "错误",
        "warning": "警告",

        # Main page
        "app_title": "🎓 AI 论文管理助手",
        "app_description": "智能化的学术资料管理与学习辅助系统",
        "welcome_message": "欢迎使用 AI 论文管理助手",
        "feature_1_title": "📄 论文总结与分析",
        "feature_1_desc": "自动总结论文内容，提取关键点，支持智能问答",
        "feature_2_title": "📚 智能资料管理",
        "feature_2_desc": "自动分类、标签提取、语义搜索和知识图谱",
        "feature_3_title": "🗺️ 学习路线生成",
        "feature_3_desc": "根据学习目标生成结构化学习路径",
        "feature_4_title": "📝 考试复习助手",
        "feature_4_desc": "生成闪卡、速记表、对比表和练习题",
        "get_started": "开始使用",

        # Paper Summary Page
        "paper_summary": "论文总结",
        "upload_document": "上传文档",
        "document_analysis": "文档分析",
        "intelligent_qa": "智能问答",
        "upload_method": "选择上传方式",
        "upload_local": "上传本地文件",
        "import_arxiv": "从 arXiv 导入",
        "select_files": "选择文件",
        "process_documents": "处理文档",
        "arxiv_id": "输入 arXiv ID",
        "import_paper": "导入论文",
        "no_documents": "暂无文档。请先上传文档。",
        "select_document": "选择文档",
        "analysis_options": "分析选项",
        "output_language": "输出语言",
        "analysis_type": "选择分析类型",
        "summary": "摘要",
        "key_points": "关键点",
        "full_analysis": "完整分析",
        "start_analysis": "开始分析",
        "methodology": "方法论",
        "contributions": "主要贡献",
        "conclusions": "结论",
        "datasets_used": "使用的数据集",
        "question": "输入问题",
        "ask_question": "提问",
        "answer": "答案",
        "sources": "查看来源",
        "source": "来源",
        "document": "文档",

        # Document Management Page
        "document_management": "资料管理",
        "browse_documents": "文档浏览",
        "semantic_search": "语义搜索",
        "knowledge_graph": "知识图谱",
        "statistics": "统计分析",
        "filter_category": "筛选分类",
        "all": "全部",
        "machine_learning": "机器学习",
        "cryptography": "密码学",
        "other": "其他",
        "search_title": "搜索标题",
        "showing_documents": "显示 {count} 个文档",
        "document_id": "文档ID",
        "category": "分类",
        "tags": "标签",
        "upload_date": "上传时间",
        "num_pages": "页数",
        "delete_success": "删除成功",
        "search_query": "输入搜索查询",
        "num_results": "结果数量",
        "search_results": "找到 {count} 个相关结果",
        "no_results": "未找到相关结果",
        "generate_graph": "生成知识图谱",
        "category_distribution": "分类分布",
        "tag_statistics": "标签统计",
        "upload_timeline": "上传时间线",
        "clear_all": "清空所有文档",
        "confirm_delete": "确认删除所有文档",

        # Learning Path Page
        "learning_path": "学习路线",
        "set_goal": "设定学习目标",
        "goal_description": "学习目标描述",
        "learning_domain": "学习领域",
        "auto_detect": "自动检测",
        "use_library": "使用我的文档库",
        "generate_path": "生成学习路径",
        "goal": "目标",
        "estimated_time": "预计总时间",
        "step": "第 {num} 步",
        "description": "描述",
        "prerequisites": "前置要求",
        "resources": "推荐资源",
        "export_plan": "导出学习计划",
        "quick_templates": "快速模板",
        "ml_basics": "机器学习入门",
        "dl_advanced": "深度学习进阶",
        "crypto_basics": "密码学基础",
        "modern_encryption": "现代加密技术",
        "check_prerequisites": "前置知识查询",
        "enter_topic": "输入主题",
        "query_prerequisites": "查询前置知识",

        # Review Helper Page
        "exam_review": "考试复习",
        "flashcards": "闪卡",
        "cheat_sheet": "速记表",
        "concept_comparison": "概念对比",
        "practice_questions": "练习题",
        "topic": "主题",
        "generate_flashcards": "生成闪卡",
        "num_cards": "闪卡数量",
        "card": "闪卡",
        "show_answer": "显示/隐藏答案",
        "previous": "上一张",
        "next": "下一张",
        "download_all_cards": "下载所有闪卡",
        "generate_cheat_sheet": "生成速记表",
        "concept_list": "概念列表",
        "generate_comparison": "生成对比",
        "comparison_table": "对比表",
        "dimension": "维度",
        "num_questions": "题目数量",
        "generate_questions": "生成练习题",
        "question_num": "第 {num} 题",
        "download_all_questions": "下载所有练习题",

        # Sidebar
        "document_stats": "文档统计",
        "total_documents": "文档总数",
        "popular_tags": "热门标签",
        "quick_actions": "快速操作",
        "batch_operations": "批量操作",
        "usage_tips": "使用提示",
        "example_goals": "示例目标",
        "common_topics": "常见复习主题",
        "usage_suggestions": "使用建议",
    },

    "en": {
        # Common
        "language": "Language",
        "chinese": "中文",
        "english": "English",
        "home": "Home",
        "back": "Back",
        "submit": "Submit",
        "cancel": "Cancel",
        "save": "Save",
        "delete": "Delete",
        "refresh": "Refresh",
        "download": "Download",
        "search": "Search",
        "loading": "Loading...",
        "processing": "Processing...",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",

        # Main page
        "app_title": "🎓 AI Paper Management Assistant",
        "app_description": "Intelligent Academic Material Management and Learning Assistant System",
        "welcome_message": "Welcome to AI Paper Management Assistant",
        "feature_1_title": "📄 Paper Summarization & Analysis",
        "feature_1_desc": "Automatically summarize papers, extract key points, support intelligent Q&A",
        "feature_2_title": "📚 Intelligent Document Management",
        "feature_2_desc": "Auto-classification, tag extraction, semantic search and knowledge graph",
        "feature_3_title": "🗺️ Learning Path Generation",
        "feature_3_desc": "Generate structured learning paths based on your goals",
        "feature_4_title": "📝 Exam Review Assistant",
        "feature_4_desc": "Generate flashcards, cheat sheets, comparison tables and practice questions",
        "get_started": "Get Started",

        # Paper Summary Page
        "paper_summary": "Paper Summary",
        "upload_document": "Upload Document",
        "document_analysis": "Document Analysis",
        "intelligent_qa": "Intelligent Q&A",
        "upload_method": "Select Upload Method",
        "upload_local": "Upload Local File",
        "import_arxiv": "Import from arXiv",
        "select_files": "Select Files",
        "process_documents": "Process Documents",
        "arxiv_id": "Enter arXiv ID",
        "import_paper": "Import Paper",
        "no_documents": "No documents yet. Please upload documents first.",
        "select_document": "Select Document",
        "analysis_options": "Analysis Options",
        "output_language": "Output Language",
        "analysis_type": "Select Analysis Type",
        "summary": "Summary",
        "key_points": "Key Points",
        "full_analysis": "Full Analysis",
        "start_analysis": "Start Analysis",
        "methodology": "Methodology",
        "contributions": "Main Contributions",
        "conclusions": "Conclusions",
        "datasets_used": "Datasets Used",
        "question": "Enter Question",
        "ask_question": "Ask",
        "answer": "Answer",
        "sources": "View Sources",
        "source": "Source",
        "document": "Document",

        # Document Management Page
        "document_management": "Document Management",
        "browse_documents": "Browse Documents",
        "semantic_search": "Semantic Search",
        "knowledge_graph": "Knowledge Graph",
        "statistics": "Statistics",
        "filter_category": "Filter Category",
        "all": "All",
        "machine_learning": "Machine Learning",
        "cryptography": "Cryptography",
        "other": "Other",
        "search_title": "Search Title",
        "showing_documents": "Showing {count} documents",
        "document_id": "Document ID",
        "category": "Category",
        "tags": "Tags",
        "upload_date": "Upload Date",
        "num_pages": "Pages",
        "delete_success": "Deleted successfully",
        "search_query": "Enter search query",
        "num_results": "Number of Results",
        "search_results": "Found {count} relevant results",
        "no_results": "No results found",
        "generate_graph": "Generate Knowledge Graph",
        "category_distribution": "Category Distribution",
        "tag_statistics": "Tag Statistics",
        "upload_timeline": "Upload Timeline",
        "clear_all": "Clear All Documents",
        "confirm_delete": "Confirm delete all documents",

        # Learning Path Page
        "learning_path": "Learning Path",
        "set_goal": "Set Learning Goal",
        "goal_description": "Goal Description",
        "learning_domain": "Learning Domain",
        "auto_detect": "Auto Detect",
        "use_library": "Use My Document Library",
        "generate_path": "Generate Learning Path",
        "goal": "Goal",
        "estimated_time": "Total Estimated Time",
        "step": "Step {num}",
        "description": "Description",
        "prerequisites": "Prerequisites",
        "resources": "Recommended Resources",
        "export_plan": "Export Learning Plan",
        "quick_templates": "Quick Templates",
        "ml_basics": "Machine Learning Basics",
        "dl_advanced": "Deep Learning Advanced",
        "crypto_basics": "Cryptography Basics",
        "modern_encryption": "Modern Encryption",
        "check_prerequisites": "Check Prerequisites",
        "enter_topic": "Enter Topic",
        "query_prerequisites": "Query Prerequisites",

        # Review Helper Page
        "exam_review": "Exam Review",
        "flashcards": "Flashcards",
        "cheat_sheet": "Cheat Sheet",
        "concept_comparison": "Concept Comparison",
        "practice_questions": "Practice Questions",
        "topic": "Topic",
        "generate_flashcards": "Generate Flashcards",
        "num_cards": "Number of Cards",
        "card": "Card",
        "show_answer": "Show/Hide Answer",
        "previous": "Previous",
        "next": "Next",
        "download_all_cards": "Download All Cards",
        "generate_cheat_sheet": "Generate Cheat Sheet",
        "concept_list": "Concept List",
        "generate_comparison": "Generate Comparison",
        "comparison_table": "Comparison Table",
        "dimension": "Dimension",
        "num_questions": "Number of Questions",
        "generate_questions": "Generate Questions",
        "question_num": "Question {num}",
        "download_all_questions": "Download All Questions",

        # Sidebar
        "document_stats": "Document Statistics",
        "total_documents": "Total Documents",
        "popular_tags": "Popular Tags",
        "quick_actions": "Quick Actions",
        "batch_operations": "Batch Operations",
        "usage_tips": "Usage Tips",
        "example_goals": "Example Goals",
        "common_topics": "Common Review Topics",
        "usage_suggestions": "Usage Suggestions",
    }
}


def get_language() -> str:
    """Get current language from session state."""
    if "language" not in st.session_state:
        st.session_state.language = "zh"  # Default to Chinese
    return st.session_state.language


def set_language(lang: str) -> None:
    """Set current language in session state."""
    st.session_state.language = lang


def t(key: str, **kwargs) -> str:
    """
    Translate a key to current language.

    Args:
        key: Translation key
        **kwargs: Format parameters for string interpolation

    Returns:
        Translated string
    """
    lang = get_language()
    translation = TRANSLATIONS.get(lang, {}).get(key, key)

    # Apply string formatting if kwargs provided
    if kwargs:
        try:
            translation = translation.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return translation


def language_selector():
    """Display language selector in sidebar."""
    with st.sidebar:
        st.markdown("---")
        current_lang = get_language()

        # Language options
        lang_options = {
            "zh": "🇨🇳 中文",
            "en": "🇬🇧 English"
        }

        selected_lang_label = st.selectbox(
            t("language"),
            options=list(lang_options.values()),
            index=0 if current_lang == "zh" else 1
        )

        # Get language code from label
        selected_lang = "zh" if "中文" in selected_lang_label else "en"

        # Update language if changed
        if selected_lang != current_lang:
            set_language(selected_lang)
            st.rerun()
