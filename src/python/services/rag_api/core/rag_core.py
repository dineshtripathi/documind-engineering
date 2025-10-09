# rag_core.py
from __future__ import annotations
import os, re, uuid, textwrap, time
from dataclasses import dataclass
from typing import List, Tuple, Dict

import torch
import requests
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# ------------ Config ------------
@dataclass(frozen=True)
class RagConfig:
    # Qdrant: Production server with persistence
    qdrant_mode: str = os.getenv("QDRANT_MODE", "server")  # "memory" | "server"
    qdrant_url: str = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
    qdrant_retries: int = int(os.getenv("QDRANT_RETRIES", "10"))
    qdrant_retry_delay: float = float(os.getenv("QDRANT_RETRY_DELAY", "1.0"))
    collection: str = os.getenv("QDRANT_COLLECTION", "tech_knowledge_base")

    # Models
    embed_model: str = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
    rerank_model: str = os.getenv("RERANK_MODEL", "jinaai/jina-reranker-v1-turbo-en")
    rerank_device_env: str | None = os.getenv("RERANK_DEVICE")  # "cpu" / "cuda" / None -> auto

    # Retrieval/Prompting
    topk: int = int(os.getenv("TOPK", "12"))
    context_k: int = int(os.getenv("CONTEXT_K", "4"))

    # Local LLM (ollama)
    ollama_url: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "phi3.5:3.8b-mini-instruct-q4_0")

    # Specialized models for different tasks
    code_generation_model: str = os.getenv("CODE_MODEL", "codellama:13b")
    code_explanation_model: str = os.getenv("CODE_EXPLAIN_MODEL", "codellama:13b")
    general_chat_model: str = os.getenv("CHAT_MODEL", "llama3.1:8b")
    technical_model: str = os.getenv("TECH_MODEL", "llama3.1:70b")

    # Domain-specific configuration
    enable_domain_detection: bool = bool(os.getenv("ENABLE_DOMAIN_DETECTION", "true"))
    min_confidence_threshold: float = float(os.getenv("MIN_CONFIDENCE", "0.7"))
    domain_models: Dict[str, str] | None = None  # Populated dynamically
