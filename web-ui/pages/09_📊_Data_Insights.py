"""
AI-Powered Data Insights & Visualization Engine
Generate intelligent data visualizations and insights using AI
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple, Any
import io
import base64
from scipy import stats

class DataInsightsEngine:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.chart_types = {
            "line_chart": "Line Chart - Time series and trends",
            "bar_chart": "Bar Chart - Categorical comparisons",
            "scatter_plot": "Scatter Plot - Relationships and correlations",
            "histogram": "Histogram - Distribution analysis",
            "box_plot": "Box Plot - Statistical summaries",
            "heatmap": "Heatmap - Correlation matrix",
            "pie_chart": "Pie Chart - Part-to-whole relationships",
            "area_chart": "Area Chart - Cumulative data",
            "violin_plot": "Violin Plot - Distribution density",
            "sunburst": "Sunburst - Hierarchical data"
        }

        self.analysis_types = {
            "descriptive": "Basic statistical summary and distributions",
            "correlation": "Correlation analysis and relationships",
            "trend": "Trend analysis and time series patterns",
            "outlier": "Outlier detection and anomaly analysis",
            "predictive": "Predictive insights and forecasting",
            "comparative": "Comparative analysis across groups",
            "segmentation": "Data segmentation and clustering"
        }

    def analyze_data_with_ai(self, df: pd.DataFrame, analysis_type: str, specific_request: str = "") -> Dict:
        """Use AI to analyze data and generate insights"""
        try:
            # Create data summary for AI
            data_summary = self.create_data_summary(df)

            # Create analysis prompt
            prompt = self.create_analysis_prompt(data_summary, analysis_type, specific_request)

            payload = {
                "q": prompt,
                "context_limit": 8,
                "model_preference": "llama3.1:70b"
            }

            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=90
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "insights": result.get("answer", ""),
                    "model_used": result.get("model_used", "unknown"),
                    "analysis_time": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_data_summary(self, df: pd.DataFrame) -> str:
        """Create a comprehensive data summary for AI analysis"""
        summary = f"Dataset Summary:\n"
        summary += f"- Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
        summary += f"- Columns: {list(df.columns)}\n\n"

        # Data types
        summary += "Data Types:\n"
        for col, dtype in df.dtypes.items():
            summary += f"- {col}: {dtype}\n"

        # Numerical columns statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary += f"\nNumerical Columns Statistics:\n"
            desc = df[numeric_cols].describe()
            summary += desc.to_string()

        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            summary += f"\nCategorical Columns:\n"
            for col in categorical_cols:
                unique_count = df[col].nunique()
                summary += f"- {col}: {unique_count} unique values\n"
                if unique_count <= 10:
                    summary += f"  Values: {list(df[col].unique())}\n"

        # Missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            summary += f"\nMissing Values:\n"
            for col, count in missing.items():
                if count > 0:
                    summary += f"- {col}: {count} ({count/len(df)*100:.1f}%)\n"

        # Sample data
        summary += f"\nFirst 3 rows:\n"
        summary += df.head(3).to_string()

        return summary

    def create_analysis_prompt(self, data_summary: str, analysis_type: str, specific_request: str) -> str:
        """Create specialized analysis prompt based on type"""
        base_prompt = f"""
Analyze this dataset and provide insights:

{data_summary}

Analysis Type: {analysis_type}
"""

        if specific_request:
            base_prompt += f"\nSpecific Request: {specific_request}\n"

        prompts = {
            "descriptive": base_prompt + """
Provide a descriptive analysis including:
1. Key characteristics of the dataset
2. Distribution patterns in numerical variables
3. Frequency patterns in categorical variables
4. Data quality observations
5. Notable patterns or interesting findings
""",

            "correlation": base_prompt + """
Analyze relationships and correlations:
1. Identify potential correlations between numerical variables
2. Suggest relationships worth investigating
3. Point out any strong positive or negative correlations
4. Recommend visualizations to explore relationships
5. Note any causation vs correlation considerations
""",

            "trend": base_prompt + """
