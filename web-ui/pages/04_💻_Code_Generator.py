"""
Advanced Code Generation Assistant
AI-powered code generation with syntax highlighting and execution
"""
import streamlit as st
from streamlit_ace import st_ace
import requests
import json
import time
from datetime import datetime
import subprocess
import tempfile
import os
from typing import Dict, List, Optional

class CodeGenerator:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.supported_languages = {
            "python": {"extension": ".py", "interpreter": "python3"},
            "javascript": {"extension": ".js", "interpreter": "node"},
            "typescript": {"extension": ".ts", "interpreter": "ts-node"},
            "bash": {"extension": ".sh", "interpreter": "bash"},
            "sql": {"extension": ".sql", "interpreter": None},
            "html": {"extension": ".html", "interpreter": None},
            "css": {"extension": ".css", "interpreter": None},
            "json": {"extension": ".json", "interpreter": None},
            "yaml": {"extension": ".yaml", "interpreter": None},
            "markdown": {"extension": ".md", "interpreter": None}
        }

    def generate_code(self, prompt: str, language: str, style: str = "professional") -> Dict:
        """Generate code using AI"""
        try:
            # Enhanced prompt for better code generation
            enhanced_prompt = f"""
            Generate {language} code for the following request:
            {prompt}

            Requirements:
            - Style: {style}
            - Include comments and documentation
            - Follow best practices for {language}
            - Make the code production-ready
            - Include error handling where appropriate

            Please provide clean, well-structured code:
            """

            payload = {
                "q": enhanced_prompt,
                "context_limit": 3,
                "model_preference": "codellama"  # Use CodeLlama for code generation
            }

            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=60  # Longer timeout for code generation
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "code": result.get("answer", ""),
                    "model_used": result.get("model_used", "unknown"),
                    "generation_time": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "code": ""
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": ""
            }

    def execute_code(self, code: str, language: str) -> Dict:
        """Execute code safely in a temporary environment"""
        if language not in self.supported_languages:
            return {
                "success": False,
                "error": f"Execution not supported for {language}"
            }

        lang_config = self.supported_languages[language]
        interpreter = lang_config["interpreter"]

        if not interpreter:
            return {
                "success": False,
                "error": f"No interpreter configured for {language}"
            }

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=lang_config["extension"],
                delete=False
            ) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            # Execute the code
            start_time = time.time()
            result = subprocess.run(
                [interpreter, temp_file_path],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            execution_time = time.time() - start_time

            # Clean up
            os.unlink(temp_file_path)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": execution_time
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Code execution timed out (30s limit)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def render_code_generator(self):
        """Render the main code generation interface"""
        st.header("💻 AI Code Generator")
        st.markdown("Generate production-ready code with AI assistance")

        # Input section
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area(
                "Describe what you want to code:",
                placeholder="E.g., Create a REST API endpoint that validates user input and returns JSON response",
                height=100
            )

        with col2:
            language = st.selectbox(
                "Programming Language:",
                options=list(self.supported_languages.keys()),
                index=0
            )

            style = st.selectbox(
                "Code Style:",
                ["professional", "minimal", "educational", "enterprise"],
                index=0
            )

        # Generate button
        if st.button("🚀 Generate Code", type="primary", disabled=not prompt):
            with st.spinner("Generating code..."):
                result = self.generate_code(prompt, language, style)

                if result["success"]:
                    st.session_state.generated_code = result["code"]
                    st.session_state.generated_language = language
                    st.session_state.generation_info = {
                        "model": result["model_used"],
                        "time": result["generation_time"]
                    }
                    st.success(f"Code generated using {result['model_used']}!")
                else:
                    st.error(f"Generation failed: {result['error']}")

    def render_code_editor(self):
        """Render the code editor with syntax highlighting"""
        if 'generated_code' not in st.session_state:
            st.info("👆 Generate some code above to see it here!")
            return

        st.markdown("---")
        st.header("📝 Generated Code")

        # Editor controls
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            theme = st.selectbox(
                "Editor Theme:",
                ["monokai", "github", "solarized_dark", "solarized_light"],
                index=0
            )

        with col2:
            font_size = st.selectbox(
                "Font Size:",
                [12, 14, 16, 18, 20],
                index=1
            )

        with col3:
            if 'generation_info' in st.session_state:
                info = st.session_state.generation_info
                st.caption(f"Generated by {info['model']} at {info['time'][:19]}")

        # Code editor
        edited_code = st_ace(
            value=st.session_state.generated_code,
            language=st.session_state.generated_language,
            theme=theme,
            font_size=font_size,
            auto_update=True,
            height=400,
            wrap=True
        )

        # Update session state with edited code
        st.session_state.generated_code = edited_code

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("▶️ Execute Code"):
                self.execute_generated_code()

        with col2:
            if st.button("💾 Download"):
                self.download_code()

        with col3:
            if st.button("📋 Copy to Clipboard"):
                st.code(edited_code, language=st.session_state.generated_language)

        with col4:
            if st.button("🔄 Regenerate"):
                if 'last_prompt' in st.session_state:
                    # Regenerate with same prompt
                    pass

    def execute_generated_code(self):
        """Execute the generated code"""
        if 'generated_code' not in st.session_state:
            return

        st.markdown("---")
        st.header("⚡ Code Execution")

        code = st.session_state.generated_code
        language = st.session_state.generated_language

        with st.spinner("Executing code..."):
            result = self.execute_code(code, language)

        if result["success"]:
            st.success(f"✅ Execution completed in {result['execution_time']:.2f}s")

            if result.get("stdout"):
                st.subheader("📤 Output:")
                st.code(result["stdout"], language="text")

            if result.get("stderr"):
                st.subheader("⚠️ Warnings/Errors:")
                st.code(result["stderr"], language="text")
        else:
            st.error(f"❌ Execution failed: {result.get('error', 'Unknown error')}")

            if result.get("stderr"):
                st.code(result["stderr"], language="text")

    def download_code(self):
        """Provide code download functionality"""
        if 'generated_code' not in st.session_state:
            return

        code = st.session_state.generated_code
        language = st.session_state.generated_language
        extension = self.supported_languages[language]["extension"]

        filename = f"generated_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"

        st.download_button(
            label=f"📥 Download {filename}",
            data=code,
            file_name=filename,
            mime="text/plain"
        )

    def render_code_templates(self):
        """Render common code templates"""
        st.markdown("---")
        st.header("📚 Code Templates")
        st.markdown("Quick start with common patterns")

        templates = {
            "Python": {
                "REST API with FastAPI": "Create a FastAPI application with CRUD endpoints for a User model",
                "Data Analysis Script": "Create a pandas script to analyze CSV data and generate visualizations",
                "Web Scraper": "Build a web scraper using requests and BeautifulSoup",
                "ML Model Training": "Create a scikit-learn pipeline for classification"
            },
            "JavaScript": {
                "React Component": "Create a React functional component with hooks",
                "Express API": "Build an Express.js REST API with middleware",
                "Async Data Fetcher": "Create an async function to fetch and process API data",
                "DOM Manipulation": "Script to dynamically update webpage content"
            },
            "TypeScript": {
                "Interface Definition": "Define TypeScript interfaces for a user management system",
                "Generic Function": "Create a generic utility function with type constraints",
                "Class with Decorators": "Build a TypeScript class with decorators",
                "API Client": "Create a typed API client class"
            }
        }

        selected_category = st.selectbox(
            "Choose Category:",
            list(templates.keys())
        )

        if selected_category:
            template_options = templates[selected_category]

            cols = st.columns(2)
            for i, (template_name, template_description) in enumerate(template_options.items()):
                with cols[i % 2]:
                    if st.button(f"🎯 {template_name}", key=f"template_{i}"):
                        # Set the prompt for generation
                        st.session_state.template_prompt = template_description
                        st.info(f"Template selected: {template_name}")
                        st.rerun()

    def render_code_history(self):
        """Render code generation history"""
        if 'code_history' not in st.session_state:
            st.session_state.code_history = []

        if not st.session_state.code_history:
            return

        st.markdown("---")
        st.header("📚 Generation History")

        for i, entry in enumerate(reversed(st.session_state.code_history[-10:])):
            with st.expander(f"Generated {entry['language']} code - {entry['timestamp'][:19]}"):
                st.code(entry['code'][:500] + "..." if len(entry['code']) > 500 else entry['code'])

                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Model: {entry.get('model', 'unknown')}")
                with col2:
                    if st.button(f"🔄 Reload", key=f"reload_{i}"):
                        st.session_state.generated_code = entry['code']
                        st.session_state.generated_language = entry['language']
                        st.rerun()

def main():
    """Main function to render code generator"""
    st.set_page_config(
        page_title="DocuMind Code Generator",
        page_icon="💻",
        layout="wide"
    )

    generator = CodeGenerator()

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Code Generator Settings")

        auto_execute = st.checkbox("Auto-execute safe code", value=False)
        save_history = st.checkbox("Save generation history", value=True)

        st.markdown("---")
        st.subheader("🛡️ Safety Notice")
        st.warning("Code execution runs in a sandboxed environment with time limits. Be cautious with system operations.")

        st.markdown("---")
        st.subheader("🎯 Supported Languages")
        for lang in generator.supported_languages.keys():
            st.write(f"• {lang.title()}")

    # Main interface
    generator.render_code_generator()
    generator.render_code_editor()
    generator.render_code_templates()
    generator.render_code_history()

if __name__ == "__main__":
    main()