# ------------ Core ------------
class RagCore:
    def __init__(self, cfg: RagConfig | None = None) -> None:
        self.cfg = cfg or RagConfig()

        auto_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = self.cfg.rerank_device_env or auto_device
        print(f"[RAG] device -> {self.device}")

        # --- Embeddings model ---
        # Note: some backends don't accept model_kwargs like attn_implementation; keep defaults for portability
        self.emb = SentenceTransformer(self.cfg.embed_model, device=self.device)

        # --- Reranker (proper CrossEncoder load) ---
        # Some sentence-transformers versions support trust_remote_code; guard it to avoid crash on older installs
        try:
            self.reranker = CrossEncoder(
                self.cfg.rerank_model,
                device=self.device,
                trust_remote_code=True  # correct for Jina rerankers
            )
        except TypeError:
            # Fallback if installed version doesn't accept trust_remote_code
            self.reranker = CrossEncoder(self.cfg.rerank_model, device=self.device)

        # --- Qdrant client ---
        if self.cfg.qdrant_mode.lower() == "memory":
            print("[RAG] Qdrant mode: :memory:")
            self.qc = QdrantClient(location=":memory:")
        else:
            print(f"[RAG] Qdrant mode: server @ {self.cfg.qdrant_url}")
            self.qc = QdrantClient(url=self.cfg.qdrant_url, timeout=5.0)

        # Ensure collection (with retry so app doesn’t crash if server isn’t ready yet)
        self._ensure_collection_with_retry(self.emb.get_sentence_embedding_dimension())

        # Optional tiny seed corpus (kept for parity with your old code)
        self._seed_once()

        # Domain detection setup
        self.domain_keywords = {
            "finance": ["loan", "mortgage", "investment", "portfolio", "risk", "compliance", "financial", "banking", "credit", "debt", "fico", "basel", "securities", "fund", "trading"],
            "legal": ["contract", "agreement", "liability", "clause", "jurisdiction", "lawsuit", "legal", "court", "attorney", "law", "litigation", "statute", "regulation", "breach", "defendant"],
            "medical": ["patient", "diagnosis", "treatment", "medication", "symptoms", "medical", "health", "doctor", "hospital", "clinical", "therapy", "prescription", "vital", "cardiac", "ecg", "oxygen"],
            "technical": [
                # .NET & Programming
                "API", "configuration", "deployment", "architecture", "protocol", "system", "software", "code", "programming", "technical",
                "server", "database", "network", "framework", "algorithm", ".net", "dotnet", "csharp", "async", "await", "task",
                "dependency", "injection", "minimal", "controllers", "middleware", "hosting", "services", "entity",
                # Azure & Cloud
                "azure", "functions", "durable", "orchestrator", "activity", "checkpointing", "retry", "workflow", "cosmos",
                "storage", "servicebus", "eventhub", "cognitive", "kubernetes", "docker", "container", "microservices",
                # DevOps & IaC
                "terraform", "yaml", "pipeline", "ci/cd", "devops", "infrastructure", "provisioning", "automation",
                "bicep", "arm", "cloudformation", "ansible", "helm", "kubectl", "deployment", "scaling",
                # Modern Tech
                "microservice", "distributed", "event-driven", "saga", "cqrs", "event-sourcing", "domain-driven",
                "observability", "monitoring", "logging", "tracing", "metrics", "telemetry", "security", "authentication"
            ],
            "education": ["student", "course", "curriculum", "academic", "education", "learning", "teaching", "university", "school", "grade", "assessment", "instruction", "pedagogy", "enrollment", "degree"],
            "general": []  # Fallback
        }

        # Initialize model availability cache
        self._available_models = None
        self._check_model_availability()

    # ---------- Public API ----------
    def health(self) -> Dict:
        return {
            "ok": True,
            "device": self.device,
            "qdrant_mode": self.cfg.qdrant_mode,
            "qdrant": self.cfg.qdrant_url,
            "collection": self.cfg.collection,
            "embed_model": self.cfg.embed_model,
            "rerank_model": self.cfg.rerank_model,
            "default_ollama_model": self.cfg.ollama_model,
            "specialized_models": {
                "code_generation": self.cfg.code_generation_model,
                "code_explanation": self.cfg.code_explanation_model,
                "general_chat": self.cfg.general_chat_model,
                "technical": self.cfg.technical_model
            },
            "available_models": self._available_models or [],
            "domain_detection": self.cfg.enable_domain_detection,
            "supported_domains": list(self.domain_keywords.keys()),
        }

    def ingest_text(self, doc_id: str, text: str) -> int:
        """Chunk -> embed -> upsert."""
        dim = self.emb.get_sentence_embedding_dimension()
        self._ensure_collection(dim)
        chunks = self.chunk_text(text, max_tokens=220, overlap_tokens=40)
        self._upsert_passages(doc_id, chunks)
        return len(chunks)

    def ingest_plain_chunks(self, doc_id: str, passages: List[str]) -> int:
        dim = self.emb.get_sentence_embedding_dimension()
        self._ensure_collection(dim)
        self._upsert_passages(doc_id, passages)
        return len(passages)

    def search(self, query: str, k: int | None = None) -> List[Dict]:
        """Embed query -> ANN -> return list of dicts {id, text, doc_id, score}"""
        k = k or self.cfg.topk
        qv = self.emb.encode([query], normalize_embeddings=True)[0].tolist()
        try:
            # Newer client
            res = self.qc.query_points(
                collection_name=self.cfg.collection,
                query=qv, limit=k, with_payload=True, with_vectors=False
            )
            pts = getattr(res, "points", res)
            return [
                {"id": str(p.id), "text": p.payload["text"], "doc_id": p.payload["doc_id"], "score": float(p.score)}
                for p in pts
            ]
        except Exception:
            # Older client fallback
            res = self.qc.search(
                collection_name=self.cfg.collection,
                query_vector=qv, limit=k, with_payload=True, with_vectors=False
            )
            return [
                {"id": str(r.id), "text": r.payload["text"], "doc_id": r.payload["doc_id"], "score": float(r.score)}
                for r in res
            ]

    def rerank(self, query: str, passages: List[Dict]) -> Tuple[List[Dict], List[float]]:
        if not passages:
            return [], []
        pairs = [(query, p["text"]) for p in passages]
        scores = self.reranker.predict(pairs)
        # ensure list of floats
        try:
            scores = scores.tolist()
        except Exception:
            scores = [float(s) for s in scores]
        order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
        ranked = [passages[i] for i in order]
        ranked_scores = [float(scores[i]) for i in order]
        return ranked, ranked_scores

    def build_prompt(self, query: str, ranked: List[Dict], k: int | None = None) -> Tuple[str, List[Dict]]:
        k = k or self.cfg.context_k
        numbered = []
        cmap = []
        for i, p in enumerate(ranked[:k], start=1):
            numbered.append(f"[{i}] {p['text'].strip()} (file: {p['doc_id']}, chunk #{p['id']})")
            cmap.append({"index": i, "doc_id": p["doc_id"], "chunk_id": p["id"], "score": float(p.get("score", 0.0))})
        ctx = "\n\n".join(numbered)
        sys = (
            "Answer ONLY using [CONTEXT]. If not present, reply exactly: not found.\n"
            "Every sentence MUST end with [n] citations from [CONTEXT]. Do not invent sources. Be concise."
        )
        prompt = textwrap.dedent(f"""
        [SYSTEM]
        {sys}

        [CONTEXT]
        {ctx}

        [QUESTION]
        {query}

        [INSTRUCTIONS]
        - Each sentence ends with citation(s) like [1] or [1][2]
        - If unsupported, reply: not found
        """)
        return prompt, cmap

    def ask_local(self, query: str) -> Dict:
        """Retrieve→Rerank→Prompt→Local LLM. Enforce citations; else abstain."""
        hits = self.search(query, k=self.cfg.topk)
        ranked, scores = self.rerank(query, hits)
        prompt, cmap = self.build_prompt(query, ranked, k=self.cfg.context_k)

        ans = self._ollama_generate(prompt, temperature=0.1).strip()
        if ans and ans.lower() != "not found" and self._has_valid_citations(ans, self.cfg.context_k):
            return {"route": "local", "answer": ans, "contextMap": cmap}
        return {"route": "abstain", "answer": "not found", "contextMap": cmap}

    # ---------- Domain Detection ----------
    def detect_domain(self, text: str) -> Tuple[str, float]:
        """Detect document domain based on keyword analysis and confidence scoring."""
        text_lower = text.lower()
        word_count = len(text.split())

        domain_scores = {}
        for domain, keywords in self.domain_keywords.items():
            if domain == "general":
                continue

            # Count keyword matches
            keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)

            # Calculate normalized score with improved algorithm
            if keywords and keyword_matches > 0:
                # Use absolute match count with normalization for large keyword sets
                base_score = min(1.0, keyword_matches / max(10, len(keywords) * 0.3))  # More forgiving for large sets
                # Apply density boost for shorter texts
                density_boost = min(2.0, keyword_matches / max(1, word_count / 100))
                domain_scores[domain] = base_score * (1 + density_boost * 0.2)  # Increased boost
            else:
                domain_scores[domain] = 0.0

        # Find best domain
        if domain_scores:
            best_domain = max(domain_scores.items(), key=lambda x: x[1])
            domain, confidence = best_domain

            # Lower confidence threshold for better detection
            if confidence >= max(0.1, self.cfg.min_confidence_threshold * 0.3):  # Much more lenient
                return domain, confidence

        # Fallback to general
        return "general", 1.0

    def select_model_for_task(self, task_type: str, domain: str = "general", query: str = "") -> str:
        """Select the best model for a specific task and domain."""
        # Code-related tasks
        if task_type == "code_generation":
            return self._get_available_model(self.cfg.code_generation_model)
        elif task_type == "code_explanation":
            return self._get_available_model(self.cfg.code_explanation_model)
        elif task_type == "technical" or domain == "technical":
            return self._get_available_model(self.cfg.technical_model)

        # Check if query contains code-related keywords
        code_keywords = ["code", "programming", "function", "class", "method", "api", "algorithm", "debug"]
        if any(keyword in query.lower() for keyword in code_keywords):
            return self._get_available_model(self.cfg.technical_model)

        # Default to general chat model
        return self._get_available_model(self.cfg.general_chat_model)

    def ask_local_with_model_selection(self, query: str, task_type: str = "general") -> Dict:
        """Enhanced ask_local with automatic model selection."""
        # Detect domain for better model selection
        domain, confidence = self.detect_domain(query)

        # Select appropriate model
        selected_model = self.select_model_for_task(task_type, domain, query)

        # Retrieve and rank context
        hits = self.search(query, k=self.cfg.topk)
        ranked, scores = self.rerank(query, hits)
        prompt, cmap = self.build_prompt(query, ranked, k=self.cfg.context_k)

        # Generate with selected model
        ans = self._ollama_generate_with_model(prompt, selected_model, temperature=0.1).strip()

        if ans and ans.lower() != "not found" and self._has_valid_citations(ans, self.cfg.context_k):
            return {
                "route": "local",
                "answer": ans,
                "contextMap": cmap,
                "model_used": selected_model,
                "detected_domain": domain,
                "domain_confidence": confidence,
                "task_type": task_type
            }
        return {
            "route": "abstain",
            "answer": "not found",
            "contextMap": cmap,
            "model_used": selected_model,
            "detected_domain": domain,
            "domain_confidence": confidence,
            "task_type": task_type
        }

    # ---------- Helpers ----------
    def chunk_text(self, text: str, max_tokens: int = 220, overlap_tokens: int = 40) -> List[str]:
        """Naive word-window chunking with overlap."""
        words = text.split()
        if not words:
            return []
        chunks = []
        i, n = 0, len(words)
        while i < n:
            j = min(i + max_tokens, n)
            chunks.append(" ".join(words[i:j]))
            if j == n:
                break
            i = max(0, j - overlap_tokens)
        return chunks

    def _upsert_passages(self, doc_id: str, passages: List[str]) -> None:
        vecs = self.emb.encode(passages, normalize_embeddings=True)
        points = []
        for i, (txt, vec) in enumerate(zip(passages, vecs), start=1):
            # stable 32-bit int id (works with Qdrant int IDs)
            pid = int(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}-{i}").int % 2**31)
            points.append(
                PointStruct(
                    id=pid,
                    vector=vec.tolist(),
                    payload={"text": txt, "doc_id": doc_id, "chunk": i},
                )
            )
        self.qc.upsert(self.cfg.collection, points=points)

    def _ensure_collection_with_retry(self, dim: int) -> None:
        last_err = None
        for _ in range(self.cfg.qdrant_retries):
            try:
                self._ensure_collection(dim)
                return
            except Exception as e:
                last_err = e
                time.sleep(self.cfg.qdrant_retry_delay)
        # final attempt (raise if still failing)
        self._ensure_collection(dim)

    def _ensure_collection(self, dim: int) -> None:
        # guard get_collections for first boot
        try:
            names = [c.name for c in self.qc.get_collections().collections]
        except Exception:
            names = []
        if self.cfg.collection not in names:
            # create (or recreate) with cosine distance
            try:
                self.qc.create_collection(
                    self.cfg.collection,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
            except Exception:
                # if exists partially or schema mismatch, recreate
                self.qc.recreate_collection(
                    collection_name=self.cfg.collection,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )

    def _ollama_generate(self, prompt: str, temperature: float = 0.2) -> str:
        # try /api/generate
        try:
            r = requests.post(
                f"{self.cfg.ollama_url}/api/generate",
                json={"model": self.cfg.ollama_model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}},
                timeout=180
            )
            if r.status_code == 200:
                return r.json().get("response", "") or ""
        except Exception:
            pass
        # fallback to /api/chat
        try:
            c = requests.post(
                f"{self.cfg.ollama_url}/api/chat",
                json={"model": self.cfg.ollama_model, "stream": False, "messages": [{"role": "user", "content": prompt}], "options": {"temperature": temperature}},
                timeout=180
            )
            c.raise_for_status()
            j = c.json()
            return j.get("message", {}).get("content", "") or ""
        except Exception:
            return ""

    def _has_valid_citations(self, answer: str, k: int) -> bool:
        matches = re.findall(r"\[(\d+)\]", answer)
        if not matches:
            return False
        for m in matches:
            try:
                n = int(m)
                if n < 1 or n > k:
                    return False
            except Exception:
                return False
        return True

    def _check_model_availability(self) -> None:
        """Check which Ollama models are available."""
        try:
            response = requests.get(f"{self.cfg.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self._available_models = [model["name"] for model in data.get("models", [])]
            else:
                self._available_models = []
        except Exception:
            self._available_models = []

    def _get_available_model(self, preferred_model: str) -> str:
        """Get available model, fallback to default if preferred not available."""
        if self._available_models is None:
            self._check_model_availability()

        available_models = self._available_models or []

        if preferred_model in available_models:
            return preferred_model

        # Fallback hierarchy
        fallbacks = [
            self.cfg.ollama_model,  # Default model
            "llama3.1:70b",         # Most powerful general model
            "llama3.1:8b",          # Good general model
            "mixtral:8x7b-instruct-v0.1-q4_0",  # Excellent instruction following
            "codellama:13b",        # Code specialization
            "phi3.5:3.8b-mini-instruct-q4_0"    # Fallback
        ]

        for fallback in fallbacks:
            if fallback in available_models:
                return fallback

        # Last resort - return the preferred model (Ollama will handle the error)
        return preferred_model

    def _ollama_generate_with_model(self, prompt: str, model: str, temperature: float = 0.2) -> str:
        """Generate with a specific model."""
        # try /api/generate
        try:
            r = requests.post(
                f"{self.cfg.ollama_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}},
                timeout=180
            )
            if r.status_code == 200:
                return r.json().get("response", "") or ""
        except Exception:
            pass
        # fallback to /api/chat
        try:
            c = requests.post(
                f"{self.cfg.ollama_url}/api/chat",
                json={"model": model, "stream": False, "messages": [{"role": "user", "content": prompt}], "options": {"temperature": temperature}},
                timeout=180
            )
            c.raise_for_status()
            j = c.json()
            return j.get("message", {}).get("content", "") or ""
        except Exception:
            return ""

    def _seed_once(self) -> None:
        # Idempotent tiny seed corpus from your original file (kept here for parity)
        DOCS = {
            "dr_runbook.md": """
            # Disaster Recovery Runbook
            The DR process includes three phases: Preparation, Failover, and Validation.
            Preparation: ensure backups are tested, RPO is under 15 minutes, and RTO under 1 hour.
            Failover: promote the replica in the disaster region and switch DNS traffic.
            Validation: run automated health checks and data consistency checks.
            """,
            "backup_policy.md": """
            # Backup Policy
            Daily incremental backups at 01:00 UTC, weekly full backups on Sunday 02:00 UTC.
            Retention: incrementals for 30 days, full backups for 12 months.
            Encryption: AES-256 at rest and TLS 1.2 in transit.
            """,
            "biryani.txt": """
            Add basmati rice, marinate chicken with yogurt and spices, cook on low heat.
            This is a cooking recipe unrelated to disaster recovery or backup policies.
            """,
        }
        try:
            exist = self.qc.scroll(self.cfg.collection, limit=1)[0]
            if exist:
                return
        except Exception:
            pass
        for name, txt in DOCS.items():
            chunks = self.chunk_text(txt, max_tokens=220, overlap_tokens=40)
            self._upsert_passages(name, chunks)


# Export singleton
core = RagCore()



# # rag_core.py
# from __future__ import annotations
# import os, re, uuid, textwrap
# from dataclasses import dataclass
# from typing import List, Tuple, Dict

# import torch
# import requests
# from sentence_transformers import SentenceTransformer, CrossEncoder
# from qdrant_client import QdrantClient
# from qdrant_client.http.models import Distance, VectorParams, PointStruct

# # ------------ Config ------------
# @dataclass(frozen=True)
# class RagConfig:
#     qdrant_url: str = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
#     collection: str = os.getenv("QDRANT_COLLECTION", "smoketest_docs")
#     embed_model: str = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
#     rerank_model: str = os.getenv("RERANK_MODEL", "jinaai/jina-reranker-v1-turbo-en")
#     topk: int = int(os.getenv("TOPK", "12"))
#     context_k: int = int(os.getenv("CONTEXT_K", "4"))
#     ollama_url: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
#     ollama_model: str = os.getenv("OLLAMA_MODEL", "phi3.5:3.8b-mini-instruct-q4_0")
#     rerank_device_env: str | None = os.getenv("RERANK_DEVICE")  # "cpu" / "cuda" / None -> auto


# # ------------ Core ------------
# class RagCore:
#     def __init__(self, cfg: RagConfig | None = None) -> None:
#         self.cfg = cfg or RagConfig()

#         auto_device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.device = self.cfg.rerank_device_env or auto_device
#         print(f"[RAG] device -> {self.device}")

#         # Models
#         # self.emb = SentenceTransformer(self.cfg.embed_model, device=self.device)
#         # self.reranker = CrossEncoder(self.cfg.rerank_model, device=self.device)

#         self.emb = SentenceTransformer(self.cfg.embed_model,device=self.device,model_kwargs={"attn_implementation": "eager"})
#         self.reranker = CrossEncoder(self.cfg.rerank_model,device=self.device,model_kwargs={"attn_implementation": "eager"})
#         # Vector store
#         self.qc = QdrantClient(url=self.cfg.qdrant_url)
#         self._ensure_collection(self.emb.get_sentence_embedding_dimension())

#         # Optional tiny seed corpus (kept for parity with your old code)
#         self._seed_once()

#     # ---------- Public API ----------
#     def health(self) -> Dict:
#         return {
#             "ok": True,
#             "qdrant": self.cfg.qdrant_url,
#             "collection": self.cfg.collection,
#             "model": self.cfg.ollama_model,
#         }

#     def ingest_text(self, doc_id: str, text: str) -> int:
#         """Chunk -> embed -> upsert."""
#         dim = self.emb.get_sentence_embedding_dimension()
#         self._ensure_collection(dim)
#         chunks = self.chunk_text(text, max_tokens=220, overlap_tokens=40)
#         self._upsert_passages(doc_id, chunks)
#         return len(chunks)

#     def ingest_plain_chunks(self, doc_id: str, passages: List[str]) -> int:
#         dim = self.emb.get_sentence_embedding_dimension()
#         self._ensure_collection(dim)
#         self._upsert_passages(doc_id, passages)
#         return len(passages)

#     def search(self, query: str, k: int | None = None) -> List[Dict]:
#         """Embed query -> ANN -> return list of dicts {id, text, doc_id, score}"""
#         k = k or self.cfg.topk
#         qv = self.emb.encode([query], normalize_embeddings=True)[0].tolist()
#         try:
#             res = self.qc.query_points(
#                 collection_name=self.cfg.collection,
#                 query=qv, limit=k, with_payload=True, with_vectors=False
#             )
#             pts = getattr(res, "points", res)
#             return [
#                 {"id": str(p.id), "text": p.payload["text"], "doc_id": p.payload["doc_id"], "score": float(p.score)}
#                 for p in pts
#             ]
#         except Exception:
#             res = self.qc.search(
#                 collection_name=self.cfg.collection,
#                 query_vector=qv, limit=k, with_payload=True, with_vectors=False
#             )
#             return [
#                 {"id": str(r.id), "text": r.payload["text"], "doc_id": r.payload["doc_id"], "score": float(r.score)}
#                 for r in res
#             ]

#     def rerank(self, query: str, passages: List[Dict]) -> Tuple[List[Dict], List[float]]:
#         if not passages:
#             return [], []
#         pairs = [(query, p["text"]) for p in passages]
#         scores = self.reranker.predict(pairs).tolist()
#         order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
#         ranked = [passages[i] for i in order]
#         ranked_scores = [scores[i] for i in order]
#         return ranked, ranked_scores

#     def build_prompt(self, query: str, ranked: List[Dict], k: int | None = None) -> Tuple[str, List[Dict]]:
#         k = k or self.cfg.context_k
#         numbered = []
#         cmap = []
#         for i, p in enumerate(ranked[:k], start=1):
#             numbered.append(f"[{i}] {p['text'].strip()} (file: {p['doc_id']}, chunk #{p['id']})")
#             cmap.append({"index": i, "doc_id": p["doc_id"], "chunk_id": p["id"], "score": float(p.get("score", 0.0))})
#         ctx = "\n\n".join(numbered)
#         sys = (
#             "Answer ONLY using [CONTEXT]. If not present, reply exactly: not found.\n"
#             "Every sentence MUST end with [n] citations from [CONTEXT]. Do not invent sources. Be concise."
#         )
#         prompt = textwrap.dedent(f"""
#         [SYSTEM]
#         {sys}

#         [CONTEXT]
#         {ctx}

#         [QUESTION]
#         {query}

#         [INSTRUCTIONS]
#         - Each sentence ends with citation(s) like [1] or [1][2]
#         - If unsupported, reply: not found
#         """)
#         return prompt, cmap

#     def ask_local(self, query: str) -> Dict:
#         """Retrieve→Rerank→Prompt→Local LLM. Enforce citations; else abstain."""
#         hits = self.search(query, k=self.cfg.topk)
#         ranked, scores = self.rerank(query, hits)
#         prompt, cmap = self.build_prompt(query, ranked, k=self.cfg.context_k)

#         ans = self._ollama_generate(prompt, temperature=0.1).strip()
#         if ans and ans.lower() != "not found" and self._has_valid_citations(ans, self.cfg.context_k):
#             return {"route": "local", "answer": ans, "contextMap": cmap}
#         return {"route": "abstain", "answer": "not found", "contextMap": cmap}

#     # ---------- Helpers ----------
#     def chunk_text(self, text: str, max_tokens: int = 220, overlap_tokens: int = 40) -> List[str]:
#         """Naive word-window chunking with overlap."""
#         words = text.split()
#         if not words:
#             return []
#         chunks = []
#         i, n = 0, len(words)
#         while i < n:
#             j = min(i + max_tokens, n)
#             chunks.append(" ".join(words[i:j]))
#             if j == n:
#                 break
#             i = max(0, j - overlap_tokens)
#         return chunks

#     def _upsert_passages(self, doc_id: str, passages: List[str]) -> None:
#         vecs = self.emb.encode(passages, normalize_embeddings=True)
#         points = []
#         for i, (txt, vec) in enumerate(zip(passages, vecs), start=1):
#             # stable 32-bit int id
#             pid = int(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}-{i}").int % 2**31)
#             points.append(
#                 PointStruct(
#                     id=pid,
#                     vector=vec.tolist(),
#                     payload={"text": txt, "doc_id": doc_id, "chunk": i},
#                 )
#             )
#         self.qc.upsert(self.cfg.collection, points=points)

#     def _ensure_collection(self, dim: int) -> None:
#         names = [c.name for c in self.qc.get_collections().collections]
#         if self.cfg.collection not in names:
#             self.qc.create_collection(
#                 self.cfg.collection,
#                 vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
#             )

#     def _ollama_generate(self, prompt: str, temperature: float = 0.2) -> str:
#         # try /api/generate
#         try:
#             r = requests.post(
#                 f"{self.cfg.ollama_url}/api/generate",
#                 json={"model": self.cfg.ollama_model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}},
#                 timeout=180
#             )
#             if r.status_code == 200:
#                 return r.json().get("response", "") or ""
#         except Exception:
#             pass
#         # fallback to /api/chat
#         try:
#             c = requests.post(
#                 f"{self.cfg.ollama_url}/api/chat",
#                 json={"model": self.cfg.ollama_model, "stream": False, "messages": [{"role": "user", "content": prompt}], "options": {"temperature": temperature}},
#                 timeout=180
#             )
#             c.raise_for_status()
#             j = c.json()
#             return j.get("message", {}).get("content", "") or ""
#         except Exception:
#             return ""

#     def _has_valid_citations(self, answer: str, k: int) -> bool:
#         matches = re.findall(r"\[(\d+)\]", answer)
#         if not matches:
#             return False
#         for m in matches:
#             try:
#                 n = int(m)
#                 if n < 1 or n > k:
#                     return False
#             except Exception:
#                 return False
#         return True

#     def _seed_once(self) -> None:
#         # Idempotent tiny seed corpus from your original file (kept here for parity)
#         DOCS = {
#             "dr_runbook.md": """
#             # Disaster Recovery Runbook
#             The DR process includes three phases: Preparation, Failover, and Validation.
#             Preparation: ensure backups are tested, RPO is under 15 minutes, and RTO under 1 hour.
#             Failover: promote the replica in the disaster region and switch DNS traffic.
#             Validation: run automated health checks and data consistency checks.
#             """,
#             "backup_policy.md": """
#             # Backup Policy
#             Daily incremental backups at 01:00 UTC, weekly full backups on Sunday 02:00 UTC.
#             Retention: incrementals for 30 days, full backups for 12 months.
#             Encryption: AES-256 at rest and TLS 1.2 in transit.
#             """,
#             "biryani.txt": """
#             Add basmati rice, marinate chicken with yogurt and spices, cook on low heat.
#             This is a cooking recipe unrelated to disaster recovery or backup policies.
#             """,
#         }
#         try:
#             exist = self.qc.scroll(self.cfg.collection, limit=1)[0]
#             if exist:
#                 return
#         except Exception:
#             pass
#         for name, txt in DOCS.items():
#             chunks = self.chunk_text(txt, max_tokens=220, overlap_tokens=40)
#             self._upsert_passages(name, chunks)


# # Export singleton
# core = RagCore()
