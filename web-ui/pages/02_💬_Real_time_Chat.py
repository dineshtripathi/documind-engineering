"""
Real-time Chat Interface with WebSocket Support
Enables streaming responses and live AI conversations
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st
from streamlit_chat import message
import requests
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatInterface:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.session_id = None

    def initialize_session(self):
        """Initialize chat session"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'chat_session_id' not in st.session_state:
            st.session_state.chat_session_id = f"session_{int(time.time())}"

        self.session_id = st.session_state.chat_session_id

    def get_ai_response(self, question: str, model_preference: str = "auto") -> Dict:
        """Get AI response with streaming simulation"""
        try:
            payload = {
                "q": question,
                "context_limit": 5,
                "model_preference": model_preference
            }

            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "answer": f"Error: API returned status {response.status_code}",
                    "model_used": "error",
                    "route": "error"
                }

        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            return {
                "answer": f"Error: {str(e)}",
                "model_used": "error",
                "route": "error"
            }

    def simulate_streaming_response(self, text: str, placeholder):
        """Simulate streaming response effect"""
        words = text.split()
        displayed_text = ""

        for i, word in enumerate(words):
            displayed_text += word + " "
            placeholder.markdown(f"🤖 **AI Response:** {displayed_text}▋")
            time.sleep(0.05)  # Simulate typing effect

        # Final display without cursor
        placeholder.markdown(f"🤖 **AI Response:** {displayed_text}")
        return displayed_text

    def render_chat_interface(self):
        """Render the main chat interface"""
        self.initialize_session()

        st.header("💬 Real-time AI Chat")
        st.markdown("---")

        # Model selection
        col1, col2 = st.columns([3, 1])

        with col2:
            model_options = {
                "auto": "🎯 Auto-Select",
                "phi3.5": "⚡ phi3.5 (Fast)",
                "llama3.1:8b": "🧠 Llama 3.1 8B",
                "llama3.1:70b": "🚀 Llama 3.1 70B",
                "codellama": "💻 CodeLlama",
            }

            selected_model = st.selectbox(
                "Select AI Model:",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                index=0
            )

        # Chat history display
        chat_container = st.container()

        with chat_container:
            if st.session_state.chat_history:
                for i, chat in enumerate(st.session_state.chat_history):
                    # User message
                    with st.chat_message("user"):
                        st.write(chat["user"])

                    # AI response
                    with st.chat_message("assistant"):
                        st.write(chat["ai"])

                        # Show model info
                        if "model_used" in chat:
                            st.caption(f"Model: {chat['model_used']} | Route: {chat.get('route', 'unknown')}")

        # Chat input
        st.markdown("---")

        # User input
        user_input = st.chat_input("Type your message here...")

        if user_input:
            # Add user message to history
            with st.chat_message("user"):
                st.write(user_input)

            # Show thinking indicator
            with st.chat_message("assistant"):
                thinking_placeholder = st.empty()
                thinking_placeholder.markdown("🤔 **Thinking...** ⏳")

                # Get AI response
                response = self.get_ai_response(user_input, selected_model)

                # Clear thinking indicator and show response
                thinking_placeholder.empty()

                # Simulate streaming
                response_placeholder = st.empty()
                ai_response = self.simulate_streaming_response(
                    response.get("answer", "No response"),
                    response_placeholder
                )

                # Show model info
                model_used = response.get("model_used", "unknown")
                route = response.get("route", "unknown")
                st.caption(f"Model: {model_used} | Route: {route}")

            # Add to chat history
            chat_entry = {
                "user": user_input,
                "ai": ai_response,
                "model_used": model_used,
                "route": route,
                "timestamp": datetime.now().isoformat()
            }

            st.session_state.chat_history.append(chat_entry)

            # Trigger rerun to update display
            st.rerun()

    def render_chat_stats(self):
        """Render chat statistics"""
        if not st.session_state.get('chat_history'):
            return

        st.markdown("### 📊 Chat Statistics")

        col1, col2, col3 = st.columns(3)

        with col1:
            total_messages = len(st.session_state.chat_history)
            st.metric("Total Messages", total_messages)

        with col2:
            models_used = [chat.get("model_used", "unknown") for chat in st.session_state.chat_history]
            unique_models = len(set(models_used))
            st.metric("Models Used", unique_models)

        with col3:
            if total_messages > 0:
                avg_length = sum(len(chat.get("ai", "")) for chat in st.session_state.chat_history) / total_messages
                st.metric("Avg Response Length", f"{int(avg_length)} chars")

        # Model usage breakdown
        if st.session_state.chat_history:
            st.markdown("#### Model Usage Breakdown")
            model_counts = {}
            for chat in st.session_state.chat_history:
                model = chat.get("model_used", "unknown")
                model_counts[model] = model_counts.get(model, 0) + 1

            for model, count in model_counts.items():
                percentage = (count / total_messages) * 100
                st.write(f"**{model}**: {count} messages ({percentage:.1f}%)")

def main():
    """Main function to render chat interface"""
    st.set_page_config(
        page_title="DocuMind Chat",
        page_icon="💬",
        layout="wide"
    )

    chat = ChatInterface()

    # Main chat interface
    col1, col2 = st.columns([2, 1])

    with col1:
        chat.render_chat_interface()

    with col2:
        chat.render_chat_stats()

        # Clear chat button
        st.markdown("---")
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

        # Export chat button
        if st.session_state.get('chat_history'):
            if st.button("📥 Export Chat", type="secondary"):
                chat_data = json.dumps(st.session_state.chat_history, indent=2)
                st.download_button(
                    label="Download Chat History",
                    data=chat_data,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()
