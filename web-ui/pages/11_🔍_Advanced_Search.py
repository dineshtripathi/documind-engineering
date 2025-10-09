"""
Advanced Search & Knowledge Discovery
Multi-modal search across documents with semantic understanding
"""
import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import networkx as nx
from collections import Counter, defaultdict
import hashlib

class AdvancedSearchEngine:
    def __init__(self, api_base_url: str = "http://localhost:7001"):
        self.api_base_url = api_base_url

        # Search types
        self.search_types = {
            "semantic": "AI-powered semantic search",
            "keyword": "Traditional keyword matching",
            "fuzzy": "Fuzzy matching for typos",
            "boolean": "Boolean logic search",
            "regex": "Regular expression patterns",
            "conceptual": "Concept and theme search",
            "contextual": "Context-aware search",
            "multi_modal": "Search across text, metadata, and structure"
        }

        # Search scopes
        self.search_scopes = {
            "all": "Search everything",
            "documents": "Documents only",
            "conversations": "Chat history",
            "code": "Code repositories",
            "metadata": "Document metadata",
            "entities": "Named entities",
            "relationships": "Entity relationships",
            "summaries": "Generated summaries"
        }

        # Initialize search index
        if 'search_index' not in st.session_state:
            st.session_state.search_index = self.initialize_search_index()

    def initialize_search_index(self) -> Dict:
        """Initialize the search index with sample data"""
        return {
            "documents": [],
            "conversations": [],
            "entities": {},
            "relationships": [],
            "embeddings": {},
            "tfidf_matrix": None,
            "vectorizer": None,
            "last_updated": datetime.now()
        }

    def add_to_search_index(self, content: str, content_type: str, metadata: Dict = None):
        """Add content to the search index"""
        doc_id = hashlib.md5(content.encode()).hexdigest()[:12]

        document = {
            "id": doc_id,
            "content": content,
            "type": content_type,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat(),
            "word_count": len(content.split()),
            "entities": self.extract_entities(content),
            "summary": self.generate_summary(content)
        }

        st.session_state.search_index["documents"].append(document)
        self.update_search_vectors()

        return doc_id

    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text"""
        # Simple entity extraction (in production, use spaCy or similar)
        entities = []

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            entities.append({"text": email, "type": "EMAIL", "start": text.find(email)})

        # Date pattern
        date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
        dates = re.findall(date_pattern, text)
        for date in dates:
            entities.append({"text": date, "type": "DATE", "start": text.find(date)})

        # Number pattern
        number_pattern = r'\b\d+(?:,\d{3})*(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, text)
        for number in numbers:
            if len(number) > 3:  # Only significant numbers
                entities.append({"text": number, "type": "NUMBER", "start": text.find(number)})

        # Capitalized words (potential proper nouns)
        proper_noun_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        proper_nouns = re.findall(proper_noun_pattern, text)
        for noun in set(proper_nouns):  # Remove duplicates
            if len(noun.split()) <= 3:  # Reasonable entity length
                entities.append({"text": noun, "type": "ENTITY", "start": text.find(noun)})

        return entities

    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of the text"""
        sentences = text.split('.')
        if len(sentences) <= 2:
            return text[:max_length] + "..." if len(text) > max_length else text

        # Simple extractive summarization
        return '. '.join(sentences[:2]) + "..."

    def update_search_vectors(self):
        """Update TF-IDF vectors for search"""
        documents = st.session_state.search_index["documents"]

        if not documents:
            return

        texts = [doc["content"] for doc in documents]

        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )

        tfidf_matrix = vectorizer.fit_transform(texts)

        st.session_state.search_index["tfidf_matrix"] = tfidf_matrix
        st.session_state.search_index["vectorizer"] = vectorizer
        st.session_state.search_index["last_updated"] = datetime.now()

    def semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Perform semantic search using AI"""
        try:
            # Use AI for semantic understanding
            search_prompt = f"""
            Analyze this search query and identify key concepts, entities, and intent:
            Query: "{query}"

            Provide:
            1. Key concepts and themes
            2. Search intent
            3. Related terms and synonyms
            4. Entity types to look for

            Format as JSON with keys: concepts, intent, related_terms, entity_types
            """

            semantic_analysis = self.call_ai_api(search_prompt)

            # Perform traditional search with expanded terms
            results = self.keyword_search(query, limit)

            # Enhance with semantic scoring
            for result in results:
                result["semantic_score"] = self.calculate_semantic_score(
                    query, result["content"], semantic_analysis
                )

            # Re-rank by semantic score
            results.sort(key=lambda x: x.get("semantic_score", 0), reverse=True)

            return results

        except Exception as e:
            st.error(f"Semantic search error: {e}")
            return self.keyword_search(query, limit)

    def keyword_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Perform keyword-based search"""
        documents = st.session_state.search_index["documents"]

        if not documents:
            return []

        vectorizer = st.session_state.search_index["vectorizer"]
        tfidf_matrix = st.session_state.search_index["tfidf_matrix"]

        if vectorizer is None or tfidf_matrix is None:
            # Fallback to simple text search
            return self.simple_text_search(query, limit)

        # Transform query
        query_vector = vectorizer.transform([query])

        # Calculate similarities
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

        # Get top results
        top_indices = similarities.argsort()[-limit:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include relevant results
                doc = documents[idx].copy()
                doc["relevance_score"] = similarities[idx]
                doc["match_type"] = "keyword"
                results.append(doc)

        return results

    def simple_text_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Simple text-based search fallback"""
        documents = st.session_state.search_index["documents"]
        query_lower = query.lower()

        results = []
        for doc in documents:
            content_lower = doc["content"].lower()
            if query_lower in content_lower:
                # Calculate simple relevance score
                matches = content_lower.count(query_lower)
                score = matches / len(doc["content"].split())

                doc_copy = doc.copy()
                doc_copy["relevance_score"] = score
                doc_copy["match_type"] = "simple"
                results.append(doc_copy)

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def fuzzy_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Fuzzy search for handling typos"""
        from difflib import SequenceMatcher

        documents = st.session_state.search_index["documents"]
        results = []

        for doc in documents:
            # Calculate fuzzy similarity
            similarity = SequenceMatcher(None, query.lower(), doc["content"].lower()).ratio()

            if similarity > 0.3:  # Threshold for fuzzy matching
                doc_copy = doc.copy()
                doc_copy["relevance_score"] = similarity
                doc_copy["match_type"] = "fuzzy"
                results.append(doc_copy)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def boolean_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Boolean search with AND, OR, NOT operators"""
        documents = st.session_state.search_index["documents"]

        # Parse boolean query (simplified)
        query = query.lower()

        # Handle AND operator
        if " and " in query:
            terms = [term.strip() for term in query.split(" and ")]
            return self.search_with_all_terms(terms, limit)

        # Handle OR operator
        elif " or " in query:
            terms = [term.strip() for term in query.split(" or ")]
            return self.search_with_any_terms(terms, limit)

        # Handle NOT operator
        elif " not " in query:
            parts = query.split(" not ")
            include_terms = parts[0].strip()
            exclude_terms = parts[1].strip() if len(parts) > 1 else ""
            return self.search_with_exclusion(include_terms, exclude_terms, limit)

        else:
            return self.keyword_search(query, limit)

    def search_with_all_terms(self, terms: List[str], limit: int) -> List[Dict]:
        """Search for documents containing all terms"""
        documents = st.session_state.search_index["documents"]
        results = []

        for doc in documents:
            content_lower = doc["content"].lower()
            if all(term in content_lower for term in terms):
                score = sum(content_lower.count(term) for term in terms) / len(doc["content"].split())
                doc_copy = doc.copy()
                doc_copy["relevance_score"] = score
                doc_copy["match_type"] = "boolean_and"
                results.append(doc_copy)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def search_with_any_terms(self, terms: List[str], limit: int) -> List[Dict]:
        """Search for documents containing any terms"""
        documents = st.session_state.search_index["documents"]
        results = []

        for doc in documents:
            content_lower = doc["content"].lower()
            matching_terms = [term for term in terms if term in content_lower]

            if matching_terms:
                score = sum(content_lower.count(term) for term in matching_terms) / len(doc["content"].split())
                doc_copy = doc.copy()
                doc_copy["relevance_score"] = score
                doc_copy["match_type"] = "boolean_or"
                doc_copy["matching_terms"] = matching_terms
                results.append(doc_copy)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def search_with_exclusion(self, include_term: str, exclude_term: str, limit: int) -> List[Dict]:
        """Search with inclusion and exclusion terms"""
        documents = st.session_state.search_index["documents"]
        results = []

        for doc in documents:
            content_lower = doc["content"].lower()
            if include_term in content_lower and exclude_term not in content_lower:
                score = content_lower.count(include_term) / len(doc["content"].split())
                doc_copy = doc.copy()
                doc_copy["relevance_score"] = score
                doc_copy["match_type"] = "boolean_not"
                results.append(doc_copy)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def regex_search(self, pattern: str, limit: int = 10) -> List[Dict]:
        """Regular expression search"""
        documents = st.session_state.search_index["documents"]
        results = []

        try:
            regex = re.compile(pattern, re.IGNORECASE)

            for doc in documents:
                matches = regex.findall(doc["content"])
                if matches:
                    doc_copy = doc.copy()
                    doc_copy["relevance_score"] = len(matches) / len(doc["content"].split())
                    doc_copy["match_type"] = "regex"
                    doc_copy["matches"] = matches
                    results.append(doc_copy)

            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:limit]

        except re.error as e:
            st.error(f"Invalid regex pattern: {e}")
            return []

    def entity_search(self, entity_type: str, entity_value: str = None, limit: int = 10) -> List[Dict]:
        """Search by entity type or specific entity"""
        documents = st.session_state.search_index["documents"]
        results = []

        for doc in documents:
            matching_entities = []

            for entity in doc.get("entities", []):
                if entity["type"] == entity_type.upper():
                    if entity_value is None or entity_value.lower() in entity["text"].lower():
                        matching_entities.append(entity)

            if matching_entities:
                doc_copy = doc.copy()
                doc_copy["relevance_score"] = len(matching_entities) / max(len(doc.get("entities", [])), 1)
                doc_copy["match_type"] = "entity"
                doc_copy["matching_entities"] = matching_entities
                results.append(doc_copy)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def conceptual_search(self, concept: str, limit: int = 10) -> List[Dict]:
        """Search by concept using AI understanding"""
        try:
            concept_prompt = f"""
            Find documents related to the concept: "{concept}"

            Expand this concept to include:
            1. Related topics and themes
            2. Synonyms and alternative terms
            3. Sub-concepts and categories
            4. Real-world applications

            Return a comprehensive list of search terms.
            """

            expanded_terms = self.call_ai_api(concept_prompt)

            # Use expanded terms for search
            all_results = []

            # Primary concept search
            primary_results = self.semantic_search(concept, limit)
            for result in primary_results:
                result["concept_relevance"] = "primary"
                all_results.append(result)

            # Related terms search
            if len(all_results) < limit:
                related_results = self.keyword_search(expanded_terms[:500], limit - len(all_results))
                for result in related_results:
                    result["concept_relevance"] = "related"
                    all_results.append(result)

            # Remove duplicates and sort
            seen_ids = set()
            unique_results = []
            for result in all_results:
                if result["id"] not in seen_ids:
                    seen_ids.add(result["id"])
                    unique_results.append(result)

            return unique_results[:limit]

        except Exception as e:
            st.error(f"Conceptual search error: {e}")
            return self.semantic_search(concept, limit)

    def calculate_semantic_score(self, query: str, content: str, semantic_analysis: str) -> float:
        """Calculate semantic relevance score"""
        # Simple semantic scoring based on content overlap
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        overlap = len(query_words.intersection(content_words))
        total_words = len(query_words.union(content_words))

        base_score = overlap / total_words if total_words > 0 else 0

        # Boost score based on semantic analysis
        if semantic_analysis and any(word in content.lower() for word in ["concept", "theme", "related"]):
            base_score *= 1.2

        return min(base_score, 1.0)

    def call_ai_api(self, prompt: str, model: str = "auto") -> str:
        """Call the AI API for semantic understanding"""
        try:
            payload = {
                "q": prompt,
                "context_limit": 5,
                "model_preference": model
            }

            response = requests.post(
                f"{self.api_base_url}/ask",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("answer", "")
            else:
                return ""

        except Exception:
            return ""

    def render_search_interface(self):
        """Render the main search interface"""
        st.header("🔍 Advanced Search & Knowledge Discovery")
        st.markdown("Multi-modal search with semantic understanding")

        # Search input
        col1, col2 = st.columns([3, 1])

        with col1:
            query = st.text_input(
                "Search Query:",
                placeholder="Enter your search query...",
                key="search_query"
            )

        with col2:
            search_type = st.selectbox(
                "Search Type:",
                options=list(self.search_types.keys()),
                format_func=lambda x: x.replace('_', ' ').title()
            )

        # Advanced search options
        with st.expander("🔧 Advanced Options"):
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                search_scope = st.selectbox(
                    "Search Scope:",
                    options=list(self.search_scopes.keys()),
                    format_func=lambda x: x.replace('_', ' ').title()
                )

                limit = st.slider("Result Limit:", 5, 50, 10)

            with col_b:
                if search_type == "entity":
                    entity_type = st.selectbox(
                        "Entity Type:",
                        ["EMAIL", "DATE", "NUMBER", "ENTITY", "PERSON", "ORGANIZATION"]
                    )
                    entity_value = st.text_input("Specific Entity Value (optional):")

                elif search_type == "regex":
                    st.markdown("**Pattern Examples:**")
                    st.code(r"\b\d{3}-\d{3}-\d{4}\b  # Phone numbers")
                    st.code(r"\$\d+(?:,\d{3})*  # Dollar amounts")

            with col_c:
                sort_by = st.selectbox(
                    "Sort by:",
                    ["relevance", "date", "type", "length"]
                )

                include_metadata = st.checkbox("Include Metadata", value=True)

        # Search execution
        if st.button("🔍 Search", type="primary") and query:
            with st.spinner("Searching..."):
                # Execute search based on type
                if search_type == "semantic":
                    results = self.semantic_search(query, limit)
                elif search_type == "keyword":
                    results = self.keyword_search(query, limit)
                elif search_type == "fuzzy":
                    results = self.fuzzy_search(query, limit)
                elif search_type == "boolean":
                    results = self.boolean_search(query, limit)
                elif search_type == "regex":
                    results = self.regex_search(query, limit)
                elif search_type == "entity":
                    results = self.entity_search(entity_type, entity_value if 'entity_value' in locals() else None, limit)
                elif search_type == "conceptual":
                    results = self.conceptual_search(query, limit)
                else:
                    results = self.keyword_search(query, limit)

                # Store results in session state
                st.session_state.last_search_results = results
                st.session_state.last_search_query = query
                st.session_state.last_search_type = search_type

        # Display search results
        if hasattr(st.session_state, 'last_search_results'):
            self.render_search_results(
                st.session_state.last_search_results,
                st.session_state.last_search_query,
                st.session_state.last_search_type
            )

        # Quick search examples
        st.markdown("#### 💡 Quick Search Examples")

        examples = {
            "Semantic": ["machine learning applications", "data privacy concerns", "project management best practices"],
            "Boolean": ["python AND machine learning", "API OR SDK", "security NOT password"],
            "Regex": [r"\b\w+@\w+\.\w+\b", r"\d{4}-\d{2}-\d{2}", r"\$\d+(?:,\d{3})*"],
            "Entity": ["Find all EMAIL entities", "Search for DATE patterns", "Locate NUMBER mentions"]
        }

        col_ex1, col_ex2, col_ex3, col_ex4 = st.columns(4)

        with col_ex1:
            st.markdown("**Semantic:**")
            for example in examples["Semantic"]:
                if st.button(f"🔍 {example}", key=f"sem_{example}"):
                    st.session_state.search_query = example
                    st.rerun()

        with col_ex2:
            st.markdown("**Boolean:**")
            for example in examples["Boolean"]:
                if st.button(f"🔍 {example}", key=f"bool_{example}"):
                    st.session_state.search_query = example
                    st.rerun()

        with col_ex3:
            st.markdown("**Regex:**")
            for example in examples["Regex"]:
                if st.button(f"🔍 {example}", key=f"regex_{example}"):
                    st.session_state.search_query = example
                    st.rerun()

        with col_ex4:
            st.markdown("**Entity:**")
            for example in examples["Entity"]:
                if st.button(f"🔍 {example}", key=f"entity_{example}"):
                    st.session_state.search_query = example.split()[-2]
                    st.rerun()

    def render_search_results(self, results: List[Dict], query: str, search_type: str):
        """Render search results"""
        st.markdown("---")
        st.subheader(f"🎯 Search Results for '{query}' ({search_type})")

        if not results:
            st.info("No results found. Try different search terms or search type.")
            return

        # Results summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Results", len(results))

        with col2:
            avg_score = sum(r.get('relevance_score', 0) for r in results) / len(results)
            st.metric("Avg Relevance", f"{avg_score:.3f}")

        with col3:
            unique_types = len(set(r.get('type', 'unknown') for r in results))
            st.metric("Content Types", unique_types)

        # Results display options
        col_opt1, col_opt2 = st.columns(2)

        with col_opt1:
            view_mode = st.radio("View Mode:", ["List", "Cards", "Table"], horizontal=True)

        with col_opt2:
            show_details = st.checkbox("Show Details", value=True)

        # Render results based on view mode
        if view_mode == "List":
            self.render_results_list(results, show_details)
        elif view_mode == "Cards":
            self.render_results_cards(results, show_details)
        else:
            self.render_results_table(results)

        # Export options
        if st.button("📁 Export Results"):
            self.export_search_results(results, query, search_type)

    def render_results_list(self, results: List[Dict], show_details: bool):
        """Render results as a list"""
        for i, result in enumerate(results):
            with st.expander(
                f"#{i+1} - {result.get('type', 'Document').title()} "
                f"(Score: {result.get('relevance_score', 0):.3f})"
            ):
                # Content preview
                content = result.get('content', '')
                st.markdown(f"**Content Preview:**")
                st.write(content[:500] + "..." if len(content) > 500 else content)

                if show_details:
                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.markdown("**Metadata:**")
                        st.json(result.get('metadata', {}))

                        if result.get('entities'):
                            st.markdown("**Entities:**")
                            entity_df = pd.DataFrame(result['entities'])
                            st.dataframe(entity_df, use_container_width=True)

                    with col_b:
                        st.markdown("**Details:**")
                        st.write(f"- **Type:** {result.get('type', 'Unknown')}")
                        st.write(f"- **Added:** {result.get('added_at', 'Unknown')}")
                        st.write(f"- **Word Count:** {result.get('word_count', 0)}")
                        st.write(f"- **Match Type:** {result.get('match_type', 'Unknown')}")

                        if result.get('summary'):
                            st.markdown("**Summary:**")
                            st.write(result['summary'])

    def render_results_cards(self, results: List[Dict], show_details: bool):
        """Render results as cards"""
        cols_per_row = 2

        for i in range(0, len(results), cols_per_row):
            cols = st.columns(cols_per_row)

            for j, col in enumerate(cols):
                if i + j < len(results):
                    result = results[i + j]

                    with col:
                        with st.container():
                            st.markdown(f"**#{i+j+1} - {result.get('type', 'Document').title()}**")
                            st.progress(min(result.get('relevance_score', 0), 1.0))

                            content = result.get('content', '')
                            st.write(content[:200] + "..." if len(content) > 200 else content)

                            if show_details:
                                st.write(f"**Score:** {result.get('relevance_score', 0):.3f}")
                                st.write(f"**Words:** {result.get('word_count', 0)}")
                                st.write(f"**Type:** {result.get('match_type', 'Unknown')}")

                            if st.button(f"View Details", key=f"details_{i+j}"):
                                st.session_state[f"show_detail_{i+j}"] = not st.session_state.get(f"show_detail_{i+j}", False)

                            if st.session_state.get(f"show_detail_{i+j}", False):
                                st.json(result.get('metadata', {}))

    def render_results_table(self, results: List[Dict]):
        """Render results as a table"""
        df_data = []

        for i, result in enumerate(results):
            df_data.append({
                "Rank": i + 1,
                "Type": result.get('type', 'Unknown'),
                "Score": f"{result.get('relevance_score', 0):.3f}",
                "Words": result.get('word_count', 0),
                "Match": result.get('match_type', 'Unknown'),
                "Preview": result.get('content', '')[:100] + "...",
                "Added": result.get('added_at', '')[:10]
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

    def export_search_results(self, results: List[Dict], query: str, search_type: str):
        """Export search results"""
        export_data = {
            "search_query": query,
            "search_type": search_type,
            "timestamp": datetime.now().isoformat(),
            "total_results": len(results),
            "results": results
        }

        # JSON export
        json_data = json.dumps(export_data, indent=2, default=str)
        st.download_button(
            label="📄 Download JSON",
            data=json_data,
            file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

        # CSV export
        if results:
            df_export = pd.DataFrame([
                {
                    "Rank": i + 1,
                    "Type": r.get('type', ''),
                    "Relevance_Score": r.get('relevance_score', 0),
                    "Word_Count": r.get('word_count', 0),
                    "Match_Type": r.get('match_type', ''),
                    "Content": r.get('content', ''),
                    "Summary": r.get('summary', ''),
                    "Added_At": r.get('added_at', '')
                }
                for i, r in enumerate(results)
            ])

            csv_data = df_export.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        st.success("✅ Export options generated!")

    def render_knowledge_discovery(self):
        """Render knowledge discovery features"""
        st.subheader("🧠 Knowledge Discovery")

        documents = st.session_state.search_index["documents"]

        if not documents:
            st.info("Add documents to the search index to enable knowledge discovery.")
            return

        # Knowledge discovery tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Topic Clusters", "🕸️ Entity Graph", "📊 Content Analysis", "🔗 Relationships"])

        with tab1:
            self.render_topic_clusters(documents)

        with tab2:
            self.render_entity_graph(documents)

        with tab3:
            self.render_content_analysis(documents)

        with tab4:
            self.render_relationship_analysis(documents)

    def render_topic_clusters(self, documents: List[Dict]):
        """Render topic clustering analysis"""
        st.markdown("#### 🎯 Topic Clusters")

        if len(documents) < 3:
            st.info("Need at least 3 documents for topic clustering.")
            return

        # Extract text for clustering
        texts = [doc["content"] for doc in documents]

        # Vectorize
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        X = vectorizer.fit_transform(texts)

        # Cluster
        n_clusters = min(5, len(documents) // 2)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)

        # Visualize clusters
        if X.shape[1] > 2:
            pca = PCA(n_components=2)
            X_reduced = pca.fit_transform(X.toarray())

            cluster_df = pd.DataFrame({
                'x': X_reduced[:, 0],
                'y': X_reduced[:, 1],
                'cluster': clusters,
                'document': [f"Doc {i+1}" for i in range(len(documents))],
                'content': [doc["content"][:100] + "..." for doc in documents]
            })

            fig = px.scatter(
                cluster_df, x='x', y='y', color='cluster',
                hover_data=['document', 'content'],
                title="Document Topic Clusters"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Cluster summaries
        feature_names = vectorizer.get_feature_names_out()

        for cluster_id in range(n_clusters):
            cluster_docs = [i for i, c in enumerate(clusters) if c == cluster_id]
            st.markdown(f"**Cluster {cluster_id + 1}** ({len(cluster_docs)} documents)")

            # Top terms for this cluster
            cluster_center = kmeans.cluster_centers_[cluster_id]
            top_indices = cluster_center.argsort()[-10:][::-1]
            top_terms = [feature_names[i] for i in top_indices]

            st.write(f"Key terms: {', '.join(top_terms)}")

            with st.expander(f"Documents in Cluster {cluster_id + 1}"):
                for doc_idx in cluster_docs:
                    st.write(f"- Document {doc_idx + 1}: {documents[doc_idx]['content'][:100]}...")

    def render_entity_graph(self, documents: List[Dict]):
        """Render entity relationship graph"""
        st.markdown("#### 🕸️ Entity Relationship Graph")

        # Collect all entities
        all_entities = []
        entity_cooccurrence = defaultdict(int)

        for doc in documents:
            doc_entities = [e["text"] for e in doc.get("entities", [])]
            all_entities.extend(doc_entities)

            # Count co-occurrences
            for i, entity1 in enumerate(doc_entities):
                for entity2 in doc_entities[i+1:]:
                    pair = tuple(sorted([entity1, entity2]))
                    entity_cooccurrence[pair] += 1

        if not all_entities:
            st.info("No entities found in documents.")
            return

        # Entity frequency
        entity_counts = Counter(all_entities)
        top_entities = entity_counts.most_common(20)

        # Display entity frequency
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top Entities:**")
            entity_df = pd.DataFrame(top_entities, columns=["Entity", "Frequency"])
            fig_entities = px.bar(entity_df, x="Frequency", y="Entity",
                                orientation='h', title="Entity Frequency")
            st.plotly_chart(fig_entities, use_container_width=True)

        with col2:
            st.markdown("**Entity Co-occurrence:**")
            if entity_cooccurrence:
                top_pairs = sorted(entity_cooccurrence.items(), key=lambda x: x[1], reverse=True)[:10]
                pair_df = pd.DataFrame([
                    {"Pair": f"{pair[0]} ↔ {pair[1]}", "Co-occurrence": count}
                    for (pair, count) in top_pairs
                ])
                st.dataframe(pair_df, use_container_width=True)

    def render_content_analysis(self, documents: List[Dict]):
        """Render content analysis"""
        st.markdown("#### 📊 Content Analysis")

        # Content statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            total_words = sum(doc.get("word_count", 0) for doc in documents)
            st.metric("Total Words", f"{total_words:,}")

        with col2:
            avg_length = total_words / len(documents) if documents else 0
            st.metric("Avg Length", f"{avg_length:.0f} words")

        with col3:
            total_entities = sum(len(doc.get("entities", [])) for doc in documents)
            st.metric("Total Entities", total_entities)

        # Content type distribution
        type_counts = Counter(doc.get("type", "unknown") for doc in documents)

        col_a, col_b = st.columns(2)

        with col_a:
            if type_counts:
                fig_types = px.pie(
                    values=list(type_counts.values()),
                    names=list(type_counts.keys()),
                    title="Content Type Distribution"
                )
                st.plotly_chart(fig_types, use_container_width=True)

        with col_b:
            # Word count distribution
            word_counts = [doc.get("word_count", 0) for doc in documents]
            fig_lengths = px.histogram(
                x=word_counts,
                nbins=20,
                title="Document Length Distribution"
            )
            st.plotly_chart(fig_lengths, use_container_width=True)

    def render_relationship_analysis(self, documents: List[Dict]):
        """Render relationship analysis"""
        st.markdown("#### 🔗 Relationship Analysis")

        # Document similarity matrix
        if len(documents) > 1:
            texts = [doc["content"] for doc in documents]
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(texts)

            similarity_matrix = cosine_similarity(tfidf_matrix)

            # Create similarity heatmap
            fig_sim = px.imshow(
                similarity_matrix,
                labels=dict(x="Document", y="Document", color="Similarity"),
                title="Document Similarity Matrix",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_sim, use_container_width=True)

            # Most similar document pairs
            st.markdown("**Most Similar Document Pairs:**")
            similarities = []
            for i in range(len(documents)):
                for j in range(i+1, len(documents)):
                    similarities.append({
                        "Doc1": f"Document {i+1}",
                        "Doc2": f"Document {j+1}",
                        "Similarity": similarity_matrix[i][j]
                    })

            similarities.sort(key=lambda x: x["Similarity"], reverse=True)
            sim_df = pd.DataFrame(similarities[:10])
            st.dataframe(sim_df, use_container_width=True)

def main():
    """Main function to render advanced search"""
    st.set_page_config(
        page_title="DocuMind Advanced Search",
        page_icon="🔍",
        layout="wide"
    )

    search_engine = AdvancedSearchEngine()

    # Sidebar
    with st.sidebar:
        st.header("🔍 Search & Discovery")

        st.markdown("""
        **🎯 Search Types:**
        - Semantic AI search
        - Keyword matching
        - Fuzzy search
        - Boolean operators
        - Regular expressions
        - Entity search
        - Conceptual search

        **📊 Knowledge Discovery:**
        - Topic clustering
        - Entity relationships
        - Content analysis
        - Document similarity
        """)

        st.markdown("---")
        st.subheader("📁 Index Management")

        # Add sample data
        if st.button("📝 Add Sample Data"):
            sample_docs = [
                {
                    "content": "Machine learning is transforming healthcare by enabling predictive analytics, personalized medicine, and automated diagnostics. AI algorithms can analyze medical images, predict patient outcomes, and assist in drug discovery.",
                    "type": "article",
                    "metadata": {"category": "healthcare", "author": "AI Research"}
                },
                {
                    "content": "Python is a versatile programming language widely used in data science, web development, and automation. Its simple syntax and extensive libraries make it ideal for beginners and experts alike.",
                    "type": "documentation",
                    "metadata": {"category": "programming", "language": "python"}
                },
                {
                    "content": "Project management requires effective communication, clear goals, and proper resource allocation. Agile methodologies have become popular for their flexibility and iterative approach to development.",
                    "type": "guide",
                    "metadata": {"category": "management", "methodology": "agile"}
                }
            ]

            for doc in sample_docs:
                search_engine.add_to_search_index(doc["content"], doc["type"], doc["metadata"])

            st.success("✅ Sample data added to search index!")

        # Upload custom document
        uploaded_file = st.file_uploader("📄 Upload Document", type=['txt', 'md'])
        if uploaded_file:
            content = str(uploaded_file.read(), "utf-8")
            doc_id = search_engine.add_to_search_index(
                content,
                "uploaded",
                {"filename": uploaded_file.name, "size": len(content)}
            )
            st.success(f"✅ Document added (ID: {doc_id})")

        # Index stats
        if st.session_state.search_index["documents"]:
            st.markdown("#### 📊 Index Stats")
            docs_count = len(st.session_state.search_index["documents"])
            st.metric("Documents", docs_count)

            total_words = sum(doc.get("word_count", 0) for doc in st.session_state.search_index["documents"])
            st.metric("Total Words", f"{total_words:,}")

    # Main interface
    tab1, tab2 = st.tabs(["🔍 Search", "🧠 Knowledge Discovery"])

    with tab1:
        search_engine.render_search_interface()

    with tab2:
        search_engine.render_knowledge_discovery()

if __name__ == "__main__":
    main()
