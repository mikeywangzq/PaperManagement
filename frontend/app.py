"""Main Streamlit application for AI Paper Management Assistant."""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from frontend.i18n import t, language_selector
from frontend.auth import check_authentication, login_page, display_user_info

# Page configuration
st.set_page_config(
    page_title="AI Paper Management Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication check - MUST be before any other content
if not check_authentication():
    login_page()
    st.stop()  # Stop execution if not authenticated

# Custom CSS with responsive design
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

    /* Responsive design for mobile devices */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .feature-box {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .feature-title {
            font-size: 1.1rem;
        }
        /* Make columns stack on mobile */
        .row-widget.stHorizontal {
            flex-direction: column;
        }
        /* Adjust button sizes */
        .stButton > button {
            width: 100%;
        }
        /* Better spacing for mobile */
        .element-container {
            margin-bottom: 0.5rem;
        }
    }

    /* Tablet responsive */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main-header {
            font-size: 2rem;
        }
        .feature-box {
            padding: 1.2rem;
        }
    }

    /* Improve touch targets for mobile */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button {
            min-height: 44px;
            padding: 0.5rem 1rem;
        }
        .stSelectbox, .stMultiSelect {
            min-height: 44px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Language selector and user info
language_selector()
display_user_info()

# Main content
st.markdown(f'<h1 class="main-header">{t("app_title")}</h1>', unsafe_allow_html=True)

st.markdown(f"""
### {t("welcome_message")}

{t("app_description")}
""")

# Features overview
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="feature-box">
        <div class="feature-title">{t("feature_1_title")}</div>
        <p>{t("feature_1_desc")}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="feature-box">
        <div class="feature-title">{t("feature_3_title")}</div>
        <p>{t("feature_3_desc")}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="feature-box">
        <div class="feature-title">{t("feature_2_title")}</div>
        <p>{t("feature_2_desc")}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="feature-box">
        <div class="feature-title">{t("feature_4_title")}</div>
        <p>{t("feature_4_desc")}</p>
    </div>
    """, unsafe_allow_html=True)

# Quick start guide
st.markdown("---")
st.markdown(f"### 🚀 {t('get_started')}")

# Sidebar info
with st.sidebar:
    st.markdown("### 📊 System Info")
    st.info(f"""
    **Model**: {settings.llm_model}

    **Vector DB**: ChromaDB

    **Formats**: PDF, TXT, MD, DOCX, PPTX, EPUB, arXiv
    """)

    st.markdown(f"### {t('usage_tips')}")
    st.markdown("""
    💡 Configure OpenAI API Key in `.env` file

    📚 Upload multiple documents to build knowledge base

    🔍 Use semantic search to find relevant content
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>AI Paper Management Assistant v0.1.0</p>
    <p>基于 RAG (Retrieval-Augmented Generation) 架构</p>
</div>
""", unsafe_allow_html=True)
