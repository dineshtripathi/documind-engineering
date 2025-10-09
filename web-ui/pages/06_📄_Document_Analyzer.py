"""
Advanced Document Analysis & Summarization Suite
AI-powered document processing with multi-format support
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import tempfile
import os
import PyPDF2
import docx
from io import BytesIO
import base64

class DocumentAnalyzer:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.supported_formats = {
            "pdf": {"extension": ".pdf", "mime": "application/pdf"},
            "docx": {"extension": ".docx", "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
            "txt": {"extension": ".txt", "mime": "text/plain"},
            "md": {"extension": ".md", "mime": "text/markdown"},
            "json": {"extension": ".json", "mime": "application/json"},
            "csv": {"extension": ".csv", "mime": "text/csv"}
        }

        self.analysis_types = {
            "comprehensive": "Complete analysis with summary, key points, and insights",
            "executive_summary": "High-level executive summary for business stakeholders",
            "technical_review": "Technical analysis focusing on implementation details",
            "compliance_check": "Compliance and regulatory analysis",
            "sentiment_analysis": "Sentiment and tone analysis",
            "keyword_extraction": "Key terms and concept extraction",
            "structure_analysis": "Document structure and organization analysis"
        }

    def extract_text_from_file(self, uploaded_file) -> str:
        """Extract text from uploaded file based on format"""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()

            if file_extension == 'pdf':
                return self.extract_pdf_text(uploaded_file)
            elif file_extension == 'docx':
                return self.extract_docx_text(uploaded_file)
            elif file_extension in ['txt', 'md']:
                return str(uploaded_file.read(), "utf-8")
            elif file_extension == 'json':
                json_data = json.loads(uploaded_file.read())
                return json.dumps(json_data, indent=2)
            elif file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
                return df.to_string()
            else:
                return "Unsupported file format"

        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def extract_pdf_text(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def extract_docx_text(self, docx_file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(BytesIO(docx_file.read()))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"

    def analyze_document(self, text: str, analysis_type: str, custom_prompt: str = "") -> Dict:
        """Analyze document using AI"""
        try:
            # Create analysis prompt based on type
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = self.create_analysis_prompt(text, analysis_type)

            payload = {
                "q": prompt,
                "context_limit": 8,
                "model_preference": "llama3.1:70b"  # Use most powerful model for analysis
            }

            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=120  # Longer timeout for complex analysis
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "analysis": result.get("answer", ""),
                    "model_used": result.get("model_used", "unknown"),
                    "analysis_time": datetime.now().isoformat(),
                    "word_count": len(text.split()),
                    "char_count": len(text)
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_analysis_prompt(self, text: str, analysis_type: str) -> str:
        """Create specialized analysis prompt based on type"""
        base_prompt = f"Analyze the following document:\n\n{text[:8000]}...\n\n"  # Limit text length

        prompts = {
            "comprehensive": base_prompt + """
            Provide a comprehensive analysis including:
            1. Executive Summary (2-3 sentences)
            2. Key Points and Main Topics
            3. Important Insights and Conclusions
            4. Actionable Recommendations
            5. Critical Information Highlights
            Format your response clearly with headers and bullet points.
            """,

            "executive_summary": base_prompt + """
            Create an executive summary suitable for business stakeholders:
            1. One-paragraph overview of the document's purpose and scope
            2. Three key findings or conclusions
            3. Primary recommendations or next steps
            4. Business impact assessment
            Keep it concise and focused on business value.
            """,

            "technical_review": base_prompt + """
            Perform a technical analysis focusing on:
            1. Technical concepts and methodologies mentioned
            2. Implementation details and specifications
            3. Technical challenges or limitations identified
            4. Best practices and standards compliance
            5. Technical recommendations for improvement
            """,

            "compliance_check": base_prompt + """
            Review for compliance and regulatory considerations:
            1. Regulatory requirements mentioned or implied
            2. Compliance gaps or risks identified
            3. Data privacy and security considerations
            4. Audit trail and documentation adequacy
            5. Recommended compliance actions
            """,

            "sentiment_analysis": base_prompt + """
            Analyze the sentiment and tone:
            1. Overall sentiment (positive, negative, neutral)
            2. Emotional tone and writing style
            3. Key sentiment indicators and phrases
            4. Audience and purpose assessment
            5. Communication effectiveness evaluation
            """,

            "keyword_extraction": base_prompt + """
            Extract and analyze key information:
            1. Most important keywords and phrases (top 20)
            2. Key concepts and themes
            3. Named entities (people, organizations, locations, dates)
            4. Technical terms and jargon
            5. Category classification of the document
            """,

            "structure_analysis": base_prompt + """
            Analyze document structure and organization:
            1. Document type and format assessment
            2. Structural organization and flow
            3. Section breakdown and hierarchy
            4. Information density and readability
            5. Suggestions for structural improvement
            """
        }

        return prompts.get(analysis_type, prompts["comprehensive"])

    def generate_document_insights(self, text: str) -> Dict:
        """Generate comprehensive document insights"""
        insights = {
            "basic_stats": {
                "word_count": len(text.split()),
                "char_count": len(text),
                "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
                "sentence_count": len([s for s in text.split('.') if s.strip()])
            },
            "readability": self.calculate_readability(text),
            "structure": self.analyze_structure(text)
        }

        return insights

    def calculate_readability(self, text: str) -> Dict:
        """Calculate basic readability metrics"""
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]

        if not words or not sentences:
            return {"error": "Insufficient text for analysis"}

        avg_words_per_sentence = len(words) / len(sentences)
        avg_chars_per_word = sum(len(word) for word in words) / len(words)

        # Simple readability score (approximate)
        readability_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_chars_per_word / 100)

        return {
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "avg_chars_per_word": round(avg_chars_per_word, 2),
            "readability_score": round(readability_score, 1),
            "readability_level": self.get_readability_level(readability_score)
        }

    def get_readability_level(self, score: float) -> str:
        """Convert readability score to level"""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"

    def analyze_structure(self, text: str) -> Dict:
        """Analyze document structure"""
        lines = text.split('\n')

        structure = {
            "total_lines": len(lines),
            "empty_lines": len([line for line in lines if not line.strip()]),
            "headings": len([line for line in lines if line.strip() and (line.startswith('#') or line.isupper())]),
            "bullet_points": len([line for line in lines if line.strip().startswith(('-', '*', '•'))]),
            "numbered_items": len([line for line in lines if line.strip() and line[0].isdigit()])
        }

        return structure

    def render_document_upload(self):
        """Render document upload interface"""
        st.header("📄 Advanced Document Analysis")
        st.markdown("Upload documents for AI-powered analysis and insights")

        # File upload
        uploaded_file = st.file_uploader(
            "Choose a document to analyze:",
            type=['pdf', 'docx', 'txt', 'md', 'json', 'csv'],
            help="Supported formats: PDF, DOCX, TXT, MD, JSON, CSV"
        )

        if uploaded_file:
            # Display file info
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("File Size", f"{uploaded_file.size:,} bytes")

            with col2:
                st.metric("File Type", uploaded_file.type)

            with col3:
                st.metric("File Name", uploaded_file.name)

            # Extract text
            with st.spinner("Extracting text from document..."):
                text = self.extract_text_from_file(uploaded_file)

            if text.startswith("Error"):
                st.error(text)
                return

            # Store in session state
            st.session_state.document_text = text
            st.session_state.document_name = uploaded_file.name

            # Show text preview
            with st.expander("📖 Document Preview"):
                st.text_area("Document Content (first 1000 characters):", text[:1000], height=200)

            # Quick insights
            insights = self.generate_document_insights(text)

            st.subheader("📊 Document Insights")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Word Count", f"{insights['basic_stats']['word_count']:,}")

            with col2:
                st.metric("Characters", f"{insights['basic_stats']['char_count']:,}")

            with col3:
                st.metric("Paragraphs", insights['basic_stats']['paragraph_count'])

            with col4:
                if 'readability' in insights:
                    st.metric("Readability", insights['readability'].get('readability_level', 'Unknown'))

            # Analysis options
            self.render_analysis_options()

    def render_analysis_options(self):
        """Render analysis options interface"""
        if 'document_text' not in st.session_state:
            st.info("👆 Upload a document first to see analysis options")
            return

        st.markdown("---")
        st.subheader("🔍 Analysis Options")

        col1, col2 = st.columns([2, 1])

        with col1:
            analysis_type = st.selectbox(
                "Select Analysis Type:",
                options=list(self.analysis_types.keys()),
                format_func=lambda x: f"{x.replace('_', ' ').title()} - {self.analysis_types[x]}"
            )

            use_custom_prompt = st.checkbox("Use Custom Analysis Prompt")

            custom_prompt = ""
            if use_custom_prompt:
                custom_prompt = st.text_area(
                    "Custom Analysis Prompt:",
                    placeholder="Enter your specific analysis requirements...",
                    height=100
                )

        with col2:
            st.markdown("**Analysis Details:**")
            st.write(self.analysis_types[analysis_type])

            st.markdown("**Model Selection:**")
            model_options = {
                "llama3.1:70b": "🚀 Llama 3.1 70B (Best)",
                "llama3.1:8b": "🧠 Llama 3.1 8B",
                "phi3.5": "⚡ phi3.5 (Fast)"
            }

            selected_model = st.selectbox(
                "AI Model:",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x]
            )

        # Analysis button
        if st.button("🚀 Start Analysis", type="primary"):
            self.run_document_analysis(analysis_type, custom_prompt, selected_model)

    def run_document_analysis(self, analysis_type: str, custom_prompt: str, model: str):
        """Run document analysis"""
        text = st.session_state.document_text

        st.markdown("---")
        st.subheader("📋 Analysis Results")

        with st.spinner(f"Analyzing document using {model}..."):
            # Update the API call to use selected model
            prompt = custom_prompt if custom_prompt else self.create_analysis_prompt(text, analysis_type)

            payload = {
                "q": prompt,
                "context_limit": 8,
                "model_preference": model
            }

            result = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=120
            )

        if result.status_code == 200:
            analysis_result = result.json()

            # Display analysis
            st.success(f"✅ Analysis completed using {analysis_result.get('model_used', 'AI')}")

            # Analysis content
            st.markdown("### 📄 Analysis Report")
            st.markdown(analysis_result.get("answer", "No analysis generated"))

            # Save to session state
            if 'analysis_history' not in st.session_state:
                st.session_state.analysis_history = []

            st.session_state.analysis_history.append({
                "document_name": st.session_state.document_name,
                "analysis_type": analysis_type,
                "result": analysis_result.get("answer", ""),
                "model_used": analysis_result.get('model_used', 'unknown'),
                "timestamp": datetime.now().isoformat()
            })

            # Additional insights
            self.render_analysis_insights(text, analysis_result)

        else:
            st.error(f"Analysis failed: {result.status_code}")

    def render_analysis_insights(self, text: str, analysis_result: Dict):
        """Render additional analysis insights"""
        st.markdown("---")
        st.subheader("📊 Additional Insights")

        col1, col2 = st.columns(2)

        with col1:
            # Document statistics
            st.markdown("#### 📈 Document Statistics")
            insights = self.generate_document_insights(text)

            stats_df = pd.DataFrame([
                {"Metric": "Words", "Value": insights['basic_stats']['word_count']},
                {"Metric": "Characters", "Value": insights['basic_stats']['char_count']},
                {"Metric": "Paragraphs", "Value": insights['basic_stats']['paragraph_count']},
                {"Metric": "Sentences", "Value": insights['basic_stats']['sentence_count']}
            ])

            fig = px.bar(stats_df, x='Metric', y='Value', title='Document Statistics')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Readability analysis
            st.markdown("#### 📚 Readability Analysis")
            if 'readability' in insights:
                readability = insights['readability']

                st.metric("Readability Score", f"{readability['readability_score']:.1f}")
                st.metric("Reading Level", readability['readability_level'])
                st.metric("Avg Words/Sentence", f"{readability['avg_words_per_sentence']:.1f}")
                st.metric("Avg Chars/Word", f"{readability['avg_chars_per_word']:.1f}")

        # Export options
        self.render_export_options(analysis_result)

    def render_export_options(self, analysis_result: Dict):
        """Render export options"""
        st.markdown("---")
        st.subheader("📥 Export Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Export as Text"):
                analysis_text = f"""
