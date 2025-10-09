# DocuMind Web UI - Streamlit Application
import streamlit as st
import requests
import json
import time
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="DocuMind AI Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
RAG_API_URL = "http://localhost:7001"
VISION_API_URL = "http://localhost:7002"
AGENTS_API_URL = "http://localhost:5076"
MAIN_API_URL = "http://localhost:5266"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .service-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
    .status-good { color: #4CAF50; font-weight: bold; }
    .status-bad { color: #f44336; font-weight: bold; }
    .model-info {
        background: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        font-size: 0.9em;
    }
    .answer-box {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .crawl-status {
        background: #fff3cd;
        padding: 0.8rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

def check_service_health(url: str, service_name: str) -> Dict:
    """Check if a service is running and healthy"""
    try:
        response = requests.get(f"{url}/healthz", timeout=5)
        if response.status_code == 200:
            return {"status": "✅ Online", "data": response.json()}
        else:
            return {"status": "❌ Error", "data": {"error": f"HTTP {response.status_code}"}}
    except Exception as e:
        return {"status": "❌ Offline", "data": {"error": str(e)}}

def make_api_request(method: str, url: str, data: Dict = None, files=None) -> Dict:
    """Make API request with error handling"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=30)
        elif method.upper() == "POST":
            if files:
                response = requests.post(url, files=files, data=data, timeout=60)
            else:
                response = requests.post(url, json=data, timeout=60)
        else:
            return {"error": f"Unsupported method: {method}"}

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 DocuMind AI Platform</h1>
        <p>Intelligent Document Processing with Multi-Model AI</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for navigation
    st.sidebar.title("🔧 Services")
    page = st.sidebar.selectbox(
        "Choose a service:",
        ["🏠 Dashboard", "💬 Ask AI", "📄 Document Ingestion", "🕷️ Web Crawler", "👁️ Vision Analysis", "🤖 Agents", "📊 System Status"]
    )

    # Add quick system status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 System Status")

    # Quick health checks
    try:
        response = requests.get(f"{RAG_API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.sidebar.success("✅ RAG API")
        else:
            st.sidebar.error("❌ RAG API")
    except:
        st.sidebar.error("❌ RAG API")

    try:
        response = requests.get("http://localhost:6333/health", timeout=2)
        if response.status_code == 200:
            st.sidebar.success("✅ Qdrant")
        else:
            st.sidebar.error("❌ Qdrant")
    except:
        st.sidebar.error("❌ Qdrant")

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            st.sidebar.success("✅ Ollama")
        else:
            st.sidebar.error("❌ Ollama")
    except:
        st.sidebar.error("❌ Ollama")

    st.sidebar.markdown("---")
    st.sidebar.info("💡 **New Features Available:**\n\n• 💬 Real-time Chat\n• 📊 Analytics Dashboard\n• 💻 Code Generator\n• 🧪 Performance Testing")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**🌐 Access Information:**")
    st.sidebar.markdown("• 🌍 Platform: Live on ngrok tunnel")
    st.sidebar.markdown("• 🔧 Local Web UI: http://localhost:8501")
    st.sidebar.markdown("• 📚 API Docs: http://localhost:7001/docs")
    st.sidebar.markdown("• 🔒 Vector DB: Local access only")

    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "💬 Ask AI":
        show_ask_interface()
    elif page == "📄 Document Ingestion":
        show_ingestion_interface()
    elif page == "🕷️ Web Crawler":
        show_crawler_interface()
    elif page == "👁️ Vision Analysis":
        show_vision_interface()
    elif page == "🤖 Agents":
        show_agents_interface()
    elif page == "📊 System Status":
        show_system_status()

def show_dashboard():
    st.header("📊 Dashboard Overview")

    # Quick system health check
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### RAG API")
        health = check_service_health(RAG_API_URL, "RAG")
        st.markdown(f"**Status:** {health['status']}")
        if health['status'] == "✅ Online" and 'available_models' in health['data']:
            st.write(f"Models: {len(health['data']['available_models'])}")

    with col2:
        st.markdown("### Vision API")
        health = check_service_health(VISION_API_URL, "Vision")
        st.markdown(f"**Status:** {health['status']}")

    with col3:
        st.markdown("### Agents API")
        health = check_service_health(AGENTS_API_URL, "Agents")
        st.markdown(f"**Status:** {health['status']}")

    with col4:
        st.markdown("### Main API")
        health = check_service_health(MAIN_API_URL, "Main")
        st.markdown(f"**Status:** {health['status']}")

    st.markdown("---")

    # Quick actions
    st.subheader("🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Quick Ask", use_container_width=True):
            st.session_state.quick_ask = True

    with col2:
        if st.button("📄 Quick Ingest", use_container_width=True):
            st.session_state.quick_ingest = True

    with col3:
        if st.button("🕷️ Start Crawl", use_container_width=True):
            st.session_state.quick_crawl = True

    # Quick Ask
    if st.session_state.get('quick_ask', False):
        st.markdown("### 💬 Quick Ask")
        query = st.text_input("Ask a question:", placeholder="What is the backup policy?")
        if st.button("Submit") and query:
            with st.spinner("Getting answer..."):
                result = make_api_request("POST", f"{RAG_API_URL}/ask", {"q": query, "task_type": "general"})
                if "error" not in result:
                    st.markdown(f"**Answer:** {result.get('answer', 'No answer')}")
                    if 'model_used' in result:
                        st.info(f"Model used: {result['model_used']}")
                else:
                    st.error(f"Error: {result['error']}")

    # Quick Ingest
    if st.session_state.get('quick_ingest', False):
        st.markdown("### 📄 Quick Ingest")
        ingest_method = st.radio("Ingestion Method:", ["Text Input", "URL", "File Upload"])

        if ingest_method == "Text Input":
            doc_id = st.text_input("Document ID:", placeholder="my-document")
            text_content = st.text_area("Text Content:", height=150, placeholder="Paste your text here...")
            if st.button("📥 Ingest Text") and doc_id and text_content:
                with st.spinner("Ingesting text..."):
                    result = make_api_request("POST", f"{RAG_API_URL}/ingest/text",
                                            {"doc_id": doc_id, "text": text_content})
                    if "error" not in result:
                        st.success(f"✅ Text ingested successfully! Chunks: {result.get('chunks', 0)}")
                    else:
                        st.error(f"Error: {result['error']}")

        elif ingest_method == "URL":
            doc_id = st.text_input("Document ID:", placeholder="webpage-content")
            url = st.text_input("URL:", placeholder="https://example.com/article")
            if st.button("🌐 Ingest URL") and doc_id and url:
                with st.spinner("Fetching and ingesting URL..."):
                    result = make_api_request("POST", f"{RAG_API_URL}/ingest/url",
                                            {"doc_id": doc_id, "url": url})
                    if "error" not in result:
                        st.success(f"✅ URL content ingested successfully! Chunks: {result.get('chunks', 0)}")
                    else:
                        st.error(f"Error: {result['error']}")

        elif ingest_method == "File Upload":
            uploaded_file = st.file_uploader("Choose a file", type=['txt', 'md', 'pdf', 'docx'])
            if uploaded_file and st.button("📁 Ingest File"):
                with st.spinner("Processing file..."):
                    files = {"file": uploaded_file.getvalue()}
                    doc_id = uploaded_file.name.split('.')[0]
                    # Note: File upload endpoint might need different handling
                    st.info("File upload implementation in progress...")

    # Quick Crawl
    if st.session_state.get('quick_crawl', False):
        st.markdown("### 🕷️ Quick Crawl")
        crawl_type = st.selectbox("Crawl Type:", [
            "General Web Crawl",
            "Python Documentation",
            "StackOverflow",
            "Microsoft Docs"
        ])

        if crawl_type == "General Web Crawl":
            url = st.text_input("URL to crawl:", placeholder="https://example.com")
            max_pages = st.slider("Max pages:", 1, 10, 3)
            if st.button("🕷️ Start Crawl") and url:
                with st.spinner("Crawling website..."):
                    result = make_api_request("POST", f"{RAG_API_URL}/crawl",
                                            {"url": url, "max_pages": max_pages})
                    if "error" not in result:
                        st.success(f"✅ Crawl completed! Pages: {result.get('pages_crawled', 0)}")
                    else:
                        st.error(f"Error: {result['error']}")

        elif crawl_type == "Python Documentation":
            topic = st.text_input("Python topic:", placeholder="asyncio")
            if st.button("📚 Crawl Python Docs") and topic:
                with st.spinner("Crawling Python documentation..."):
                    result = make_api_request("POST", f"{RAG_API_URL}/crawl/python-docs",
                                            {"topic": topic})
                    if "error" not in result:
                        st.success(f"✅ Python docs crawled successfully!")
                    else:
                        st.error(f"Error: {result['error']}")

        elif crawl_type == "StackOverflow":
            query = st.text_input("Search query:", placeholder="python async programming")
            max_questions = st.slider("Max questions:", 1, 20, 5)
            if st.button("❓ Crawl StackOverflow") and query:
                with st.spinner("Crawling StackOverflow..."):
                    result = make_api_request("POST", f"{RAG_API_URL}/crawl/stackoverflow",
                                            {"query": query, "max_questions": max_questions})
                    if "error" not in result:
                        st.success(f"✅ StackOverflow crawled successfully!")
                    else:
                        st.error(f"Error: {result['error']}")

        elif crawl_type == "Microsoft Docs":
            topic = st.text_input("Microsoft topic:", placeholder="azure-functions")
            if st.button("🏢 Crawl Microsoft Docs") and topic:
                with st.spinner("Crawling Microsoft documentation..."):
                    result = make_api_request("POST", f"{RAG_API_URL}/crawl/microsoft-docs",
                                            {"topic": topic})
                    if "error" not in result:
                        st.success(f"✅ Microsoft docs crawled successfully!")
                    else:
                        st.error(f"Error: {result['error']}")

    # Recent activity (placeholder)
    st.subheader("📈 Recent Activity")
    st.info("Activity tracking will be implemented based on your usage patterns")

def show_ask_interface():
    st.header("💬 Ask AI Assistant")

    # Model selection info
    health = check_service_health(RAG_API_URL, "RAG")
    if health['status'] == "✅ Online" and 'available_models' in health['data']:
        with st.expander("🤖 Available Models"):
            models_data = health['data']
            st.json(models_data.get('specialized_models', {}))

    # Query interface
    col1, col2 = st.columns([3, 1])

    with col1:
        query = st.text_area("Ask your question:", height=100, placeholder="How do I implement authentication in FastAPI?")

    with col2:
        task_type = st.selectbox("Task Type:", [
            "general", "code_generation", "code_explanation", "technical"
        ])

        preferred_model = st.selectbox("Preferred Model:", [
            "auto", "phi3.5:3.8b-mini-instruct-q4_0", "deepseek-coder:6.7b", "codeqwen:7b"
        ])

        temperature = st.slider("Temperature:", 0.0, 1.0, 0.1, 0.1)

    if st.button("🚀 Ask AI", use_container_width=True) and query:
        with st.spinner("🤔 AI is thinking..."):
            # Prepare request data
            request_data = {
                "q": query,
                "task_type": task_type
            }

            # Use enhanced endpoint if specific model is requested
            if preferred_model != "auto":
                endpoint = f"{RAG_API_URL}/ask-enhanced"
                request_data = {
                    "query": query,
                    "task_type": task_type,
                    "preferred_model": preferred_model,
                    "temperature": temperature,
                    "max_tokens": 1500
                }
            else:
                endpoint = f"{RAG_API_URL}/ask"

            result = make_api_request("POST", endpoint, request_data)

            if "error" not in result:
                # Display answer
                st.markdown("### 🎯 Answer")
                st.markdown(f'<div class="answer-box">{result.get("answer", "No answer provided")}</div>', unsafe_allow_html=True)

                # Display metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    if 'model_used' in result:
                        st.markdown(f'<div class="model-info">🤖 <strong>Model:</strong> {result["model_used"]}</div>', unsafe_allow_html=True)

                with col2:
                    if 'detected_domain' in result:
                        confidence = result.get('domain_confidence', 0)
                        st.markdown(f'<div class="model-info">🎯 <strong>Domain:</strong> {result["detected_domain"]} ({confidence:.2f})</div>', unsafe_allow_html=True)

                with col3:
                    if 'route' in result:
                        st.markdown(f'<div class="model-info">🛤️ <strong>Route:</strong> {result["route"]}</div>', unsafe_allow_html=True)

                # Display context sources
                if 'contextMap' in result and result['contextMap']:
                    with st.expander("📚 Sources"):
                        for idx, ctx in enumerate(result['contextMap']):
                            st.write(f"**[{ctx['index']}]** {ctx['doc_id']} (Score: {ctx['score']:.3f})")
            else:
                st.error(f"❌ Error: {result['error']}")

def show_ingestion_interface():
    st.header("📄 Document Ingestion")

    tab1, tab2, tab3 = st.tabs(["📝 Text Input", "📁 File Upload", "🌐 URL Import"])

    with tab1:
        st.subheader("Direct Text Ingestion")
        doc_id = st.text_input("Document ID:", placeholder="policy-001")
        text_content = st.text_area("Document Content:", height=200, placeholder="Enter your document text here...")
        domain_hint = st.selectbox("Domain Hint:", ["auto", "technical", "finance", "legal", "medical", "education"])

        if st.button("💾 Ingest Text") and doc_id and text_content:
            with st.spinner("Processing document..."):
                data = {"doc_id": doc_id, "text": text_content}
                if domain_hint != "auto":
                    data["domain_hint"] = domain_hint

                result = make_api_request("POST", f"{RAG_API_URL}/ingest/text", data)
                if "error" not in result:
                    st.success(f"✅ Successfully ingested {result.get('chunks', 0)} chunks!")
                else:
                    st.error(f"❌ Error: {result['error']}")

    with tab2:
        st.subheader("File Upload")
        uploaded_file = st.file_uploader("Choose a file", type=['txt', 'md', 'pdf', 'docx'])
        upload_doc_id = st.text_input("Document ID for upload:", placeholder="uploaded-doc-001")

        if uploaded_file and upload_doc_id:
            if st.button("📤 Upload and Ingest"):
                # For now, handle text files
                if uploaded_file.type == "text/plain":
                    content = uploaded_file.read().decode('utf-8')
                    with st.spinner("Processing uploaded file..."):
                        result = make_api_request("POST", f"{RAG_API_URL}/ingest/text", {
                            "doc_id": upload_doc_id,
                            "text": content
                        })
                        if "error" not in result:
                            st.success(f"✅ Successfully processed {uploaded_file.name}!")
                        else:
                            st.error(f"❌ Error: {result['error']}")
                else:
                    st.warning("📄 PDF and DOCX support will be added soon. For now, please use text files.")

    with tab3:
        st.subheader("URL Import")
        url = st.text_input("Document URL:", placeholder="https://example.com/document.pdf")
        url_doc_id = st.text_input("Document ID for URL:", placeholder="external-doc-001")

        if st.button("🌐 Import from URL") and url and url_doc_id:
            st.info("🔧 URL import functionality will be implemented in the next version.")

def show_crawler_interface():
    st.header("🕷️ Web Crawler")

    tab1, tab2, tab3 = st.tabs(["🆕 New Crawl", "📊 Job Status", "📝 Specialized Crawlers"])

    with tab1:
        st.subheader("Start New Crawl Job")

        # URL input
        urls_text = st.text_area("URLs (one per line):", height=100, placeholder="https://docs.python.org/3/\nhttps://fastapi.tiangolo.com/")

        col1, col2 = st.columns(2)
        with col1:
            max_pages = st.number_input("Max Pages:", min_value=1, max_value=100, value=10)
            delay_seconds = st.number_input("Delay (seconds):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

        with col2:
            domain_hint = st.selectbox("Domain Hint:", ["auto", "technical", "finance", "legal", "medical", "education"])
            job_id = st.text_input("Job ID (optional):", placeholder="my-crawl-job-001")

        if st.button("🚀 Start Crawling") and urls_text:
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]

            data = {
                "urls": urls,
                "max_pages": max_pages,
                "delay_seconds": delay_seconds
            }

            if domain_hint != "auto":
                data["domain_hint"] = domain_hint
            if job_id:
                data["job_id"] = job_id

            with st.spinner("Starting crawl job..."):
                result = make_api_request("POST", f"{RAG_API_URL}/crawler/crawl", data)
                if "error" not in result:
                    st.success(f"✅ Crawl job started! Job ID: {result.get('job_id')}")
                    st.session_state.current_job_id = result.get('job_id')
                else:
                    st.error(f"❌ Error: {result['error']}")

    with tab2:
        st.subheader("Job Status Monitoring")

        # Job ID input
        status_job_id = st.text_input("Job ID:", value=st.session_state.get('current_job_id', ''))

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔍 Check Status") and status_job_id:
                result = make_api_request("GET", f"{RAG_API_URL}/crawler/status/{status_job_id}")
                if "error" not in result:
                    status = result.get('status', 'unknown')

                    # Status display
                    if status == "completed":
                        st.success(f"✅ Job completed!")
                    elif status == "running":
                        st.info(f"🔄 Job is running...")
                    elif status == "failed":
                        st.error(f"❌ Job failed: {result.get('error_message', 'Unknown error')}")
                    else:
                        st.warning(f"⏳ Job status: {status}")

                    # Progress info
                    st.markdown(f"""
                    <div class="crawl-status">
                    <strong>Progress:</strong> {result.get('processed_urls', 0)}/{result.get('total_urls', 0)} URLs<br>
                    <strong>Documents Ingested:</strong> {result.get('ingested_docs', 0)}<br>
                    <strong>Started:</strong> {datetime.fromtimestamp(result.get('started_at', 0)).strftime('%Y-%m-%d %H:%M:%S') if result.get('started_at') else 'N/A'}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Error: {result['error']}")

        with col2:
            if st.button("📋 List All Jobs"):
                result = make_api_request("GET", f"{RAG_API_URL}/crawler/jobs")
                if "error" not in result and result:
                    st.subheader("Active Jobs")
                    for job in result:
                        st.write(f"**{job['job_id']}** - {job['status']}")
                else:
                    st.info("No active jobs found")

    with tab3:
        st.subheader("Specialized Crawlers")

        crawler_type = st.selectbox("Crawler Type:", [
            "Python Docs", "Microsoft Docs", "Stack Overflow", "GitHub Repository"
        ])

        if crawler_type == "Python Docs":
            topics = st.text_input("Topics (comma-separated):", placeholder="asyncio, fastapi, pydantic")
            max_pages_per_topic = st.number_input("Max pages per topic:", min_value=5, max_value=50, value=15)

            if st.button("🐍 Crawl Python Docs") and topics:
                data = {
                    "topics": [t.strip() for t in topics.split(',')],
                    "max_pages_per_topic": max_pages_per_topic,
                    "job_id": f"python-docs-{int(time.time())}"
                }

                with st.spinner("Starting Python docs crawl..."):
                    result = make_api_request("POST", f"{RAG_API_URL}/crawler/crawl-python-docs", data)
                    if "error" not in result:
                        st.success(f"✅ Python docs crawl started! Job ID: {result.get('job_id')}")
                    else:
                        st.error(f"❌ Error: {result['error']}")

def show_vision_interface():
    st.header("👁️ Vision Analysis")

    tab1, tab2 = st.tabs(["🖼️ Image Analysis", "📄 Document OCR"])

    with tab1:
        st.subheader("Image Analysis")

        # Image input options
        input_method = st.radio("Input Method:", ["Upload File", "Image URL"])

        if input_method == "Upload File":
            uploaded_image = st.file_uploader("Choose an image", type=['jpg', 'jpeg', 'png', 'pdf'])
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        else:
            image_url = st.text_input("Image URL:", placeholder="https://example.com/image.jpg")

        # Analysis options
        col1, col2 = st.columns(2)
        with col1:
            features = st.multiselect("Analysis Features:",
                                    ["Read", "Caption", "Tags"],
                                    default=["Read"])
            language = st.selectbox("Language:", ["en", "es", "fr", "de"])

        with col2:
            ingest_to_rag = st.checkbox("Ingest to RAG system")
            if ingest_to_rag:
                vision_doc_id = st.text_input("Document ID:", placeholder="vision-doc-001")

        if st.button("🔍 Analyze Image"):
            if input_method == "Image URL" and image_url:
                data = {
                    "url": image_url,
                    "language": language,
                    "features": features
                }

                if ingest_to_rag and vision_doc_id:
                    data["docId"] = vision_doc_id
                    data["ingestToRag"] = True

                with st.spinner("Analyzing image..."):
                    result = make_api_request("POST", f"{VISION_API_URL}/vision/analyze", data)
                    if "error" not in result:
                        st.success("✅ Analysis complete!")
                        st.json(result)
                    else:
                        st.error(f"❌ Error: {result['error']}")
            else:
                st.warning("Please provide an image URL or upload a file")

    with tab2:
        st.subheader("Document OCR")
        st.info("📄 Advanced OCR features will be available in the next version")

def show_agents_interface():
    st.header("🤖 AI Agents")

    tab1, tab2 = st.tabs(["📋 Agent Tasks", "🔄 Orchestration"])

    with tab1:
        st.subheader("Agent Task Execution")

        agent_type = st.selectbox("Agent Type:", [
            "Document Analyzer", "Code Reviewer", "Knowledge Synthesizer",
            "Technical Documentation", "Security Analyst"
        ])

        if agent_type == "Code Reviewer":
            code_snippet = st.text_area("Code to Review:", height=200,
                                      placeholder="async def my_function():\n    pass")
            language = st.selectbox("Programming Language:", ["python", "javascript", "csharp", "java"])

            if st.button("🔍 Review Code") and code_snippet:
                data = {
                    "codeSnippet": code_snippet,
                    "language": language,
                    "reviewLevel": "comprehensive",
                    "suggestImprovements": True,
                    "checkSecurity": True
                }

                with st.spinner("Agent is reviewing code..."):
                    result = make_api_request("POST", f"{AGENTS_API_URL}/agents/code-reviewer", data)
                    if "error" not in result:
                        st.success("✅ Code review complete!")
                        st.json(result)
                    else:
                        st.error(f"❌ Error: {result['error']}")

        elif agent_type == "Knowledge Synthesizer":
            synthesis_query = st.text_area("Query for Synthesis:",
                                         placeholder="Summarize all backup and disaster recovery procedures")

            if st.button("🧠 Synthesize Knowledge") and synthesis_query:
                data = {
                    "query": synthesis_query,
                    "sources": ["documents", "crawled_content", "vision_extracts"],
                    "synthesisLevel": "detailed",
                    "includeRecommendations": True
                }

                with st.spinner("Synthesizing knowledge..."):
                    result = make_api_request("POST", f"{AGENTS_API_URL}/agents/knowledge-synthesizer", data)
                    if "error" not in result:
                        st.success("✅ Knowledge synthesis complete!")
                        st.json(result)
                    else:
                        st.error(f"❌ Error: {result['error']}")

    with tab2:
        st.subheader("Agent Orchestration")
        st.info("🔄 Multi-agent orchestration features will be available in the next version")

def show_system_status():
    st.header("📊 System Status")

    # Service health checks
    services = [
        ("RAG API", RAG_API_URL),
        ("Vision API", VISION_API_URL),
        ("Agents API", AGENTS_API_URL),
        ("Main API", MAIN_API_URL)
    ]

    st.subheader("🏥 Service Health")

    for service_name, service_url in services:
        with st.expander(f"{service_name} Status"):
            health = check_service_health(service_url, service_name)

            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**Status:** {health['status']}")

            with col2:
                if health['status'] == "✅ Online" and 'data' in health:
                    st.json(health['data'])
                else:
                    st.error(health['data'].get('error', 'Service unavailable'))

    st.markdown("---")

    # API Documentation links
    st.subheader("📚 API Documentation")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📖 RAG API Docs"):
            st.markdown(f"[Open Swagger UI]({RAG_API_URL}/docs)")

    with col2:
        if st.button("📖 Vision API Docs"):
            st.markdown(f"[Open Swagger UI]({VISION_API_URL}/docs)")

    with col3:
        if st.button("📖 Agents API Docs"):
            st.markdown(f"[Open Swagger UI]({AGENTS_API_URL}/docs)")

    with col4:
        if st.button("📖 Main API Docs"):
            st.markdown(f"[Open Swagger UI]({MAIN_API_URL}/docs)")

if __name__ == "__main__":
    # Initialize session state
    if 'current_job_id' not in st.session_state:
        st.session_state.current_job_id = ""

    main()
