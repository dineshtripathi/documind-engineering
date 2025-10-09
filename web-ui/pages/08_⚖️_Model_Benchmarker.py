"""
Advanced AI Model Comparison & Benchmarking Suite
Compare and benchmark different AI models across various tasks
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

class ModelBenchmarker:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.available_models = {
            "phi3.5": "⚡ phi3.5 - Fast general purpose",
            "llama3.1:8b": "🧠 Llama 3.1 8B - Balanced performance",
            "llama3.1:70b": "🚀 Llama 3.1 70B - Most powerful",
            "codellama": "💻 CodeLlama - Programming specialist",
            "auto": "🎯 Auto-select - Intelligent routing"
        }

        self.benchmark_categories = {
            "general_knowledge": {
                "name": "General Knowledge",
                "description": "Basic factual questions and general reasoning",
                "questions": [
                    "What is the capital of France?",
                    "Explain the concept of machine learning in simple terms.",
                    "What are the main differences between Python and Java?",
                    "How does photosynthesis work?",
                    "What is the significance of the year 1969 in space exploration?"
                ]
            },
            "technical_expertise": {
                "name": "Technical Expertise",
                "description": "Advanced technical questions requiring specialized knowledge",
                "questions": [
                    "Explain the difference between REST and GraphQL APIs.",
                    "How does Docker containerization improve application deployment?",
                    "What are the SOLID principles in software engineering?",
                    "Describe the CAP theorem in distributed systems.",
                    "How does gradient descent work in neural networks?"
                ]
            },
            "code_generation": {
                "name": "Code Generation",
                "description": "Programming and code-related tasks",
                "questions": [
                    "Write a Python function to find the factorial of a number.",
                    "Create a JavaScript function to validate email addresses.",
                    "Write a SQL query to find the top 5 customers by total purchases.",
                    "Implement a binary search algorithm in Python.",
                    "Create a React component for a simple todo list."
                ]
            },
            "problem_solving": {
                "name": "Problem Solving",
                "description": "Complex reasoning and analytical thinking",
                "questions": [
                    "How would you design a scalable chat application for millions of users?",
                    "What's the best approach to implement real-time collaboration in a document editor?",
                    "How would you optimize a slow database query that processes millions of records?",
                    "Design a recommendation system for an e-commerce platform.",
                    "How would you handle data consistency in a microservices architecture?"
                ]
            },
            "creativity": {
                "name": "Creativity & Communication",
                "description": "Creative writing and communication skills",
                "questions": [
                    "Write a brief story about a developer who discovers AI consciousness.",
                    "Explain quantum computing to a 10-year-old.",
                    "Create a marketing pitch for a new AI-powered productivity tool.",
                    "Write documentation for a REST API endpoint.",
                    "Compose an email explaining a technical issue to non-technical stakeholders."
                ]
            }
        }

    def run_single_benchmark(self, model: str, question: str, question_id: str) -> Dict:
        """Run a single benchmark test"""
        start_time = time.time()

        try:
            payload = {
                "q": question,
                "context_limit": 5,
                "model_preference": model if model != "auto" else "auto"
            }

            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=60
            )

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "")

                return {
                    "question_id": question_id,
                    "model": model,
                    "question": question,
                    "answer": answer,
                    "response_time_ms": response_time,
                    "word_count": len(answer.split()),
                    "char_count": len(answer),
                    "model_used": result.get("model_used", model),
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "quality_score": self.assess_answer_quality(question, answer)
                }
            else:
                return {
                    "question_id": question_id,
                    "model": model,
                    "question": question,
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time_ms": response_time
                }

        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "question_id": question_id,
                "model": model,
                "question": question,
                "success": False,
                "error": str(e),
                "response_time_ms": response_time
            }

    def assess_answer_quality(self, question: str, answer: str) -> float:
        """Simple heuristic to assess answer quality"""
        if not answer:
            return 0.0

        quality_score = 0.0

        # Length appropriateness (not too short, not too long)
        word_count = len(answer.split())
        if 20 <= word_count <= 200:
            quality_score += 0.3
        elif 10 <= word_count <= 300:
            quality_score += 0.2
        elif word_count > 5:
            quality_score += 0.1

        # Structure indicators
        if any(indicator in answer.lower() for indicator in ['first', 'second', 'finally', '1.', '2.', '-']):
            quality_score += 0.2

        # Technical depth for technical questions
        if any(tech_word in question.lower() for tech_word in ['api', 'database', 'algorithm', 'code', 'python']):
            if any(tech_term in answer.lower() for tech_term in ['function', 'method', 'class', 'variable', 'return']):
                quality_score += 0.2

        # Completeness indicators
        if len(answer) > 100 and answer.endswith('.'):
            quality_score += 0.1

        # Code presence for coding questions
        if 'write' in question.lower() and 'code' in question.lower():
            if any(code_indicator in answer for code_indicator in ['def ', 'function', '()', '{', '}']):
                quality_score += 0.2

        return min(quality_score, 1.0)

    def run_comprehensive_benchmark(self, models: List[str], categories: List[str], progress_callback=None) -> List[Dict]:
        """Run comprehensive benchmark across models and categories"""
        all_results = []
        total_tests = 0

        # Count total tests
        for category in categories:
            total_tests += len(models) * len(self.benchmark_categories[category]["questions"])

        completed_tests = 0

        # Run tests for each category
        for category in categories:
            questions = self.benchmark_categories[category]["questions"]

            for i, question in enumerate(questions):
                question_id = f"{category}_{i}"

                # Test all models on this question
                for model in models:
                    result = self.run_single_benchmark(model, question, question_id)
                    result["category"] = category
                    all_results.append(result)

                    completed_tests += 1
                    if progress_callback:
                        progress_callback(completed_tests / total_tests)

        return all_results

    def analyze_benchmark_results(self, results: List[Dict]) -> Dict:
        """Analyze benchmark results and generate insights"""
        successful_results = [r for r in results if r.get("success", False)]

        if not successful_results:
            return {"error": "No successful results to analyze"}

        # Group by model
        by_model = {}
        for result in successful_results:
            model = result["model_used"]
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(result)

        # Calculate metrics for each model
        model_metrics = {}
        for model, model_results in by_model.items():
            response_times = [r["response_time_ms"] for r in model_results]
            quality_scores = [r.get("quality_score", 0) for r in model_results]
            word_counts = [r.get("word_count", 0) for r in model_results]

            model_metrics[model] = {
                "avg_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "avg_quality_score": statistics.mean(quality_scores),
                "avg_word_count": statistics.mean(word_counts),
                "total_tests": len(model_results),
                "success_rate": 100.0  # Only successful results are included
            }

        # Category analysis
        by_category = {}
        for result in successful_results:
            category = result["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)

        category_metrics = {}
        for category, cat_results in by_category.items():
            response_times = [r["response_time_ms"] for r in cat_results]
            quality_scores = [r.get("quality_score", 0) for r in cat_results]

            category_metrics[category] = {
                "avg_response_time": statistics.mean(response_times),
                "avg_quality_score": statistics.mean(quality_scores),
                "total_tests": len(cat_results)
            }

        return {
            "model_metrics": model_metrics,
            "category_metrics": category_metrics,
            "total_successful_tests": len(successful_results),
            "total_tests": len(results)
        }

    def render_benchmark_interface(self):
        """Render the main benchmarking interface"""
        st.header("⚖️ AI Model Comparison & Benchmarking")
        st.markdown("Compare performance across different AI models and task categories")

        # Configuration section
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🔧 Benchmark Configuration")

            # Model selection
            selected_models = st.multiselect(
                "Select models to benchmark:",
                options=list(self.available_models.keys()),
                default=["phi3.5", "llama3.1:8b"],
                format_func=lambda x: self.available_models[x]
            )

            # Category selection
            selected_categories = st.multiselect(
                "Select benchmark categories:",
                options=list(self.benchmark_categories.keys()),
                default=["general_knowledge", "technical_expertise"],
                format_func=lambda x: self.benchmark_categories[x]["name"]
            )

        with col2:
            st.subheader("📊 Benchmark Details")

            if selected_models and selected_categories:
                total_questions = sum(len(self.benchmark_categories[cat]["questions"]) for cat in selected_categories)
                total_tests = len(selected_models) * total_questions

                st.metric("Total Tests", total_tests)
                st.metric("Models", len(selected_models))
                st.metric("Categories", len(selected_categories))

                estimated_time = total_tests * 3  # Estimate 3 seconds per test
                st.metric("Estimated Time", f"{estimated_time//60}m {estimated_time%60}s")

        # Category details
        if selected_categories:
            st.subheader("📋 Selected Categories")
            for category in selected_categories:
                cat_info = self.benchmark_categories[category]
                with st.expander(f"📚 {cat_info['name']} ({len(cat_info['questions'])} questions)"):
                    st.write(cat_info["description"])
                    for i, question in enumerate(cat_info["questions"][:3]):
                        st.write(f"{i+1}. {question}")
                    if len(cat_info["questions"]) > 3:
                        st.write(f"... and {len(cat_info['questions']) - 3} more questions")

        # Run benchmark button
        if st.button("🚀 Start Benchmark", type="primary", disabled=not (selected_models and selected_categories)):
            self.run_benchmark_suite(selected_models, selected_categories)

    def run_benchmark_suite(self, models: List[str], categories: List[str]):
        """Run the complete benchmark suite"""
        st.markdown("---")
        st.subheader("⚡ Running Benchmark Suite")

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(progress):
            progress_bar.progress(progress)
            status_text.text(f"Progress: {progress:.1%} - Running benchmark tests...")

        # Run benchmarks
        start_time = time.time()
        with st.spinner("Executing benchmark tests..."):
            results = self.run_comprehensive_benchmark(models, categories, update_progress)

        total_time = time.time() - start_time

        # Store results
        st.session_state.benchmark_results = results
        st.session_state.benchmark_metadata = {
            "models": models,
            "categories": categories,
            "total_time": total_time,
            "timestamp": datetime.now()
        }

        st.success(f"✅ Benchmark completed in {total_time:.1f} seconds!")

        # Display results
        self.render_benchmark_results()

    def render_benchmark_results(self):
        """Render comprehensive benchmark results"""
        if 'benchmark_results' not in st.session_state:
            st.info("👆 Run a benchmark to see results here!")
            return

        results = st.session_state.benchmark_results
        metadata = st.session_state.benchmark_metadata
        analysis = self.analyze_benchmark_results(results)

        if "error" in analysis:
            st.error(f"Analysis failed: {analysis['error']}")
            return

        st.markdown("---")
        st.subheader("📊 Benchmark Results")

        # Overall summary
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Tests", analysis["total_tests"])

        with col2:
            success_rate = (analysis["total_successful_tests"] / analysis["total_tests"]) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")

        with col3:
            st.metric("Models Tested", len(metadata["models"]))

        with col4:
            st.metric("Categories", len(metadata["categories"]))

        # Model comparison charts
        self.render_model_comparison_charts(analysis)

        # Category performance analysis
        self.render_category_analysis(analysis)

        # Detailed results table
        self.render_detailed_results(results)

        # Export options
        self.render_benchmark_export()

    def render_model_comparison_charts(self, analysis: Dict):
        """Render model comparison visualizations"""
        st.subheader("🏆 Model Performance Comparison")

        model_metrics = analysis["model_metrics"]

        if not model_metrics:
            st.warning("No model metrics available")
            return

        # Create comparison DataFrame
        comparison_data = []
        for model, metrics in model_metrics.items():
            comparison_data.append({
                "Model": model,
                "Avg Response Time (ms)": metrics["avg_response_time"],
                "Quality Score": metrics["avg_quality_score"],
                "Avg Word Count": metrics["avg_word_count"],
                "Total Tests": metrics["total_tests"]
            })

        df = pd.DataFrame(comparison_data)

        # Performance charts
        col1, col2 = st.columns(2)

        with col1:
            # Response time comparison
            fig_time = px.bar(
                df,
                x="Model",
                y="Avg Response Time (ms)",
                title="Average Response Time by Model",
                color="Avg Response Time (ms)",
                color_continuous_scale="Reds_r"
            )
            st.plotly_chart(fig_time, use_container_width=True)

        with col2:
            # Quality score comparison
            fig_quality = px.bar(
                df,
                x="Model",
                y="Quality Score",
                title="Average Quality Score by Model",
                color="Quality Score",
                color_continuous_scale="Greens"
            )
            st.plotly_chart(fig_quality, use_container_width=True)

        # Combined performance radar chart
        if len(df) > 1:
            fig_radar = go.Figure()

            for _, row in df.iterrows():
                # Normalize metrics for radar chart
                normalized_time = 1 - (row["Avg Response Time (ms)"] / df["Avg Response Time (ms)"].max())
                normalized_quality = row["Quality Score"]
                normalized_words = row["Avg Word Count"] / df["Avg Word Count"].max()

                fig_radar.add_trace(go.Scatterpolar(
                    r=[normalized_time, normalized_quality, normalized_words],
                    theta=["Speed", "Quality", "Verbosity"],
                    fill='toself',
                    name=row["Model"]
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1])
                ),
                title="Model Performance Radar Chart",
                showlegend=True
            )

            st.plotly_chart(fig_radar, use_container_width=True)

    def render_category_analysis(self, analysis: Dict):
        """Render category performance analysis"""
        st.subheader("📚 Performance by Category")

        category_metrics = analysis["category_metrics"]

        if not category_metrics:
            st.warning("No category metrics available")
            return

        # Create category DataFrame
        category_data = []
        for category, metrics in category_metrics.items():
            category_name = self.benchmark_categories[category]["name"]
            category_data.append({
                "Category": category_name,
                "Avg Response Time (ms)": metrics["avg_response_time"],
                "Quality Score": metrics["avg_quality_score"],
                "Total Tests": metrics["total_tests"]
            })

        df = pd.DataFrame(category_data)

        col1, col2 = st.columns(2)

        with col1:
            # Category response times
            fig_cat_time = px.bar(
                df,
                x="Category",
                y="Avg Response Time (ms)",
                title="Response Time by Category"
            )
            st.plotly_chart(fig_cat_time, use_container_width=True)

        with col2:
            # Category quality scores
            fig_cat_quality = px.bar(
                df,
                x="Category",
                y="Quality Score",
                title="Quality Score by Category"
            )
            st.plotly_chart(fig_cat_quality, use_container_width=True)

    def render_detailed_results(self, results: List[Dict]):
        """Render detailed results table"""
        st.subheader("📋 Detailed Results")

        # Create detailed DataFrame
        detailed_data = []
        for result in results:
            if result.get("success", False):
                detailed_data.append({
                    "Model": result.get("model_used", result["model"]),
                    "Category": self.benchmark_categories[result["category"]]["name"],
                    "Question": result["question"][:100] + "..." if len(result["question"]) > 100 else result["question"],
                    "Response Time (ms)": round(result["response_time_ms"], 2),
                    "Quality Score": round(result.get("quality_score", 0), 3),
                    "Word Count": result.get("word_count", 0),
                    "Answer Preview": result["answer"][:150] + "..." if len(result["answer"]) > 150 else result["answer"]
                })

        if detailed_data:
            df = pd.DataFrame(detailed_data)
            st.dataframe(df, use_container_width=True, height=400)

            # Summary statistics
            st.subheader("📈 Summary Statistics")
            summary_stats = df.describe()
            st.dataframe(summary_stats)

    def render_benchmark_export(self):
        """Render export options for benchmark results"""
        st.markdown("---")
        st.subheader("📥 Export Benchmark Results")

        if 'benchmark_results' not in st.session_state:
            return

        results = st.session_state.benchmark_results
        metadata = st.session_state.benchmark_metadata

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Export as CSV"):
                # Create CSV-friendly data
                csv_data = []
                for result in results:
                    csv_data.append({
                        "timestamp": result.get("timestamp", ""),
                        "model": result.get("model", ""),
                        "model_used": result.get("model_used", ""),
                        "category": result.get("category", ""),
                        "question": result.get("question", ""),
                        "answer": result.get("answer", ""),
                        "response_time_ms": result.get("response_time_ms", 0),
                        "quality_score": result.get("quality_score", 0),
                        "word_count": result.get("word_count", 0),
                        "success": result.get("success", False)
                    })

                csv_df = pd.DataFrame(csv_data)
                csv_content = csv_df.to_csv(index=False)

                st.download_button(
                    label="Download CSV",
                    data=csv_content,
                    file_name=f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        with col2:
            if st.button("📄 Export as JSON"):
                export_data = {
                    "metadata": {
                        "models": metadata["models"],
                        "categories": metadata["categories"],
                        "total_time": metadata["total_time"],
                        "timestamp": metadata["timestamp"].isoformat()
                    },
                    "results": results
                }

                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2, default=str),
                    file_name=f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col3:
            if st.button("📈 Export Analysis"):
                analysis = self.analyze_benchmark_results(results)

                st.download_button(
                    label="Download Analysis",
                    data=json.dumps(analysis, indent=2, default=str),
                    file_name=f"benchmark_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

def main():
    """Main function to render model benchmarker"""
    st.set_page_config(
        page_title="DocuMind Model Benchmarker",
        page_icon="⚖️",
        layout="wide"
    )

    benchmarker = ModelBenchmarker()

    # Sidebar for information
    with st.sidebar:
        st.header("⚖️ Model Benchmarker")

        st.markdown("""
        **🎯 Benchmark Categories:**
        - General Knowledge
        - Technical Expertise
        - Code Generation
        - Problem Solving
        - Creativity & Communication

        **📊 Metrics Measured:**
        - Response time
        - Answer quality
        - Content length
        - Success rate

        **🔬 Analysis Features:**
        - Model comparison charts
        - Category performance
        - Statistical analysis
        - Export capabilities
        """)

        st.markdown("---")
        st.subheader("📈 Current Session")

        if 'benchmark_results' in st.session_state:
            results = st.session_state.benchmark_results
            successful = len([r for r in results if r.get("success", False)])
            st.metric("Tests Completed", len(results))
            st.metric("Successful Tests", successful)

    # Main interface
    benchmarker.render_benchmark_interface()
    benchmarker.render_benchmark_results()

if __name__ == "__main__":
    main()
