"""
AI Knowledge Graph Visualizer
Interactive knowledge mapping and relationship discovery
"""
import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List, Optional, Tuple
import re
from collections import defaultdict, Counter

class KnowledgeGraphVisualizer:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url
        self.graph_types = {
            "concept_map": "Concept relationships and hierarchies",
            "entity_network": "Named entities and their connections",
            "topic_clusters": "Topic clustering and similarity mapping",
            "knowledge_flow": "Knowledge flow and dependency mapping",
            "semantic_web": "Semantic relationships and ontologies"
        }

    def extract_entities_and_relations(self, text: str, graph_type: str) -> Dict:
        """Extract entities and relationships using AI"""
        try:
            # Create specialized prompt based on graph type
            prompt = self.create_extraction_prompt(text, graph_type)

            payload = {
                "q": prompt,
                "context_limit": 10,
                "model_preference": "llama3.1:70b"
            }

            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                # Parse the AI response to extract structured data
                parsed_data = self.parse_ai_response(result.get("answer", ""), graph_type)

                return {
                    "success": True,
                    "entities": parsed_data.get("entities", []),
                    "relationships": parsed_data.get("relationships", []),
                    "metadata": {
                        "model_used": result.get("model_used", "unknown"),
                        "extraction_time": datetime.now().isoformat(),
                        "graph_type": graph_type
                    }
                }
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_extraction_prompt(self, text: str, graph_type: str) -> str:
        """Create specialized extraction prompt"""
        base_text = text[:4000]  # Limit text length

        prompts = {
            "concept_map": f"""
            Analyze this text and extract concepts and their relationships:

            {base_text}

            Please identify:
            1. Main concepts (nouns, ideas, topics)
            2. Relationships between concepts (is-a, part-of, related-to, depends-on)
            3. Hierarchical structures (parent-child relationships)

            Format your response as:
            ENTITIES: concept1, concept2, concept3...
            RELATIONSHIPS: concept1 -> relates_to -> concept2; concept2 -> is_part_of -> concept3...
            """,

            "entity_network": f"""
            Extract named entities and their relationships from this text:

            {base_text}

            Identify:
            1. People, organizations, locations, technologies
            2. How these entities are connected
            3. The nature of their relationships

            Format as:
            ENTITIES: entity1 (type), entity2 (type), entity3 (type)...
            RELATIONSHIPS: entity1 -> works_with -> entity2; entity2 -> located_in -> entity3...
            """,

            "topic_clusters": f"""
            Identify topics and group related concepts from this text:

            {base_text}

            Extract:
            1. Main topics and themes
            2. Related concepts for each topic
            3. Connections between topics

            Format as:
            ENTITIES: topic1, topic2, subtopic1, subtopic2...
            RELATIONSHIPS: subtopic1 -> belongs_to -> topic1; topic1 -> relates_to -> topic2...
            """,

            "knowledge_flow": f"""
            Map knowledge flow and dependencies in this text:

            {base_text}

            Identify:
            1. Knowledge components and skills
            2. Prerequisites and dependencies
            3. Learning or process sequences

            Format as:
            ENTITIES: skill1, skill2, process1, requirement1...
            RELATIONSHIPS: skill1 -> requires -> requirement1; process1 -> leads_to -> skill2...
            """,

            "semantic_web": f"""
            Extract semantic relationships and create an ontology from this text:

            {base_text}

            Identify:
            1. Semantic concepts and categories
            2. Properties and attributes
            3. Hierarchical and associative relationships

            Format as:
            ENTITIES: class1, property1, instance1, category1...
            RELATIONSHIPS: instance1 -> is_instance_of -> class1; property1 -> applies_to -> class1...
            """
        }

        return prompts.get(graph_type, prompts["concept_map"])

    def parse_ai_response(self, response: str, graph_type: str) -> Dict:
        """Parse AI response to extract entities and relationships"""
        entities = []
        relationships = []

        try:
            # Look for ENTITIES section
            entities_match = re.search(r'ENTITIES:\s*(.+?)(?=RELATIONSHIPS:|$)', response, re.IGNORECASE | re.DOTALL)
            if entities_match:
                entities_text = entities_match.group(1).strip()
                # Split by commas and clean up
                entities = [e.strip().split('(')[0].strip() for e in entities_text.split(',') if e.strip()]

            # Look for RELATIONSHIPS section
            relationships_match = re.search(r'RELATIONSHIPS:\s*(.+?)$', response, re.IGNORECASE | re.DOTALL)
            if relationships_match:
                relationships_text = relationships_match.group(1).strip()
                # Parse relationships (format: entity1 -> relation -> entity2)
                for rel_line in relationships_text.split(';'):
                    rel_parts = [part.strip() for part in rel_line.split('->')]
                    if len(rel_parts) >= 3:
                        source = rel_parts[0].strip()
                        relation = rel_parts[1].strip()
                        target = rel_parts[2].strip()
                        relationships.append({
                            "source": source,
                            "target": target,
                            "relation": relation
                        })

            # If parsing fails, try alternative extraction
            if not entities or not relationships:
                entities, relationships = self.fallback_extraction(response)

        except Exception as e:
            st.warning(f"Parsing error: {e}. Using fallback extraction.")
            entities, relationships = self.fallback_extraction(response)

        return {"entities": entities, "relationships": relationships}

    def fallback_extraction(self, response: str) -> Tuple[List[str], List[Dict]]:
        """Fallback entity and relationship extraction"""
        # Simple extraction based on common patterns
        words = response.split()

        # Extract potential entities (capitalized words, technical terms)
        entities = []
        for word in words:
            word = word.strip('.,!?;:"()[]{}')
            if (word.istitle() or word.isupper()) and len(word) > 2:
                entities.append(word)

        # Remove duplicates and limit
        entities = list(set(entities))[:20]

        # Create simple relationships based on proximity
        relationships = []
        for i, entity1 in enumerate(entities[:10]):
            for entity2 in entities[i+1:i+3]:
                relationships.append({
                    "source": entity1,
                    "target": entity2,
                    "relation": "related_to"
                })

        return entities, relationships

    def create_network_graph(self, entities: List[str], relationships: List[Dict]) -> go.Figure:
        """Create interactive network graph using Plotly"""
        # Create NetworkX graph
        G = nx.Graph()

        # Add nodes
        for entity in entities:
            G.add_node(entity)

        # Add edges
        edge_traces = []
        edge_info = []

        for rel in relationships:
            source = rel["source"]
            target = rel["target"]
            relation = rel["relation"]

            if source in entities and target in entities:
                G.add_edge(source, target, relation=relation)
                edge_info.append(f"{source} -> {relation} -> {target}")

        # Create layout
        try:
            pos = nx.spring_layout(G, k=1, iterations=50)
        except:
            # Fallback to random positions if spring layout fails
            pos = {node: (i % 5, i // 5) for i, node in enumerate(entities)}

        # Create edge traces
        edge_x = []
        edge_y = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='lightblue'),
            hoverinfo='none',
            mode='lines'
        )

        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            # Size based on degree (number of connections)
            node_size.append(20 + G.degree(node) * 5)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=node_size,
                color='lightcoral',
                line=dict(width=2, color='darkred')
            )
        )

        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Knowledge Graph Visualization',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Interactive Knowledge Graph",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor="left", yanchor="bottom",
                               font=dict(color="grey", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))

        return fig

    def create_hierarchical_graph(self, entities: List[str], relationships: List[Dict]) -> go.Figure:
        """Create hierarchical tree visualization"""
        # Build hierarchy based on relationships
        hierarchy = defaultdict(list)
        roots = set(entities)

        for rel in relationships:
            if rel["relation"] in ["is_part_of", "belongs_to", "is_instance_of"]:
                parent = rel["target"]
                child = rel["source"]
                hierarchy[parent].append(child)
                roots.discard(child)

        # Create tree structure
        fig = go.Figure()

        # Simple hierarchical layout
        levels = {}
        positions = {}

        # Assign levels
        for root in list(roots)[:5]:  # Limit to 5 roots
            self._assign_levels(root, hierarchy, levels, 0)

        # Assign positions
        level_counts = defaultdict(int)
        for node, level in levels.items():
            positions[node] = (level_counts[level], -level)
            level_counts[level] += 1

        # Add edges
        for parent, children in hierarchy.items():
            if parent in positions:
                for child in children:
                    if child in positions:
                        fig.add_trace(go.Scatter(
                            x=[positions[parent][0], positions[child][0]],
                            y=[positions[parent][1], positions[child][1]],
                            mode='lines',
                            line=dict(color='lightblue', width=2),
                            showlegend=False
                        ))

        # Add nodes
        x_vals = [pos[0] for pos in positions.values()]
        y_vals = [pos[1] for pos in positions.values()]
        texts = list(positions.keys())

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='markers+text',
            text=texts,
            textposition="middle center",
            marker=dict(size=15, color='lightcoral'),
            showlegend=False
        ))

        fig.update_layout(
            title="Hierarchical Knowledge Structure",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )

        return fig

    def _assign_levels(self, node: str, hierarchy: Dict, levels: Dict, level: int):
        """Recursively assign levels for hierarchical layout"""
        if node not in levels:
            levels[node] = level
            for child in hierarchy.get(node, []):
                self._assign_levels(child, hierarchy, levels, level + 1)

    def render_graph_interface(self):
        """Render the main knowledge graph interface"""
        st.header("🕸️ AI Knowledge Graph Visualizer")
        st.markdown("Create interactive knowledge graphs from text using AI")

        # Input section
        col1, col2 = st.columns([2, 1])

        with col1:
            input_method = st.radio(
                "Choose input method:",
                ["Enter Text", "Upload Document", "Use Previous Analysis"]
            )

            text_input = ""

            if input_method == "Enter Text":
                text_input = st.text_area(
                    "Enter text to analyze:",
                    placeholder="Enter the text you want to create a knowledge graph from...",
                    height=200
                )

            elif input_method == "Upload Document":
                uploaded_file = st.file_uploader(
                    "Upload document:",
                    type=['txt', 'md'],
                    help="Text files only for knowledge graph generation"
                )

                if uploaded_file:
                    text_input = str(uploaded_file.read(), "utf-8")
                    st.text_area("Document content:", text_input[:500] + "...", height=100)

            elif input_method == "Use Previous Analysis":
                if 'document_text' in st.session_state:
                    text_input = st.session_state.document_text
                    st.info(f"Using previously uploaded document: {st.session_state.get('document_name', 'Unknown')}")
                else:
                    st.warning("No previous document analysis found. Please upload a document first.")

        with col2:
            graph_type = st.selectbox(
                "Graph Type:",
                options=list(self.graph_types.keys()),
                format_func=lambda x: f"{x.replace('_', ' ').title()}"
            )

            st.markdown(f"**Description:**")
            st.write(self.graph_types[graph_type])

            visualization_style = st.selectbox(
                "Visualization Style:",
                ["Network Graph", "Hierarchical Tree", "Clustered Layout"]
            )

        # Generate graph button
        if st.button("🚀 Generate Knowledge Graph", type="primary", disabled=not text_input):
            self.generate_knowledge_graph(text_input, graph_type, visualization_style)

    def generate_knowledge_graph(self, text: str, graph_type: str, viz_style: str):
        """Generate and display knowledge graph"""
        st.markdown("---")
        st.subheader("🕸️ Knowledge Graph Generation")

        with st.spinner("Analyzing text and extracting knowledge relationships..."):
            extraction_result = self.extract_entities_and_relations(text, graph_type)

        if not extraction_result["success"]:
            st.error(f"Failed to extract knowledge: {extraction_result['error']}")
            return

        entities = extraction_result["entities"]
        relationships = extraction_result["relationships"]
        metadata = extraction_result["metadata"]

        st.success(f"✅ Extracted {len(entities)} entities and {len(relationships)} relationships using {metadata['model_used']}")

        # Display statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Entities Found", len(entities))

        with col2:
            st.metric("Relationships", len(relationships))

        with col3:
            if relationships:
                relation_types = [rel["relation"] for rel in relationships]
                most_common = Counter(relation_types).most_common(1)[0][0]
                st.metric("Most Common Relation", most_common)

        # Store in session state
        st.session_state.knowledge_graph = {
            "entities": entities,
            "relationships": relationships,
            "metadata": metadata,
            "text": text
        }

        # Generate visualization
        self.render_knowledge_visualization(entities, relationships, viz_style)

        # Show detailed analysis
        self.render_graph_analysis(entities, relationships)

    def render_knowledge_visualization(self, entities: List[str], relationships: List[Dict], style: str):
        """Render knowledge graph visualization"""
        st.subheader("📊 Knowledge Graph Visualization")

        if style == "Network Graph":
            fig = self.create_network_graph(entities, relationships)
            st.plotly_chart(fig, use_container_width=True)

        elif style == "Hierarchical Tree":
            fig = self.create_hierarchical_graph(entities, relationships)
            st.plotly_chart(fig, use_container_width=True)

        elif style == "Clustered Layout":
            # Create clustered visualization
            fig = self.create_clustered_graph(entities, relationships)
            st.plotly_chart(fig, use_container_width=True)

    def create_clustered_graph(self, entities: List[str], relationships: List[Dict]) -> go.Figure:
        """Create clustered layout visualization"""
        # Group entities by relationship types
        clusters = defaultdict(list)

        for rel in relationships:
            relation_type = rel["relation"]
            clusters[relation_type].extend([rel["source"], rel["target"]])

        # Remove duplicates
        for cluster_name in clusters:
            clusters[cluster_name] = list(set(clusters[cluster_name]))

        fig = go.Figure()

        # Create traces for each cluster
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']

        for i, (cluster_name, cluster_entities) in enumerate(clusters.items()):
            if i >= len(colors):
                break

            # Position entities in cluster
            cluster_x = []
            cluster_y = []

            for j, entity in enumerate(cluster_entities[:10]):  # Limit to 10 per cluster
                angle = 2 * 3.14159 * j / len(cluster_entities)
                x = i * 3 + 2 * (0.5 + 0.5 * (j % 2)) * abs(angle)
                y = 2 * (j // 2)
                cluster_x.append(x)
                cluster_y.append(y)

            fig.add_trace(go.Scatter(
                x=cluster_x,
                y=cluster_y,
                mode='markers+text',
                text=cluster_entities[:10],
                textposition="middle center",
                marker=dict(size=15, color=colors[i % len(colors)]),
                name=cluster_name,
                showlegend=True
            ))

        fig.update_layout(
            title="Clustered Knowledge Graph",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )

        return fig

    def render_graph_analysis(self, entities: List[str], relationships: List[Dict]):
        """Render detailed graph analysis"""
        st.markdown("---")
        st.subheader("📋 Knowledge Graph Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 Key Entities")

            # Entity frequency analysis
            entity_mentions = Counter()
            for rel in relationships:
                entity_mentions[rel["source"]] += 1
                entity_mentions[rel["target"]] += 1

            top_entities = entity_mentions.most_common(10)

            if top_entities:
                entity_df = pd.DataFrame(top_entities, columns=["Entity", "Connections"])
                st.dataframe(entity_df, use_container_width=True)

                # Entity importance chart
                fig = px.bar(entity_df, x="Entity", y="Connections", title="Entity Importance by Connections")
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 🔗 Relationship Types")

            # Relationship analysis
            relation_counts = Counter([rel["relation"] for rel in relationships])

            if relation_counts:
                relation_df = pd.DataFrame(relation_counts.most_common(), columns=["Relation", "Count"])
                st.dataframe(relation_df, use_container_width=True)

                # Relationship distribution chart
                fig = px.pie(relation_df, values="Count", names="Relation", title="Relationship Distribution")
                st.plotly_chart(fig, use_container_width=True)

        # Detailed relationships table
        st.markdown("#### 📊 All Relationships")

        if relationships:
            relations_df = pd.DataFrame(relationships)
            st.dataframe(relations_df, use_container_width=True)

        # Export options
        self.render_graph_export()

    def render_graph_export(self):
        """Render export options for knowledge graph"""
        st.markdown("---")
        st.subheader("📥 Export Knowledge Graph")

        if 'knowledge_graph' not in st.session_state:
            return

        graph_data = st.session_state.knowledge_graph

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Export as JSON"):
                export_data = {
                    "metadata": graph_data["metadata"],
                    "entities": graph_data["entities"],
                    "relationships": graph_data["relationships"],
                    "export_timestamp": datetime.now().isoformat()
                }

                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"knowledge_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        with col2:
            if st.button("📊 Export as CSV"):
                relationships_df = pd.DataFrame(graph_data["relationships"])
                csv_data = relationships_df.to_csv(index=False)

                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"relationships_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

        with col3:
            if st.button("🕸️ Export as GraphML"):
                # Create GraphML format (simplified)
                graphml_content = self.create_graphml_export(graph_data["entities"], graph_data["relationships"])

                st.download_button(
                    label="Download GraphML",
                    data=graphml_content,
                    file_name=f"knowledge_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.graphml",
                    mime="application/xml"
                )

    def create_graphml_export(self, entities: List[str], relationships: List[Dict]) -> str:
        """Create GraphML format export"""
        graphml = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="name" for="node" attr.name="name" attr.type="string"/>
  <key id="relation" for="edge" attr.name="relation" attr.type="string"/>
  <graph id="knowledge_graph" edgedefault="directed">
'''

        # Add nodes
        for i, entity in enumerate(entities):
            graphml += f'    <node id="n{i}"><data key="name">{entity}</data></node>\n'

        # Add edges
        entity_to_id = {entity: f"n{i}" for i, entity in enumerate(entities)}

        for i, rel in enumerate(relationships):
            source_id = entity_to_id.get(rel["source"])
            target_id = entity_to_id.get(rel["target"])

            if source_id and target_id:
                graphml += f'    <edge id="e{i}" source="{source_id}" target="{target_id}"><data key="relation">{rel["relation"]}</data></edge>\n'

        graphml += '''  </graph>
</graphml>'''

        return graphml

def main():
    """Main function to render knowledge graph visualizer"""
    st.set_page_config(
        page_title="DocuMind Knowledge Graph",
        page_icon="🕸️",
        layout="wide"
    )

    visualizer = KnowledgeGraphVisualizer()

    # Sidebar for information
    with st.sidebar:
        st.header("🕸️ Knowledge Graph")

        st.markdown("""
        **🎯 Graph Types:**
        - Concept mapping
        - Entity networks
        - Topic clustering
        - Knowledge flow
        - Semantic web

        **📊 Visualizations:**
        - Interactive network graphs
        - Hierarchical trees
        - Clustered layouts

        **💾 Export Formats:**
        - JSON (structured data)
        - CSV (relationships)
        - GraphML (graph format)
        """)

        st.markdown("---")
        st.subheader("📈 Current Session")

        if 'knowledge_graph' in st.session_state:
            graph_data = st.session_state.knowledge_graph
            st.metric("Entities", len(graph_data["entities"]))
            st.metric("Relationships", len(graph_data["relationships"]))

    # Main interface
    visualizer.render_graph_interface()

if __name__ == "__main__":
    main()