Analyze trends and patterns:
1. Identify any time-based patterns (if applicable)
2. Look for increasing or decreasing trends
3. Identify seasonal or cyclical patterns
4. Point out any significant changes or anomalies
5. Suggest forecasting opportunities
""",

            "outlier": base_prompt + """
Perform outlier and anomaly detection:
1. Identify potential outliers in numerical columns
2. Look for unusual patterns or anomalies
3. Assess data quality issues
4. Suggest which outliers might be errors vs. genuine anomalies
5. Recommend outlier handling strategies
""",

            "predictive": base_prompt + """
Generate predictive insights:
1. Identify potential target variables for prediction
2. Suggest which features might be good predictors
3. Identify opportunities for forecasting
4. Recommend machine learning approaches
5. Highlight important variables for modeling
""",

            "comparative": base_prompt + """
Perform comparative analysis:
1. Compare different groups or categories in the data
2. Identify significant differences between segments
3. Highlight performance variations
4. Suggest meaningful comparisons to explore
5. Point out any surprising differences
""",

            "segmentation": base_prompt + """
Analyze data segmentation opportunities:
1. Identify natural groupings or clusters in the data
2. Suggest segmentation strategies
3. Point out variables that could be used for grouping
4. Identify distinct patterns in different segments
5. Recommend clustering approaches
"""
        }

        return prompts.get(analysis_type, prompts["descriptive"])

    def generate_automatic_visualizations(self, df: pd.DataFrame) -> List[go.Figure]:
        """Generate automatic visualizations based on data characteristics"""
        figures = []

        # Get numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # 1. Distribution plots for numeric columns
        if len(numeric_cols) > 0:
            for col in numeric_cols[:4]:  # Limit to first 4
                fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                figures.append(fig)

        # 2. Bar charts for categorical columns
        if len(categorical_cols) > 0:
            for col in categorical_cols[:3]:  # Limit to first 3
                if df[col].nunique() <= 20:  # Only if reasonable number of categories
                    value_counts = df[col].value_counts()
                    fig = px.bar(x=value_counts.index, y=value_counts.values,
                               title=f"Frequency of {col}")
                    figures.append(fig)

        # 3. Correlation heatmap if multiple numeric columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(corr_matrix,
                          title="Correlation Heatmap",
                          color_continuous_scale="RdBu_r",
                          aspect="auto")
            figures.append(fig)

        # 4. Scatter plots for pairs of numeric columns
        if len(numeric_cols) >= 2:
            col1, col2 = numeric_cols[0], numeric_cols[1]
            fig = px.scatter(df, x=col1, y=col2,
                           title=f"{col1} vs {col2}")
            figures.append(fig)

        # 5. Box plots if we have categorical and numeric
        if len(numeric_cols) > 0 and len(categorical_cols) > 0:
            num_col = numeric_cols[0]
            cat_col = categorical_cols[0]
            if df[cat_col].nunique() <= 10:  # Reasonable number of categories
                fig = px.box(df, x=cat_col, y=num_col,
                           title=f"{num_col} by {cat_col}")
                figures.append(fig)

        return figures

    def suggest_custom_visualizations(self, df: pd.DataFrame) -> List[Dict]:
        """Suggest custom visualizations based on data"""
        suggestions = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        # Time series suggestions
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append({
                "type": "line_chart",
                "title": "Time Series Analysis",
                "description": f"Track {numeric_cols[0]} over time",
                "x_axis": date_cols[0],
                "y_axis": numeric_cols[0]
            })

        # Comparison suggestions
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            suggestions.append({
                "type": "bar_chart",
                "title": "Category Comparison",
                "description": f"Compare {numeric_cols[0]} across {categorical_cols[0]}",
                "x_axis": categorical_cols[0],
                "y_axis": numeric_cols[0]
            })

        # Relationship suggestions
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "scatter_plot",
                "title": "Relationship Analysis",
                "description": f"Explore relationship between {numeric_cols[0]} and {numeric_cols[1]}",
                "x_axis": numeric_cols[0],
                "y_axis": numeric_cols[1]
            })

        # Distribution suggestions
        for col in numeric_cols[:2]:
            suggestions.append({
                "type": "histogram",
                "title": f"Distribution Analysis",
                "description": f"Analyze distribution of {col}",
                "x_axis": col,
                "y_axis": "Count"
            })

        return suggestions

    def create_custom_visualization(self, df: pd.DataFrame, chart_type: str, x_col: str, y_col: str = None, color_col: str = None) -> go.Figure:
        """Create custom visualization based on user selection"""
        try:
            if chart_type == "line_chart":
                fig = px.line(df, x=x_col, y=y_col, color=color_col,
                             title=f"Line Chart: {y_col} vs {x_col}")

            elif chart_type == "bar_chart":
                if y_col:
                    fig = px.bar(df, x=x_col, y=y_col, color=color_col,
                               title=f"Bar Chart: {y_col} by {x_col}")
                else:
                    # Value counts for single column
                    value_counts = df[x_col].value_counts()
                    fig = px.bar(x=value_counts.index, y=value_counts.values,
                               title=f"Frequency of {x_col}")

            elif chart_type == "scatter_plot":
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                               title=f"Scatter Plot: {y_col} vs {x_col}")

            elif chart_type == "histogram":
                fig = px.histogram(df, x=x_col, color=color_col,
                                 title=f"Histogram of {x_col}")

            elif chart_type == "box_plot":
                fig = px.box(df, x=x_col, y=y_col, color=color_col,
                           title=f"Box Plot: {y_col} by {x_col}")

            elif chart_type == "heatmap":
                if df.select_dtypes(include=[np.number]).shape[1] > 1:
                    corr = df.select_dtypes(include=[np.number]).corr()
                    fig = px.imshow(corr, title="Correlation Heatmap")
                else:
                    fig = go.Figure()
                    fig.add_annotation(text="Need multiple numeric columns for heatmap")

            elif chart_type == "pie_chart":
                value_counts = df[x_col].value_counts()
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                           title=f"Pie Chart of {x_col}")

            elif chart_type == "area_chart":
                fig = px.area(df, x=x_col, y=y_col, color=color_col,
                            title=f"Area Chart: {y_col} vs {x_col}")

            elif chart_type == "violin_plot":
                fig = px.violin(df, x=x_col, y=y_col, color=color_col,
                              title=f"Violin Plot: {y_col} by {x_col}")

            else:
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                               title=f"Default Scatter Plot")

            return fig

        except Exception as e:
            # Return error figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating visualization: {str(e)}",
                x=0.5, y=0.5, xref="paper", yref="paper"
            )
            return fig

    def render_data_upload(self):
        """Render data upload interface"""
        st.header("📊 AI-Powered Data Insights Engine")
        st.markdown("Upload data and get AI-generated insights and visualizations")

        # File upload
        uploaded_file = st.file_uploader(
            "Upload your dataset:",
            type=['csv', 'xlsx', 'json'],
            help="Supported formats: CSV, Excel, JSON"
        )

        if uploaded_file:
            try:
                # Load data based on file type
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    df = pd.read_json(uploaded_file)

                # Store in session state
                st.session_state.analysis_df = df
                st.session_state.filename = uploaded_file.name

                # Display basic info
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Rows", df.shape[0])

                with col2:
                    st.metric("Columns", df.shape[1])

                with col3:
                    st.metric("Numeric Columns", len(df.select_dtypes(include=[np.number]).columns))

                with col4:
                    st.metric("Missing Values", df.isnull().sum().sum())

                # Data preview
                st.subheader("📋 Data Preview")
                st.dataframe(df.head(10), use_container_width=True)

                # Column information
                with st.expander("📊 Column Information"):
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Type': df.dtypes,
                        'Null Count': df.isnull().sum(),
                        'Unique Values': [df[col].nunique() for col in df.columns]
                    })
                    st.dataframe(col_info, use_container_width=True)

                # Analysis options
                self.render_analysis_options()

            except Exception as e:
                st.error(f"Error loading file: {str(e)}")

    def render_analysis_options(self):
        """Render analysis options interface"""
        if 'analysis_df' not in st.session_state:
            return

        df = st.session_state.analysis_df

        st.markdown("---")
        st.subheader("🔍 AI Analysis Options")

        col1, col2 = st.columns([2, 1])

        with col1:
            analysis_type = st.selectbox(
                "Select Analysis Type:",
                options=list(self.analysis_types.keys()),
                format_func=lambda x: f"{x.title()} - {self.analysis_types[x]}"
            )

            specific_request = st.text_area(
                "Specific Analysis Request (optional):",
                placeholder="e.g., 'Focus on sales trends by region' or 'Identify factors affecting customer satisfaction'",
                height=100
            )

        with col2:
            st.markdown("**Analysis Options:**")
            generate_auto_viz = st.checkbox("Generate Automatic Visualizations", value=True)
            include_statistical = st.checkbox("Include Statistical Analysis", value=True)
            suggest_viz = st.checkbox("Suggest Custom Visualizations", value=True)

        # Run analysis button
        if st.button("🚀 Run AI Analysis", type="primary"):
            self.run_comprehensive_analysis(df, analysis_type, specific_request,
                                          generate_auto_viz, include_statistical, suggest_viz)

    def run_comprehensive_analysis(self, df: pd.DataFrame, analysis_type: str,
                                 specific_request: str, auto_viz: bool,
                                 statistical: bool, suggest_viz: bool):
        """Run comprehensive data analysis"""
        st.markdown("---")
        st.subheader("📊 Analysis Results")

        # AI Analysis
        with st.spinner("AI is analyzing your data..."):
            ai_analysis = self.analyze_data_with_ai(df, analysis_type, specific_request)

        if ai_analysis["success"]:
            st.success(f"✅ Analysis completed using {ai_analysis['model_used']}")

            # Display AI insights
            st.markdown("### 🧠 AI-Generated Insights")
            st.markdown(ai_analysis["insights"])

            # Store analysis
            if 'analysis_history' not in st.session_state:
                st.session_state.analysis_history = []

            st.session_state.analysis_history.append({
                "filename": st.session_state.filename,
                "analysis_type": analysis_type,
                "insights": ai_analysis["insights"],
                "timestamp": ai_analysis["analysis_time"]
            })
        else:
            st.error(f"AI Analysis failed: {ai_analysis['error']}")

        # Statistical Analysis
        if statistical:
            self.render_statistical_analysis(df)

        # Automatic Visualizations
        if auto_viz:
            self.render_automatic_visualizations(df)

        # Custom Visualization Suggestions
        if suggest_viz:
            self.render_visualization_suggestions(df)

    def render_statistical_analysis(self, df: pd.DataFrame):
        """Render statistical analysis"""
        st.markdown("### 📈 Statistical Analysis")

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📊 Descriptive Statistics")
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)

            with col2:
                st.markdown("#### 🔗 Correlation Analysis")
                if len(numeric_cols) > 1:
                    corr_matrix = df[numeric_cols].corr()
                    st.dataframe(corr_matrix, use_container_width=True)

                    # Find strongest correlations
                    corr_pairs = []
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                            corr_value = corr_matrix.iloc[i, j]
                            corr_pairs.append((col1, col2, corr_value))

                    corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)

                    st.markdown("**Strongest Correlations:**")
                    for col1, col2, corr in corr_pairs[:5]:
                        st.write(f"• {col1} ↔ {col2}: {corr:.3f}")
                else:
                    st.info("Need multiple numeric columns for correlation analysis")
        else:
            st.info("No numeric columns found for statistical analysis")

    def render_automatic_visualizations(self, df: pd.DataFrame):
        """Render automatic visualizations"""
        st.markdown("### 📊 Automatic Visualizations")

        with st.spinner("Generating visualizations..."):
            figures = self.generate_automatic_visualizations(df)

        if figures:
            # Display figures in a grid
            for i, fig in enumerate(figures):
                st.plotly_chart(fig, use_container_width=True, key=f"auto_viz_{i}")
        else:
            st.info("No automatic visualizations could be generated for this dataset")

    def render_visualization_suggestions(self, df: pd.DataFrame):
        """Render custom visualization suggestions and builder"""
        st.markdown("### 🎨 Custom Visualization Builder")

        suggestions = self.suggest_custom_visualizations(df)

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### 💡 Suggested Visualizations")

            for i, suggestion in enumerate(suggestions[:5]):
                if st.button(f"{suggestion['title']}", key=f"suggest_{i}"):
                    # Auto-fill the custom viz builder
                    st.session_state.selected_chart_type = suggestion["type"]
                    st.session_state.selected_x_axis = suggestion["x_axis"]
                    st.session_state.selected_y_axis = suggestion.get("y_axis")

        with col2:
            st.markdown("#### 🛠️ Build Custom Visualization")

            # Chart type selection
            chart_type = st.selectbox(
                "Chart Type:",
                options=list(self.chart_types.keys()),
                format_func=lambda x: self.chart_types[x],
                key="chart_type_select"
            )

            # Column selection
            columns = df.columns.tolist()

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                x_axis = st.selectbox("X-axis:", columns, key="x_axis_select")

            with col_b:
                y_axis_options = ["None"] + columns
                y_axis = st.selectbox("Y-axis:", y_axis_options, key="y_axis_select")
                y_axis = None if y_axis == "None" else y_axis

            with col_c:
                color_options = ["None"] + columns
                color_col = st.selectbox("Color by:", color_options, key="color_select")
                color_col = None if color_col == "None" else color_col

            # Generate custom visualization
            if st.button("📊 Generate Visualization"):
                try:
                    custom_fig = self.create_custom_visualization(df, chart_type, x_axis, y_axis, color_col)
                    st.plotly_chart(custom_fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating visualization: {str(e)}")

    def render_export_options(self):
        """Render export options"""
        if 'analysis_df' not in st.session_state:
            return

        st.markdown("---")
        st.subheader("📥 Export Options")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Export Analysis Report"):
                if 'analysis_history' in st.session_state and st.session_state.analysis_history:
                    latest_analysis = st.session_state.analysis_history[-1]

                    report = f"""
