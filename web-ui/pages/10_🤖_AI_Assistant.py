"""
Advanced AI Assistant & Task Automation
Intelligent task automation and workflow management
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any
import schedule
import threading
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class AITask:
    id: str
    title: str
    description: str
    task_type: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    parameters: Optional[Dict] = None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'parameters': self.parameters
        }

class TaskAutomationEngine:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.task_types = {
            "document_analysis": "Analyze uploaded documents for insights",
            "data_processing": "Process and analyze CSV/Excel data",
            "content_generation": "Generate content using AI",
            "code_review": "Review and analyze code snippets",
            "research_summary": "Research and summarize topics",
            "email_draft": "Draft professional emails",
            "report_generation": "Generate comprehensive reports",
            "knowledge_extraction": "Extract knowledge from text",
            "translation": "Translate text between languages",
            "sentiment_analysis": "Analyze sentiment in text"
        }

        self.automation_templates = {
            "daily_report": {
                "name": "Daily Report Generation",
                "description": "Generate daily summary reports",
                "schedule": "daily",
                "tasks": ["data_processing", "report_generation"]
            },
            "content_pipeline": {
                "name": "Content Creation Pipeline",
                "description": "Automated content creation workflow",
                "schedule": "weekly",
                "tasks": ["research_summary", "content_generation"]
            },
            "document_processor": {
                "name": "Document Processing Workflow",
                "description": "Automated document analysis pipeline",
                "schedule": "on_upload",
                "tasks": ["document_analysis", "knowledge_extraction"]
            }
        }

    def create_ai_task(self, title: str, description: str, task_type: str,
                      priority: TaskPriority, parameters: Dict = None,
                      scheduled_for: datetime = None) -> AITask:
        """Create a new AI task"""
        task_id = f"task_{int(time.time())}_{len(st.session_state.get('ai_tasks', []))}"

        task = AITask(
            id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING if not scheduled_for else TaskStatus.SCHEDULED,
            created_at=datetime.now(),
            scheduled_for=scheduled_for,
            parameters=parameters or {}
        )

        return task

    def execute_task(self, task: AITask) -> AITask:
        """Execute an AI task"""
        task.status = TaskStatus.IN_PROGRESS

        try:
            if task.task_type == "document_analysis":
                result = self.execute_document_analysis(task)
            elif task.task_type == "data_processing":
                result = self.execute_data_processing(task)
            elif task.task_type == "content_generation":
                result = self.execute_content_generation(task)
            elif task.task_type == "code_review":
                result = self.execute_code_review(task)
            elif task.task_type == "research_summary":
                result = self.execute_research_summary(task)
            elif task.task_type == "email_draft":
                result = self.execute_email_draft(task)
            elif task.task_type == "report_generation":
                result = self.execute_report_generation(task)
            else:
                result = self.execute_generic_task(task)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()

        except Exception as e:
            task.result = f"Error: {str(e)}"
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()

        return task

    def execute_document_analysis(self, task: AITask) -> str:
        """Execute document analysis task"""
        doc_text = task.parameters.get("document_text", "")
        analysis_type = task.parameters.get("analysis_type", "comprehensive")

        prompt = f"""
        Analyze this document and provide insights:

        {doc_text[:2000]}...

        Analysis type: {analysis_type}

        Please provide:
        1. Key summary points
        2. Main topics and themes
        3. Important insights
        4. Action items or recommendations
        """

        return self.call_ai_api(prompt)

    def execute_data_processing(self, task: AITask) -> str:
        """Execute data processing task"""
        data_summary = task.parameters.get("data_summary", "")
        analysis_focus = task.parameters.get("analysis_focus", "general")

        prompt = f"""
        Analyze this dataset and provide insights:

        {data_summary}

        Focus area: {analysis_focus}

        Please provide:
        1. Key statistical insights
        2. Notable patterns or trends
        3. Data quality observations
        4. Recommendations for further analysis
        """

        return self.call_ai_api(prompt)

    def execute_content_generation(self, task: AITask) -> str:
        """Execute content generation task"""
        topic = task.parameters.get("topic", "")
        content_type = task.parameters.get("content_type", "article")
        target_audience = task.parameters.get("target_audience", "general")

        prompt = f"""
        Create {content_type} content about: {topic}

        Target audience: {target_audience}

        Requirements:
        1. Engaging and informative
        2. Well-structured with clear sections
        3. Professional tone
        4. Include relevant examples
        5. Conclude with key takeaways
        """

        return self.call_ai_api(prompt)

    def execute_code_review(self, task: AITask) -> str:
        """Execute code review task"""
        code = task.parameters.get("code", "")
        language = task.parameters.get("language", "python")

        prompt = f"""
        Review this {language} code and provide feedback:

        ```{language}
        {code}
        ```

        Please analyze:
        1. Code quality and best practices
        2. Potential bugs or issues
        3. Performance considerations
        4. Security concerns
        5. Suggestions for improvement
        """

        return self.call_ai_api(prompt, model="codellama")

    def execute_research_summary(self, task: AITask) -> str:
        """Execute research summary task"""
        topic = task.parameters.get("topic", "")
        depth = task.parameters.get("depth", "medium")

        prompt = f"""
        Research and summarize the topic: {topic}

        Depth level: {depth}

        Please provide:
        1. Overview of the topic
        2. Current state and recent developments
        3. Key challenges and opportunities
        4. Expert opinions and perspectives
        5. Future outlook and trends
        """

        return self.call_ai_api(prompt)

    def execute_email_draft(self, task: AITask) -> str:
        """Execute email drafting task"""
        purpose = task.parameters.get("purpose", "")
        recipient = task.parameters.get("recipient", "colleague")
        tone = task.parameters.get("tone", "professional")

        prompt = f"""
        Draft a {tone} email for the following purpose:
        {purpose}

        Recipient: {recipient}

        Please include:
        1. Appropriate subject line
        2. Professional greeting
        3. Clear and concise body
        4. Call to action if needed
        5. Professional closing
        """

        return self.call_ai_api(prompt)

    def execute_report_generation(self, task: AITask) -> str:
        """Execute report generation task"""
        data_source = task.parameters.get("data_source", "")
        report_type = task.parameters.get("report_type", "summary")

        prompt = f"""
        Generate a {report_type} report based on:
        {data_source}

        Include:
        1. Executive summary
        2. Key findings
        3. Data analysis and insights
        4. Recommendations
        5. Conclusion

        Format as a professional report.
        """

        return self.call_ai_api(prompt)

    def execute_generic_task(self, task: AITask) -> str:
        """Execute generic AI task"""
        prompt = f"""
        Task: {task.title}
        Description: {task.description}

        Please complete this task with detailed and helpful information.
        """

        return self.call_ai_api(prompt)

    def call_ai_api(self, prompt: str, model: str = "auto") -> str:
        """Call the AI API"""
        try:
            payload = {
                "q": prompt,
                "context_limit": 8,
                "model_preference": model
            }

            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("answer", "No response generated")
            else:
                return f"API Error: {response.status_code}"

        except Exception as e:
            return f"Error: {str(e)}"

    def render_task_dashboard(self):
        """Render the main task dashboard"""
        st.header("🤖 AI Assistant & Task Automation")
        st.markdown("Intelligent task automation and workflow management")

        # Initialize session state
        if 'ai_tasks' not in st.session_state:
            st.session_state.ai_tasks = []

        # Dashboard metrics
        tasks = st.session_state.ai_tasks

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Tasks", len(tasks))

        with col2:
            completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
            st.metric("Completed", completed_tasks)

        with col3:
            pending_tasks = len([t for t in tasks if t.get('status') in ['pending', 'scheduled']])
            st.metric("Pending", pending_tasks)

        with col4:
            failed_tasks = len([t for t in tasks if t.get('status') == 'failed'])
            st.metric("Failed", failed_tasks)

        # Task creation and management tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Task", "📋 Task Queue", "🔄 Automation", "📊 Analytics"])

        with tab1:
            self.render_task_creation()

        with tab2:
            self.render_task_queue()

        with tab3:
            self.render_automation_setup()

        with tab4:
            self.render_task_analytics()

    def render_task_creation(self):
        """Render task creation interface"""
        st.subheader("📝 Create New Task")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Basic task information
            title = st.text_input("Task Title:", placeholder="e.g., Analyze Q4 Sales Report")

            description = st.text_area(
                "Task Description:",
                placeholder="Detailed description of what the task should accomplish...",
                height=100
            )

            task_type = st.selectbox(
                "Task Type:",
                options=list(self.task_types.keys()),
                format_func=lambda x: f"{x.replace('_', ' ').title()} - {self.task_types[x]}"
            )

        with col2:
            priority = st.selectbox(
                "Priority:",
                options=[p.value for p in TaskPriority],
                format_func=lambda x: x.title()
            )

            # Scheduling options
            schedule_task = st.checkbox("Schedule Task")

            scheduled_for = None
            if schedule_task:
                schedule_date = st.date_input("Schedule Date:")
                schedule_time = st.time_input("Schedule Time:")
                scheduled_for = datetime.combine(schedule_date, schedule_time)

        # Task-specific parameters
        st.markdown("#### Task Parameters")
        parameters = {}

        if task_type == "document_analysis":
            col_a, col_b = st.columns(2)
            with col_a:
                if 'document_text' in st.session_state:
                    st.info("Using previously uploaded document")
                    parameters["document_text"] = st.session_state.document_text
                else:
                    doc_text = st.text_area("Document Text:", height=150)
                    parameters["document_text"] = doc_text

            with col_b:
                analysis_type = st.selectbox("Analysis Type:",
                    ["comprehensive", "summary", "technical", "financial"])
                parameters["analysis_type"] = analysis_type

        elif task_type == "content_generation":
            col_a, col_b = st.columns(2)
            with col_a:
                topic = st.text_input("Topic:", placeholder="e.g., Machine Learning in Healthcare")
                parameters["topic"] = topic

            with col_b:
                content_type = st.selectbox("Content Type:",
                    ["article", "blog_post", "summary", "presentation", "documentation"])
                parameters["content_type"] = content_type

                target_audience = st.selectbox("Target Audience:",
                    ["general", "technical", "business", "academic"])
                parameters["target_audience"] = target_audience

        elif task_type == "code_review":
            code_input = st.text_area("Code to Review:", height=200,
                placeholder="Paste your code here...")
            language = st.selectbox("Programming Language:",
                ["python", "javascript", "java", "csharp", "cpp"])

            parameters["code"] = code_input
            parameters["language"] = language

        elif task_type == "email_draft":
            col_a, col_b = st.columns(2)
            with col_a:
                purpose = st.text_area("Email Purpose:",
                    placeholder="e.g., Request meeting with client about project update")
                parameters["purpose"] = purpose

            with col_b:
                recipient = st.text_input("Recipient Type:", value="colleague")
                tone = st.selectbox("Tone:", ["professional", "friendly", "formal", "casual"])
                parameters["recipient"] = recipient
                parameters["tone"] = tone

        # Create task button
        if st.button("🚀 Create Task", type="primary", disabled=not (title and description)):
            task = self.create_ai_task(
                title=title,
                description=description,
                task_type=task_type,
                priority=TaskPriority(priority),
                parameters=parameters,
                scheduled_for=scheduled_for
            )

            st.session_state.ai_tasks.append(task.to_dict())
            st.success(f"✅ Task '{title}' created successfully!")

            # Auto-execute if not scheduled
            if not scheduled_for:
                if st.button("▶️ Execute Now", key=f"execute_{task.id}"):
                    self.execute_task_by_id(task.id)

    def render_task_queue(self):
        """Render task queue management"""
        st.subheader("📋 Task Queue")

        tasks = st.session_state.ai_tasks

        if not tasks:
            st.info("No tasks created yet. Create your first task in the 'Create Task' tab.")
            return

        # Filter and sort options
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox("Filter by Status:",
                ["all"] + [status.value for status in TaskStatus])

        with col2:
            priority_filter = st.selectbox("Filter by Priority:",
                ["all"] + [priority.value for priority in TaskPriority])

        with col3:
            sort_by = st.selectbox("Sort by:",
                ["created_at", "priority", "status", "title"])

        # Filter tasks
        filtered_tasks = tasks
        if status_filter != "all":
            filtered_tasks = [t for t in filtered_tasks if t.get('status') == status_filter]
        if priority_filter != "all":
            filtered_tasks = [t for t in filtered_tasks if t.get('priority') == priority_filter]

        # Display tasks
        for task in filtered_tasks:
            with st.expander(
                f"{'✅' if task.get('status') == 'completed' else '⏳'} {task.get('title', 'Untitled')} "
                f"[{task.get('priority', 'medium').upper()}] - {task.get('status', 'unknown').title()}"
            ):
                col_a, col_b = st.columns([3, 1])

                with col_a:
                    st.write(f"**Description:** {task.get('description', 'No description')}")
                    st.write(f"**Type:** {task.get('task_type', 'unknown').replace('_', ' ').title()}")
                    st.write(f"**Created:** {task.get('created_at', 'unknown')[:19]}")

                    if task.get('completed_at'):
                        st.write(f"**Completed:** {task.get('completed_at')[:19]}")

                    if task.get('result'):
                        st.markdown("**Result:**")
                        st.write(task.get('result'))

                with col_b:
                    if task.get('status') in ['pending', 'scheduled']:
                        if st.button("▶️ Execute", key=f"exec_{task.get('id')}"):
                            self.execute_task_by_id(task.get('id'))
                            st.rerun()

                    if st.button("🗑️ Delete", key=f"del_{task.get('id')}"):
                        st.session_state.ai_tasks = [t for t in st.session_state.ai_tasks
                                                   if t.get('id') != task.get('id')]
                        st.rerun()

    def execute_task_by_id(self, task_id: str):
        """Execute a task by ID"""
        for i, task_dict in enumerate(st.session_state.ai_tasks):
            if task_dict.get('id') == task_id:
                # Convert dict back to AITask object
                task = AITask(
                    id=task_dict['id'],
                    title=task_dict['title'],
                    description=task_dict['description'],
                    task_type=task_dict['task_type'],
                    priority=TaskPriority(task_dict['priority']),
                    status=TaskStatus(task_dict['status']),
                    created_at=datetime.fromisoformat(task_dict['created_at']),
                    scheduled_for=datetime.fromisoformat(task_dict['scheduled_for']) if task_dict.get('scheduled_for') else None,
                    completed_at=datetime.fromisoformat(task_dict['completed_at']) if task_dict.get('completed_at') else None,
                    result=task_dict.get('result'),
                    parameters=task_dict.get('parameters', {})
                )

                # Execute task
                with st.spinner(f"Executing task: {task.title}"):
                    executed_task = self.execute_task(task)

                # Update in session state
                st.session_state.ai_tasks[i] = executed_task.to_dict()

                if executed_task.status == TaskStatus.COMPLETED:
                    st.success(f"✅ Task '{task.title}' completed successfully!")
                else:
                    st.error(f"❌ Task '{task.title}' failed: {executed_task.result}")

                break

    def render_automation_setup(self):
        """Render automation workflow setup"""
        st.subheader("🔄 Task Automation & Workflows")

        # Automation templates
        st.markdown("#### 📋 Automation Templates")

        for template_id, template in self.automation_templates.items():
            with st.expander(f"🔧 {template['name']}"):
                st.write(f"**Description:** {template['description']}")
                st.write(f"**Schedule:** {template['schedule']}")
                st.write(f"**Tasks:** {', '.join(template['tasks'])}")

                if st.button(f"🚀 Set Up {template['name']}", key=f"setup_{template_id}"):
                    st.info(f"Automation template '{template['name']}' would be configured here.")

        # Custom automation
        st.markdown("#### ⚙️ Custom Automation")

        col1, col2 = st.columns(2)

        with col1:
            workflow_name = st.text_input("Workflow Name:")
            trigger_type = st.selectbox("Trigger Type:",
                ["time_based", "file_upload", "data_change", "manual"])

        with col2:
            if trigger_type == "time_based":
                schedule_frequency = st.selectbox("Frequency:",
                    ["daily", "weekly", "monthly", "hourly"])
                schedule_time = st.time_input("Time:")

        # Workflow steps
        st.markdown("#### 📝 Workflow Steps")

        if 'workflow_steps' not in st.session_state:
            st.session_state.workflow_steps = []

        col_a, col_b = st.columns([3, 1])

        with col_a:
            step_task_type = st.selectbox("Add Step:",
                list(self.task_types.keys()),
                format_func=lambda x: x.replace('_', ' ').title())

        with col_b:
            if st.button("➕ Add Step"):
                st.session_state.workflow_steps.append(step_task_type)
                st.rerun()

        # Display workflow steps
        for i, step in enumerate(st.session_state.workflow_steps):
            col_x, col_y = st.columns([4, 1])
            with col_x:
                st.write(f"{i+1}. {step.replace('_', ' ').title()}")
            with col_y:
                if st.button("❌", key=f"remove_step_{i}"):
                    st.session_state.workflow_steps.pop(i)
                    st.rerun()

        if st.button("💾 Save Automation Workflow"):
            if workflow_name and st.session_state.workflow_steps:
                st.success(f"Workflow '{workflow_name}' saved successfully!")
                st.info("Automation workflows would be stored and scheduled here.")

    def render_task_analytics(self):
        """Render task analytics and insights"""
        st.subheader("📊 Task Analytics")

        tasks = st.session_state.ai_tasks

        if not tasks:
            st.info("No tasks to analyze yet.")
            return

        # Create analytics DataFrame
        df = pd.DataFrame(tasks)

        # Task completion stats
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Task Status Distribution")
            if 'status' in df.columns:
                status_counts = df['status'].value_counts()
                fig_status = px.pie(values=status_counts.values, names=status_counts.index,
                                  title="Task Status Distribution")
                st.plotly_chart(fig_status, use_container_width=True)

        with col2:
            st.markdown("#### ⭐ Priority Distribution")
            if 'priority' in df.columns:
                priority_counts = df['priority'].value_counts()
                fig_priority = px.bar(x=priority_counts.index, y=priority_counts.values,
                                    title="Task Priority Distribution")
                st.plotly_chart(fig_priority, use_container_width=True)

        # Task type analysis
        st.markdown("#### 🎯 Task Type Performance")
        if 'task_type' in df.columns:
            type_counts = df['task_type'].value_counts()
            fig_types = px.bar(x=type_counts.index, y=type_counts.values,
                             title="Tasks by Type")
            st.plotly_chart(fig_types, use_container_width=True)

        # Completion timeline
        completed_tasks = df[df['status'] == 'completed']
        if not completed_tasks.empty and 'completed_at' in completed_tasks.columns:
            st.markdown("#### ⏰ Task Completion Timeline")
            completed_tasks['completion_date'] = pd.to_datetime(completed_tasks['completed_at']).dt.date
            daily_completions = completed_tasks.groupby('completion_date').size()

            fig_timeline = px.line(x=daily_completions.index, y=daily_completions.values,
                                 title="Daily Task Completions")
            st.plotly_chart(fig_timeline, use_container_width=True)

        # Task details table
        st.markdown("#### 📋 Task Summary Table")
        display_df = df[['title', 'task_type', 'priority', 'status', 'created_at']].copy()
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(display_df, use_container_width=True)

def main():
    """Main function to render AI assistant"""
    st.set_page_config(
        page_title="DocuMind AI Assistant",
        page_icon="🤖",
        layout="wide"
    )

    assistant = TaskAutomationEngine()

    # Sidebar for information
    with st.sidebar:
        st.header("🤖 AI Assistant")

        st.markdown("""
        **🎯 Task Types:**
        - Document analysis
        - Data processing
        - Content generation
        - Code review
        - Research summaries
        - Email drafting
        - Report generation

        **⚡ Automation Features:**
        - Scheduled execution
        - Workflow automation
        - Priority management
        - Task dependencies

        **📊 Analytics:**
        - Performance tracking
        - Completion statistics
        - Time analysis
        - Success rates
        """)

        st.markdown("---")
        st.subheader("📈 Quick Stats")

        if 'ai_tasks' in st.session_state:
            tasks = st.session_state.ai_tasks
            st.metric("Total Tasks", len(tasks))

            completed = len([t for t in tasks if t.get('status') == 'completed'])
            if len(tasks) > 0:
                completion_rate = (completed / len(tasks)) * 100
                st.metric("Completion Rate", f"{completion_rate:.1f}%")

    # Main interface
    assistant.render_task_dashboard()

if __name__ == "__main__":
    main()
