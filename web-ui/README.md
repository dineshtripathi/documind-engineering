# 🧠 DocuMind Web UI - Complete Demo Interface

Welcome to the **DocuMind Web UI** - your lightweight, powerful interface for the entire DocuMind AI platform!

## 🚀 Quick Start

### Option 1: Start Everything (Recommended)
```bash
cd /home/dinesh/documind-engineering
./start-all-services.sh
```

### Option 2: Start Web UI Only
```bash
cd /home/dinesh/documind-engineering/web-ui
./start-ui.sh
```

## 🌟 What You Get

### 📊 **Dashboard**
- System health monitoring
- Quick actions for all services
- Real-time status of all components

### 💬 **Ask AI Interface**
- **Multi-model support**: phi3.5, DeepSeek Coder, CodeQwen
- **Task-type selection**: general, code_generation, code_explanation, technical
- **Model selection**: Auto or manual model choice
- **Temperature control**: Fine-tune response creativity
- **Source citations**: See exactly where answers come from

### 📄 **Document Ingestion**
- **Text Input**: Direct text ingestion with domain hints
- **File Upload**: Upload TXT, MD files (PDF/DOCX coming soon)
- **URL Import**: Import documents from web URLs

### 🕷️ **Web Crawler**
- **Custom Crawling**: Crawl any websites with job tracking
- **Specialized Crawlers**:
  - Python Documentation
  - Microsoft Docs
  - Stack Overflow
  - GitHub Repositories
- **Real-time Monitoring**: Track crawl progress and status
- **Background Jobs**: Non-blocking operations with job IDs

### 👁️ **Vision Analysis**
- **Image Analysis**: OCR, captioning, tagging
- **Document OCR**: Extract text from images and PDFs
- **RAG Integration**: Automatically ingest extracted content

### 🤖 **AI Agents**
- **Code Reviewer**: Comprehensive code analysis
- **Knowledge Synthesizer**: Multi-source knowledge compilation
- **Document Analyzer**: Intelligent document processing
- **Security Analyst**: Security-focused code review

### 📊 **System Status**
- **Health Checks**: Monitor all service status
- **API Documentation**: Direct links to Swagger/OpenAPI docs
- **Service Metrics**: Real-time system performance

## 🔗 Access Points

Once started, access these URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| 🌐 **Web UI** | http://localhost:8501 | Main interface |
| 📚 **RAG API Docs** | http://localhost:7001/docs | API documentation |
| 🔍 **Qdrant Dashboard** | http://localhost:6333/dashboard | Vector database |
| 🤖 **Ollama** | http://localhost:11434 | Local LLM server |

## 🎯 Key Features

### ✨ **Smart Model Selection**
The system automatically selects the best model for your task:
- **phi3.5**: General chat and document Q&A
- **DeepSeek Coder**: Code generation and technical tasks
- **CodeQwen**: Code explanation and analysis

### 🎨 **Beautiful UI**
- **Responsive design**: Works on desktop and mobile
- **Intuitive interface**: Easy to navigate and use
- **Real-time updates**: Live status and progress tracking
- **Custom styling**: Professional look and feel

### 🔄 **Background Processing**
- **Non-blocking operations**: Web crawling runs in background
- **Job tracking**: Monitor progress with unique job IDs
- **Status updates**: Real-time progress information

### 📱 **Cross-Platform**
- **Web-based**: Access from any device with a browser
- **No installation**: Just start the script and go
- **Local or remote**: Can be accessed from other machines

## 🛠️ Technical Stack

- **Frontend**: Streamlit (Python-based web framework)
- **Backend**: FastAPI with comprehensive API documentation
- **AI Models**: Multiple Ollama models with automatic selection
- **Vector DB**: Qdrant for semantic search
- **Crawling**: Async web crawling with job management

## 🚀 Why This Approach?

### ✅ **Streamlit Advantages**
- **Rapid Development**: Build UI in minutes, not hours
- **Python Native**: No JavaScript needed
- **Auto-Reactive**: UI updates automatically with data changes
- **Rich Components**: Built-in charts, file uploads, forms
- **Easy Deployment**: Single command to start

### ✅ **Maintainability**
- **Single File**: All UI logic in one place
- **Modular Functions**: Each page is a separate function
- **Easy Customization**: Simple Python code to modify
- **No Build Process**: Direct execution, no compilation

### ✅ **Integration**
- **API First**: All functionality available via REST APIs
- **Swagger Documentation**: Auto-generated API docs
- **CORS Enabled**: Web UI can access all services
- **Health Monitoring**: Built-in service health checks

## 🎉 Demo Scenarios

### 1. **Ask Questions**
- "What is the backup policy?"
- "How do I create a FastAPI endpoint?"
- "Explain async/await in Python"

### 2. **Ingest Documents**
- Upload your company policies
- Add technical documentation
- Import from URLs

### 3. **Web Crawling**
- Crawl Python documentation
- Index Microsoft Azure docs
- Process Stack Overflow content

### 4. **Vision Processing**
- Upload diagrams and charts
- Extract text from PDFs
- Analyze code screenshots

## 🛑 Stopping Services

To stop all services:
```bash
pkill -f 'streamlit|uvicorn|qdrant|ollama'
```

## 🔮 Coming Soon

- **Real-time Chat**: Live conversation interface
- **Batch Processing**: Upload multiple files at once
- **Advanced Analytics**: Usage metrics and insights
- **Custom Themes**: Personalize the interface
- **Mobile App**: Native mobile access

---

**Ready to explore?** Run `./start-all-services.sh` and visit http://localhost:8501! 🚀