DATA ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Dataset: {latest_analysis['filename']}
Analysis Type: {latest_analysis['analysis_type']}

AI-GENERATED INSIGHTS:
{latest_analysis['insights']}

DATASET SUMMARY:
{self.create_data_summary(st.session_state.analysis_df)}
"""

                    st.download_button(
                        label="Download Report",
                        data=report,
                        file_name=f"data_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

        with col2:
            if st.button("📊 Export Processed Data"):
                df = st.session_state.analysis_df
                csv_data = df.to_csv(index=False)

                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        with col3:
            if st.button("📈 Export Summary Stats"):
                df = st.session_state.analysis_df
                numeric_cols = df.select_dtypes(include=[np.number]).columns

                if len(numeric_cols) > 0:
                    stats_data = df[numeric_cols].describe()
                    stats_csv = stats_data.to_csv()

                    st.download_button(
                        label="Download Statistics",
                        data=stats_csv,
                        file_name=f"summary_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )

def main():
    """Main function to render data insights engine"""
    st.set_page_config(
        page_title="DocuMind Data Insights",
        page_icon="📊",
        layout="wide"
    )

    engine = DataInsightsEngine()

    # Sidebar for information
    with st.sidebar:
        st.header("📊 Data Insights Engine")

        st.markdown("""
        **🎯 Analysis Types:**
        - Descriptive analysis
        - Correlation analysis
        - Trend analysis
        - Outlier detection
        - Predictive insights
        - Comparative analysis
        - Data segmentation

        **📈 Visualization Types:**
        - Line charts
        - Bar charts
        - Scatter plots
        - Histograms
        - Box plots
        - Heatmaps
        - Pie charts
        - And more...

        **🤖 AI Features:**
        - Automatic insight generation
        - Smart visualization suggestions
        - Statistical analysis
        - Data quality assessment
        """)

        st.markdown("---")
        st.subheader("📈 Current Session")

        if 'analysis_df' in st.session_state:
            df = st.session_state.analysis_df
            st.metric("Dataset Rows", df.shape[0])
            st.metric("Dataset Columns", df.shape[1])

        if 'analysis_history' in st.session_state:
            st.metric("Analyses Run", len(st.session_state.analysis_history))

    # Main interface
    engine.render_data_upload()
    engine.render_export_options()

if __name__ == "__main__":
    main()
