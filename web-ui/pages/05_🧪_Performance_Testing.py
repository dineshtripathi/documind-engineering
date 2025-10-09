"""
API Performance Testing Suite
Load testing and performance monitoring for DocuMind APIs
"""
import streamlit as st
import requests
import asyncio
import aiohttp
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import statistics
from typing import Dict, List, Optional, Tuple
import json

class PerformanceTester:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.test_scenarios = {
            "quick_query": {
                "endpoint": "/ask",
                "method": "POST",
                "payload": {"q": "What is Python?", "context_limit": 3},
                "description": "Simple question about Python"
            },
            "complex_query": {
                "endpoint": "/ask",
                "method": "POST",
                "payload": {"q": "Explain the architecture of a scalable microservices system with Docker, Kubernetes, and monitoring", "context_limit": 5},
                "description": "Complex technical question"
            },
            "code_query": {
                "endpoint": "/ask",
                "method": "POST",
                "payload": {"q": "Generate a Python FastAPI application with authentication", "context_limit": 4, "model_preference": "codellama"},
                "description": "Code generation request"
            },
            "health_check": {
                "endpoint": "/health",
                "method": "GET",
                "payload": None,
                "description": "Health endpoint check"
            },
            "domain_analysis": {
                "endpoint": "/analyze-domain",
                "method": "POST",
                "payload": {"text": "Machine learning algorithms for natural language processing"},
                "description": "Domain analysis request"
            }
        }

    def single_request_test(self, scenario: Dict, request_id: int) -> Dict:
        """Execute a single API request and measure performance"""
        start_time = time.time()

        try:
            if scenario["method"] == "GET":
                response = requests.get(
                    f"{self.api_base_url}{scenario['endpoint']}",
                    timeout=60
                )
            else:
                response = requests.post(
                    f"{self.api_base_url}{scenario['endpoint']}",
                    json=scenario["payload"],
                    timeout=60
                )

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                "request_id": request_id,
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "response_size": len(response.content) if response.content else 0,
                "timestamp": datetime.now(),
                "error": None
            }

        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "request_id": request_id,
                "success": False,
                "status_code": 0,
                "response_time_ms": response_time,
                "response_size": 0,
                "timestamp": datetime.now(),
                "error": str(e)
            }

    def load_test(self, scenario_key: str, num_requests: int, concurrent_users: int, progress_callback=None) -> List[Dict]:
        """Execute load test with multiple concurrent requests"""
        scenario = self.test_scenarios[scenario_key]
        results = []

        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # Submit all requests
            future_to_id = {
                executor.submit(self.single_request_test, scenario, i): i
                for i in range(num_requests)
            }

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_id):
                result = future.result()
                results.append(result)
                completed += 1

                if progress_callback:
                    progress_callback(completed / num_requests)

        return results

    def analyze_results(self, results: List[Dict]) -> Dict:
        """Analyze performance test results"""
        if not results:
            return {}

        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]

        response_times = [r["response_time_ms"] for r in successful_results]

        analysis = {
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "failed_requests": len(failed_results),
            "success_rate": (len(successful_results) / len(results)) * 100 if results else 0,
            "response_times": {
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "p95": self.percentile(response_times, 95) if response_times else 0,
                "p99": self.percentile(response_times, 99) if response_times else 0
            },
            "throughput": {
                "requests_per_second": len(successful_results) / ((max([r["timestamp"] for r in results]) - min([r["timestamp"] for r in results])).total_seconds()) if len(results) > 1 else 0
            },
            "errors": [r["error"] for r in failed_results if r["error"]]
        }

        return analysis

    def percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def render_test_configuration(self):
        """Render test configuration interface"""
        st.header("🧪 Performance Testing Suite")
        st.markdown("Load test your DocuMind APIs and monitor performance")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🎯 Test Configuration")

            scenario = st.selectbox(
                "Test Scenario:",
                options=list(self.test_scenarios.keys()),
                format_func=lambda x: f"{x.replace('_', ' ').title()} - {self.test_scenarios[x]['description']}"
            )

            col_a, col_b = st.columns(2)
            with col_a:
                num_requests = st.number_input(
                    "Number of Requests:",
                    min_value=1,
                    max_value=1000,
                    value=50,
                    step=10
                )

            with col_b:
                concurrent_users = st.number_input(
                    "Concurrent Users:",
                    min_value=1,
                    max_value=50,
                    value=5,
                    step=1
                )

        with col2:
            st.subheader("📋 Scenario Details")
            selected_scenario = self.test_scenarios[scenario]

            st.write(f"**Endpoint:** `{selected_scenario['endpoint']}`")
            st.write(f"**Method:** `{selected_scenario['method']}`")
            st.write(f"**Description:** {selected_scenario['description']}")

            if selected_scenario["payload"]:
                with st.expander("📦 Request Payload"):
                    st.json(selected_scenario["payload"])

        # Start test button
        if st.button("🚀 Start Performance Test", type="primary"):
            self.run_performance_test(scenario, num_requests, concurrent_users)

    def run_performance_test(self, scenario: str, num_requests: int, concurrent_users: int):
        """Execute performance test with real-time progress"""
        st.markdown("---")
        st.subheader("⚡ Test Execution")

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(progress):
            progress_bar.progress(progress)
            status_text.text(f"Progress: {progress:.1%} - {int(progress * num_requests)}/{num_requests} requests completed")

        # Run the test
        start_time = time.time()
        with st.spinner("Running performance test..."):
            results = self.load_test(scenario, num_requests, concurrent_users, update_progress)

        total_time = time.time() - start_time

        # Store results in session state
        st.session_state.test_results = results
        st.session_state.test_metadata = {
            "scenario": scenario,
            "num_requests": num_requests,
            "concurrent_users": concurrent_users,
            "total_time": total_time,
            "timestamp": datetime.now()
        }

        st.success(f"✅ Test completed in {total_time:.2f} seconds!")

        # Display results
        self.render_test_results()

    def render_test_results(self):
        """Render detailed test results"""
        if 'test_results' not in st.session_state:
            st.info("👆 Run a performance test to see results here!")
            return

        results = st.session_state.test_results
        metadata = st.session_state.test_metadata
        analysis = self.analyze_results(results)

        st.markdown("---")
        st.subheader("📊 Test Results")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Success Rate",
                f"{analysis['success_rate']:.1f}%",
                delta=f"{analysis['successful_requests']}/{analysis['total_requests']}"
            )

        with col2:
            st.metric(
                "Avg Response Time",
                f"{analysis['response_times']['mean']:.0f}ms",
                delta=f"Min: {analysis['response_times']['min']:.0f}ms"
            )

        with col3:
            st.metric(
                "95th Percentile",
                f"{analysis['response_times']['p95']:.0f}ms",
                delta=f"99th: {analysis['response_times']['p99']:.0f}ms"
            )

        with col4:
            st.metric(
                "Throughput",
                f"{analysis['throughput']['requests_per_second']:.1f} req/s",
                delta=f"{metadata['concurrent_users']} concurrent users"
            )

        # Response time distribution
        if analysis['successful_requests'] > 0:
            col1, col2 = st.columns(2)

            with col1:
                # Response time histogram
                df = pd.DataFrame(results)
                successful_df = df[df['success'] == True]

                fig_hist = px.histogram(
                    successful_df,
                    x='response_time_ms',
                    nbins=20,
                    title='Response Time Distribution',
                    labels={'response_time_ms': 'Response Time (ms)', 'count': 'Frequency'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            with col2:
                # Response time over time
                successful_df['request_order'] = range(len(successful_df))

                fig_time = px.line(
                    successful_df,
                    x='request_order',
                    y='response_time_ms',
                    title='Response Time Over Time',
                    labels={'request_order': 'Request Number', 'response_time_ms': 'Response Time (ms)'}
                )
                st.plotly_chart(fig_time, use_container_width=True)

        # Detailed statistics table
        st.subheader("📈 Detailed Statistics")

        stats_data = {
            "Metric": [
                "Total Requests",
                "Successful Requests",
                "Failed Requests",
                "Success Rate (%)",
                "Mean Response Time (ms)",
                "Median Response Time (ms)",
                "Min Response Time (ms)",
                "Max Response Time (ms)",
                "95th Percentile (ms)",
                "99th Percentile (ms)",
                "Requests per Second"
            ],
            "Value": [
                analysis['total_requests'],
                analysis['successful_requests'],
                analysis['failed_requests'],
                f"{analysis['success_rate']:.2f}",
                f"{analysis['response_times']['mean']:.2f}",
                f"{analysis['response_times']['median']:.2f}",
                f"{analysis['response_times']['min']:.2f}",
                f"{analysis['response_times']['max']:.2f}",
                f"{analysis['response_times']['p95']:.2f}",
                f"{analysis['response_times']['p99']:.2f}",
                f"{analysis['throughput']['requests_per_second']:.2f}"
            ]
        }

        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

        # Error analysis
        if analysis['errors']:
            st.subheader("❌ Error Analysis")
            error_counts = {}
            for error in analysis['errors']:
                error_counts[error] = error_counts.get(error, 0) + 1

            for error, count in error_counts.items():
                st.error(f"**{error}** - Occurred {count} times")

        # Export results
        st.subheader("📥 Export Results")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Download Results CSV"):
                df = pd.DataFrame(results)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"performance_test_{metadata['timestamp'].strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        with col2:
            if st.button("📋 Download Analysis JSON"):
                analysis_json = json.dumps({
                    "metadata": {
                        "scenario": metadata['scenario'],
                        "num_requests": metadata['num_requests'],
                        "concurrent_users": metadata['concurrent_users'],
                        "timestamp": metadata['timestamp'].isoformat()
                    },
                    "analysis": analysis
                }, indent=2)

                st.download_button(
                    label="Download JSON",
                    data=analysis_json,
                    file_name=f"performance_analysis_{metadata['timestamp'].strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

    def render_benchmark_comparison(self):
        """Render benchmark comparison interface"""
        st.markdown("---")
        st.subheader("⚖️ Benchmark Comparison")

        # Sample benchmark data (would be stored/loaded in real implementation)
        benchmark_data = {
            "quick_query": {"mean_response_time": 850, "success_rate": 99.2, "throughput": 12.5},
            "complex_query": {"mean_response_time": 2100, "success_rate": 98.8, "throughput": 4.2},
            "code_query": {"mean_response_time": 3200, "success_rate": 97.5, "throughput": 2.8},
            "health_check": {"mean_response_time": 45, "success_rate": 100.0, "throughput": 85.0}
        }

        if 'test_results' in st.session_state:
            metadata = st.session_state.test_metadata
            analysis = self.analyze_results(st.session_state.test_results)
            scenario = metadata['scenario']

            if scenario in benchmark_data:
                benchmark = benchmark_data[scenario]

                col1, col2, col3 = st.columns(3)

                with col1:
                    current_rt = analysis['response_times']['mean']
                    benchmark_rt = benchmark['mean_response_time']
                    rt_delta = ((current_rt - benchmark_rt) / benchmark_rt) * 100

                    st.metric(
                        "Response Time vs Benchmark",
                        f"{current_rt:.0f}ms",
                        delta=f"{rt_delta:+.1f}% vs {benchmark_rt}ms"
                    )

                with col2:
                    current_sr = analysis['success_rate']
                    benchmark_sr = benchmark['success_rate']
                    sr_delta = current_sr - benchmark_sr

                    st.metric(
                        "Success Rate vs Benchmark",
                        f"{current_sr:.1f}%",
                        delta=f"{sr_delta:+.1f}% vs {benchmark_sr}%"
                    )

                with col3:
                    current_tp = analysis['throughput']['requests_per_second']
                    benchmark_tp = benchmark['throughput']
                    tp_delta = ((current_tp - benchmark_tp) / benchmark_tp) * 100

                    st.metric(
                        "Throughput vs Benchmark",
                        f"{current_tp:.1f} req/s",
                        delta=f"{tp_delta:+.1f}% vs {benchmark_tp} req/s"
                    )

def main():
    """Main function to render performance testing interface"""
    st.set_page_config(
        page_title="DocuMind Performance Testing",
        page_icon="🧪",
        layout="wide"
    )

    tester = PerformanceTester()

    # Sidebar for testing guidelines
    with st.sidebar:
        st.header("⚙️ Testing Guidelines")

        st.markdown("""
        **📋 Best Practices:**
        - Start with small tests (10-20 requests)
        - Monitor system resources during tests
        - Test different scenarios separately
        - Use realistic concurrent user counts

        **⚠️ Limitations:**
        - Max 1000 requests per test
        - Max 50 concurrent users
        - 60-second timeout per request

        **🎯 Scenarios:**
        - **Quick Query**: Fast responses
        - **Complex Query**: Heavy processing
        - **Code Query**: AI code generation
        - **Health Check**: System availability
        """)

        st.markdown("---")
        st.subheader("📊 Current System")

        # Quick system check
        try:
            response = requests.get("http://localhost:7001/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API is healthy")
            else:
                st.warning("⚠️ API issues detected")
        except:
            st.error("❌ API not accessible")

    # Main interface
    tester.render_test_configuration()
    tester.render_test_results()
    tester.render_benchmark_comparison()

if __name__ == "__main__":
    main()
