"""
Advanced Analytics Dashboard for DocuMind
Real-time system monitoring and usage analytics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import time
from datetime import datetime, timedelta
import psutil
import docker
from typing import Dict, List, Optional

class AnalyticsDashboard:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.docker_client = None
        try:
            self.docker_client = docker.from_env()
        except:
            pass

    def get_system_metrics(self) -> Dict:
        """Get real-time system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # GPU info (if available)
            gpu_info = "Not available"
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_info = f"{gpu.name} - {gpu.memoryUtil*100:.1f}% memory used"
            except:
                pass

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_total_gb": memory.total / (1024**3),
                "memory_used_gb": memory.used / (1024**3),
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_total_gb": disk.total / (1024**3),
                "disk_used_gb": disk.used / (1024**3),
                "gpu_info": gpu_info,
                "timestamp": datetime.now()
            }
        except Exception as e:
            st.error(f"Error getting system metrics: {str(e)}")
            return {}

    def get_docker_stats(self) -> List[Dict]:
        """Get Docker container statistics"""
        if not self.docker_client:
            return []

        try:
            containers = []
            for container in self.docker_client.containers.list():
                stats = container.stats(stream=False)

                # Calculate CPU percentage
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                cpu_percent = 0
                if system_delta > 0:
                    cpu_percent = (cpu_delta / system_delta) * 100

                # Calculate memory usage
                memory_usage = stats['memory_stats'].get('usage', 0)
                memory_limit = stats['memory_stats'].get('limit', 1)
                memory_percent = (memory_usage / memory_limit) * 100

                containers.append({
                    "name": container.name,
                    "status": container.status,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "memory_usage_mb": memory_usage / (1024**2),
                    "memory_limit_mb": memory_limit / (1024**2)
                })

            return containers
        except Exception as e:
            st.error(f"Error getting Docker stats: {str(e)}")
            return []

    def get_api_health(self) -> Dict:
        """Get API health status"""
        services = {
            "RAG API": f"{self.api_base_url}/health",
            "Qdrant": "http://localhost:6333/health",
            "Ollama": "http://localhost:11434/api/tags"
        }

        health_status = {}
        for service, url in services.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5)
                response_time = (time.time() - start_time) * 1000

                health_status[service] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time_ms": response_time,
                    "status_code": response.status_code
                }
            except Exception as e:
                health_status[service] = {
                    "status": "error",
                    "response_time_ms": 0,
                    "error": str(e)
                }

        return health_status

    def render_system_overview(self):
        """Render system overview section"""
        st.header("🖥️ System Overview")

        # Get metrics
        metrics = self.get_system_metrics()
        health = self.get_api_health()

        if not metrics:
            st.error("Unable to fetch system metrics")
            return

        # System metrics cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "CPU Usage",
                f"{metrics['cpu_percent']:.1f}%",
                delta=None
            )

        with col2:
            st.metric(
                "Memory Usage",
                f"{metrics['memory_percent']:.1f}%",
                delta=f"{metrics['memory_used_gb']:.1f}GB / {metrics['memory_total_gb']:.1f}GB"
            )

        with col3:
            st.metric(
                "Disk Usage",
                f"{metrics['disk_percent']:.1f}%",
                delta=f"{metrics['disk_used_gb']:.1f}GB / {metrics['disk_total_gb']:.1f}GB"
            )

        with col4:
            healthy_services = sum(1 for s in health.values() if s.get('status') == 'healthy')
            total_services = len(health)
            st.metric(
                "Services Health",
                f"{healthy_services}/{total_services}",
                delta="All Healthy" if healthy_services == total_services else "Issues Detected"
            )

        # GPU info if available
        if metrics['gpu_info'] != "Not available":
            st.info(f"🎮 GPU: {metrics['gpu_info']}")

    def render_service_health(self):
        """Render service health monitoring"""
        st.header("🏥 Service Health")

        health = self.get_api_health()

        for service, status in health.items():
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                if status['status'] == 'healthy':
                    st.success(f"✅ {service}")
                elif status['status'] == 'unhealthy':
                    st.warning(f"⚠️ {service}")
                else:
                    st.error(f"❌ {service}")

            with col2:
                if 'response_time_ms' in status:
                    st.metric("Response Time", f"{status['response_time_ms']:.0f}ms")

            with col3:
                if 'status_code' in status:
                    st.metric("Status Code", status['status_code'])
                elif 'error' in status:
                    st.error(f"Error: {status['error']}")

    def render_docker_monitoring(self):
        """Render Docker container monitoring"""
        st.header("🐳 Docker Containers")

        containers = self.get_docker_stats()

        if not containers:
            st.warning("No Docker containers found or Docker not accessible")
            return

        # Create DataFrame for table display
        df = pd.DataFrame(containers)

        if not df.empty:
            # Display container table
            st.dataframe(
                df[['name', 'status', 'cpu_percent', 'memory_percent', 'memory_usage_mb']].round(2),
                use_container_width=True
            )

            # Container resource usage charts
            col1, col2 = st.columns(2)

            with col1:
                fig_cpu = px.bar(
                    df,
                    x='name',
                    y='cpu_percent',
                    title='Container CPU Usage (%)',
                    color='cpu_percent',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_cpu, use_container_width=True)

            with col2:
                fig_memory = px.bar(
                    df,
                    x='name',
                    y='memory_percent',
                    title='Container Memory Usage (%)',
                    color='memory_percent',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_memory, use_container_width=True)

    def render_real_time_charts(self):
        """Render real-time monitoring charts"""
        st.header("📊 Real-time Monitoring")

        # Initialize session state for historical data
        if 'metrics_history' not in st.session_state:
            st.session_state.metrics_history = []

        # Auto-refresh functionality
        placeholder = st.empty()

        # Get current metrics
        current_metrics = self.get_system_metrics()
        if current_metrics:
            st.session_state.metrics_history.append(current_metrics)

            # Keep only last 50 readings
            if len(st.session_state.metrics_history) > 50:
                st.session_state.metrics_history = st.session_state.metrics_history[-50:]

        if st.session_state.metrics_history:
            df_history = pd.DataFrame(st.session_state.metrics_history)

            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('CPU Usage (%)', 'Memory Usage (%)', 'Disk Usage (%)', 'System Load'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )

            # CPU usage
            fig.add_trace(
                go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['cpu_percent'],
                    mode='lines+markers',
                    name='CPU',
                    line=dict(color='red')
                ),
                row=1, col=1
            )

            # Memory usage
            fig.add_trace(
                go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['memory_percent'],
                    mode='lines+markers',
                    name='Memory',
                    line=dict(color='blue')
                ),
                row=1, col=2
            )

            # Disk usage
            fig.add_trace(
                go.Scatter(
                    x=df_history['timestamp'],
                    y=df_history['disk_percent'],
                    mode='lines+markers',
                    name='Disk',
                    line=dict(color='green')
                ),
                row=2, col=1
            )

            # Combined system load
            fig.add_trace(
                go.Scatter(
                    x=df_history['timestamp'],
                    y=(df_history['cpu_percent'] + df_history['memory_percent']) / 2,
                    mode='lines+markers',
                    name='Avg Load',
                    line=dict(color='purple')
                ),
                row=2, col=2
            )

            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        # Auto-refresh controls
        col1, col2 = st.columns([1, 3])
        with col1:
            auto_refresh = st.checkbox("Auto Refresh", value=False)

        if auto_refresh:
            time.sleep(2)
            st.rerun()

    def render_usage_analytics(self):
        """Render usage analytics"""
        st.header("📈 Usage Analytics")

        # Simulated usage data (in a real system, this would come from logs)
        st.info("📊 Usage analytics will be populated as users interact with the system")

        # Placeholder for future analytics
        sample_data = {
            "queries_today": 42,
            "unique_users": 12,
            "avg_response_time": "1.2s",
            "most_used_model": "phi3.5",
            "top_query_types": ["Python", ".NET", "Web Development"]
        }

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Queries Today", sample_data["queries_today"])
            st.metric("Unique Users", sample_data["unique_users"])

        with col2:
            st.metric("Avg Response Time", sample_data["avg_response_time"])
            st.metric("Most Used Model", sample_data["most_used_model"])

        with col3:
            st.write("**Top Query Types:**")
            for i, query_type in enumerate(sample_data["top_query_types"], 1):
                st.write(f"{i}. {query_type}")

def main():
    """Main function to render analytics dashboard"""
    st.set_page_config(
        page_title="DocuMind Analytics",
        page_icon="📊",
        layout="wide"
    )

    dashboard = AnalyticsDashboard()

    # Sidebar for dashboard controls
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")

        refresh_interval = st.selectbox(
            "Refresh Interval",
            [5, 10, 30, 60],
            index=1,
            format_func=lambda x: f"{x} seconds"
        )

        show_advanced = st.checkbox("Show Advanced Metrics", value=True)

        if st.button("🔄 Refresh Now"):
            st.rerun()

    # Main dashboard sections
    dashboard.render_system_overview()
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        dashboard.render_service_health()

    with col2:
        dashboard.render_docker_monitoring()

    st.markdown("---")
    dashboard.render_real_time_charts()

    st.markdown("---")
    dashboard.render_usage_analytics()

if __name__ == "__main__":
    main()
