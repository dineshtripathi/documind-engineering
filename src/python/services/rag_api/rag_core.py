# rag_core.py
from __future__ import annotations
import os, re, uuid, textwrap
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
    qdrant_url: str = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
    collection: str = os.getenv("QDRANT_COLLECTION", "smoketest_docs")
    embed_model: str = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
    rerank_model: str = os.getenv("RERANK_MODEL", "jinaai/jina-reranker-v1-turbo-en")
    topk: int = int(os.getenv("TOPK", "12"))
    context_k: int = int(os.getenv("CONTEXT_K", "4"))
    ollama_url: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "phi3.5:3.8b-mini-instruct-q4_0")
    rerank_device_env: str | None = os.getenv("RERANK_DEVICE")  # "cpu" / "cuda" / None -> auto


# ------------ Core ------------
class RagCore:
    def __init__(self, cfg: RagConfig | None = None) -> None:
        self.cfg = cfg or RagConfig()

        auto_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = self.cfg.rerank_device_env or auto_device
        print(f"[RAG] device -> {self.device}")

        # Models
        # self.emb = SentenceTransformer(self.cfg.embed_model, device=self.device)
        # self.reranker = CrossEncoder(self.cfg.rerank_model, device=self.device)

        self.emb = SentenceTransformer(self.cfg.embed_model,device=self.device,model_kwargs={"attn_implementation": "eager"}) 
        self.reranker = CrossEncoder(self.cfg.rerank_model,device=self.device,model_kwargs={"attn_implementation": "eager"})
        # Vector store
        self.qc = QdrantClient(url=self.cfg.qdrant_url)
        self._ensure_collection(self.emb.get_sentence_embedding_dimension())

        # Optional tiny seed corpus (kept for parity with your old code)
        self._seed_once()

    # ---------- Public API ----------
    def health(self) -> Dict:
        return {
            "ok": True,
            "qdrant": self.cfg.qdrant_url,
            "collection": self.cfg.collection,
            "model": self.cfg.ollama_model,
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
        scores = self.reranker.predict(pairs).tolist()
        order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
        ranked = [passages[i] for i in order]
        ranked_scores = [scores[i] for i in order]
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
            # stable 32-bit int id
            pid = int(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}-{i}").int % 2**31)
            points.append(
                PointStruct(
                    id=pid,
                    vector=vec.tolist(),
                    payload={"text": txt, "doc_id": doc_id, "chunk": i},
                )
            )
        self.qc.upsert(self.cfg.collection, points=points)

    def _ensure_collection(self, dim: int) -> None:
        names = [c.name for c in self.qc.get_collections().collections]
        if self.cfg.collection not in names:
            self.qc.create_collection(
                self.cfg.collection,
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
