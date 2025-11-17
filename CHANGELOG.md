# Changelog

All notable changes to the AI Paper Management Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-17

### Added
- 🦙 **Local LLM Support (Ollama)**: Full integration with Ollama for privacy-focused, cost-free local inference
  - Support for LLaMA 2, LLaMA 3, Mistral, CodeLlama, and more
  - Configurable via `.env` file (`LLM_PROVIDER=ollama`)
  - Local embedding models support (nomic-embed-text)
- 🔐 **User Authentication System**: Built-in authentication with role-based access control
  - Default admin and demo accounts
  - Password hashing with SHA-256
  - User profile management
  - Session management
- 👤 **Permission Management**: Role-based access control (RBAC)
  - Admin and user roles
  - Extensible permission system
  - User info display in sidebar

### Changed
- Enhanced security with authentication layer
- Improved system architecture to support multiple LLM providers
- Updated `backend/utils/llm_utils.py` to support both OpenAI and Ollama

### Documentation
- Added FAQ Q8 about user authentication
- Added comprehensive Ollama setup guide in FAQ Q6
- Updated `.env.example` with Ollama configuration

## [0.2.0] - 2025-01-17

### Added
- 📊 **Extended Document Format Support**:
  - DOCX (Microsoft Word) - Full text and table extraction
  - PPTX (Microsoft PowerPoint) - Slide-by-slide text extraction
  - EPUB (E-books) - HTML parsing and text extraction
- 🌐 **Multi-language Interface (i18n)**:
  - Complete Chinese and English translations
  - Language switcher in sidebar
  - Dynamic language switching without page reload
  - Extensible translation system in `frontend/i18n.py`
- 📱 **Responsive Mobile Design**:
  - Mobile-friendly CSS with media queries
  - Touch-optimized UI elements (44px minimum touch targets)
  - Responsive layouts for phones, tablets, and desktops
  - Improved button and form sizing for mobile devices

### Changed
- Updated `DocumentType` enum to include DOCX, PPTX, EPUB
- Enhanced `DocumentProcessor` with new processing methods:
  - `process_docx()`: Extracts paragraphs and tables from Word documents
  - `process_pptx()`: Processes PowerPoint slides and shapes
  - `process_epub()`: Parses EPUB HTML content with BeautifulSoup
- Updated `file_utils.py` to recognize new file extensions
- Modernized frontend with responsive CSS
- Enhanced main app layout with language selection

### Documentation
- Updated README with new supported formats
- Added FAQ Q9 about language switching
- Updated upload instructions to include new formats

### Dependencies
- Added `python-pptx==0.6.23`
- Added `ebooklib==0.18`
- Added `streamlit-authenticator==0.2.3`
- Added `PyYAML==6.0.1`
- Removed duplicate `beautifulsoup4` entry

## [0.1.0] - 2025-01-15

### Added
- 🤖 **RAG-based Q&A System**: Retrieval-Augmented Generation for accurate question answering
- 📄 **Paper Summarization**: Automatic summary generation (250-500 words)
- 🔑 **Key Points Extraction**: Bullet-point extraction of core contributions
- 🏷️ **Smart Classification**: Auto-categorization into Machine Learning, Cryptography, etc.
- 🔖 **Tag Extraction**: Automatic topic tag generation (CNN, RNN, RSA, etc.)
- 🕸️ **Knowledge Graph**: Interactive visualization with NetworkX and Plotly
- 🔍 **Semantic Search**: Vector-based document retrieval with ChromaDB
- 🗺️ **Learning Path Generator**: Personalized learning roadmaps with prerequisites
- 📝 **Exam Review Tools**:
  - Flashcard generation
  - Cheat sheet creation
  - Concept comparison tables
  - Practice question generation
- 📚 **Document Management**: Upload, browse, search, and organize documents
- 📊 **Statistics Dashboard**: Category distribution, tag clouds, upload timeline
- 🌍 **Bilingual Support**: Chinese and English output for analysis results

### Technical Features
- Built on LangChain framework
- ChromaDB vector database for embeddings
- OpenAI GPT-4 and text-embedding-3-small models
- Streamlit web interface
- Support for PDF, TXT, MD, and arXiv papers
- PyMuPDF for PDF processing
- Comprehensive error handling and logging

### Documentation
- Comprehensive README with setup instructions
- FAQ section with 7 common questions
- Architecture diagrams and examples
- Development roadmap

---

## Version History Summary

- **v0.3.0**: Local LLM support + Authentication system
- **v0.2.0**: Multi-format + i18n + Responsive design
- **v0.1.0**: Initial release with core RAG features

[0.3.0]: https://github.com/yourusername/PaperManagement/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/yourusername/PaperManagement/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/PaperManagement/releases/tag/v0.1.0