DOCUMENT ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Document: {st.session_state.get('document_name', 'Unknown')}
Model: {analysis_result.get('model_used', 'Unknown')}

{analysis_result.get('answer', 'No analysis available')}
"""
                st.download_button(
                    label="Download Text Report",
                    data=analysis_text,
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

        with col2:
            if st.button("📊 Export as JSON"):
                export_data = {
                    "document_name": st.session_state.get('document_name', 'Unknown'),
                    "analysis_timestamp": datetime.now().isoformat(),
                    "model_used": analysis_result.get('model_used', 'Unknown'),
                    "analysis_result": analysis_result.get('answer', ''),
                    "document_stats": self.generate_document_insights(st.session_state.get('document_text', ''))
                }

                st.download_button(
                    label="Download JSON Report",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col3:
            if st.button("📧 Generate Summary"):
                summary = f"Document analysis completed for '{st.session_state.get('document_name', 'Unknown')}' using {analysis_result.get('model_used', 'AI')} model."
                st.success(summary)

    def render_analysis_history(self):
        """Render analysis history"""
        if 'analysis_history' not in st.session_state or not st.session_state.analysis_history:
            return

        st.markdown("---")
        st.subheader("📚 Analysis History")

        for i, analysis in enumerate(reversed(st.session_state.analysis_history[-5:])):
            with st.expander(f"📄 {analysis['document_name']} - {analysis['analysis_type'].title()} ({analysis['timestamp'][:19]})"):
                st.markdown(f"**Model Used:** {analysis['model_used']}")
                st.markdown(f"**Analysis Type:** {analysis['analysis_type'].replace('_', ' ').title()}")
                st.markdown("**Result:**")
                st.write(analysis['result'][:500] + "..." if len(analysis['result']) > 500 else analysis['result'])

def main():
    """Main function to render document analyzer"""
    st.set_page_config(
        page_title="DocuMind Document Analyzer",
        page_icon="📄",
        layout="wide"
    )

    analyzer = DocumentAnalyzer()

    # Sidebar for information
    with st.sidebar:
        st.header("📄 Document Analyzer")

        st.markdown("""
        **🎯 Supported Formats:**
        - PDF documents
        - Word documents (DOCX)
        - Text files (TXT, MD)
        - Structured data (JSON, CSV)

        **🔍 Analysis Types:**
        - Comprehensive analysis
        - Executive summaries
        - Technical reviews
        - Compliance checking
        - Sentiment analysis
        - Keyword extraction
        - Structure analysis

        **⚡ AI Models:**
        - Llama 3.1 70B (most comprehensive)
        - Llama 3.1 8B (balanced)
        - phi3.5 (fastest)
        """)

        st.markdown("---")
        st.subheader("📊 Current Session")

        if 'analysis_history' in st.session_state:
            st.metric("Documents Analyzed", len(st.session_state.analysis_history))

        if 'document_text' in st.session_state:
            st.metric("Current Document", f"{len(st.session_state.document_text.split())} words")

    # Main interface
    analyzer.render_document_upload()
    analyzer.render_analysis_history()

if __name__ == "__main__":
    main()
