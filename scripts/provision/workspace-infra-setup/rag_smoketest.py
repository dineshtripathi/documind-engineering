#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, time, math, textwrap, requests
from typing import List, Tuple
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# -------- Config --------
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "smoketest_docs")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
 # fast; use BAAI/bge-reranker-v2-m3 for quality
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3.5:3.8b-mini-instruct-q8_0")    # or llama3.1:8b-instruct-q4_K_M
TOPK = int(os.getenv("TOPK", "12"))
CONTEXT_K = int(os.getenv("CONTEXT_K", "6"))
SEED_DOCS = True  # set False if you want to re-run without re-upserting

# -------- Tiny corpus (you can replace with your own later) --------
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

# -------- Helpers --------
def chunk_text(text: str, max_tokens: int = 220, overlap: int = 40) -> List[str]:
    # naive token-ish splitter by sentences; good enough for smoke
    paras = [p.strip() for p in text.splitlines() if p.strip()]
    chunks, buf = [], []
    def toklen(s): return len(s.split())
    count = 0
    for p in paras:
        w = toklen(p)
        if count + w > max_tokens and buf:
            chunks.append(" ".join(buf))
            # overlap
            last = " ".join(buf)[-overlap*5:]  # crude char overlap
            buf, count = [last], toklen(last)
        buf.append(p)
        count += w
    if buf:
        chunks.append(" ".join(buf))
    return chunks

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

@dataclass
class Passage:
    id: str
    text: str
    doc_id: str
    score: float

# -------- Init models (GPU if available) --------
print("Loading embedding model:", EMBED_MODEL)
emb_model = SentenceTransformer(EMBED_MODEL)  # auto CUDA if available
print("Loading rerank model:", RERANK_MODEL)
rerank_model = CrossEncoder(RERANK_MODEL, device="cuda")



# -------- Qdrant --------
qc = QdrantClient(url=QDRANT_URL)

def ensure_collection(dim: int):
    existing = [c.name for c in qc.get_collections().collections]
    if COLLECTION not in existing:
        qc.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        # simple payload index for doc_id
        try:
            qc.create_payload_index(COLLECTION, field_name="doc_id")
        except Exception:
            pass

def upsert_docs():
    points = []
    pid = 1
    for doc_id, txt in DOCS.items():
        for ch in chunk_text(txt):
            vec = emb_model.encode([ch], normalize_embeddings=True)[0]
            points.append(PointStruct(
                id=pid,
                vector=vec.tolist(),
                payload={"text": ch, "doc_id": doc_id}
            ))
            pid += 1
    if points:
        qc.upsert(COLLECTION, points=points)

def search(query: str, k: int = TOPK, filter_doc: str | None = None) -> List[Passage]:
    qv = emb_model.encode([query], normalize_embeddings=True)[0].tolist()
    flt = None
    if filter_doc:
        flt = Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=filter_doc))])
    res = qc.search(
        collection_name=COLLECTION,
        query_vector=qv,
        limit=k,
        query_filter=flt,
        with_payload=True,
        with_vectors=False,
    )
    out = []
    for r in res:
        p = Passage(
            id=str(r.id),
            text=r.payload["text"],
            doc_id=r.payload["doc_id"],
            score=float(r.score),
        )
        out.append(p)
    return out

def rerank(query: str, passages: List[Passage]) -> Tuple[List[Passage], List[float]]:
    pairs = [(query, p.text) for p in passages]
    scores = rerank_model.predict(pairs).tolist()
    order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
    ranked = [passages[i] for i in order]
    ranked_scores = [scores[i] for i in order]
    return ranked, ranked_scores

def build_prompt(query: str, contexts: List[Passage], k: int = CONTEXT_K) -> str:
    ctx = []
    for p in contexts[:k]:
        cite = f"(source: {p.doc_id}, chunk #{p.id})"
        ctx.append(f"{p.text.strip()}\n{cite}")
    context_block = "\n\n---\n\n".join(ctx)
    sys = (
        "You are a precise assistant. Answer ONLY using the context below. "
        "If the answer is not present, say 'not found'. Always include citations."
    )
    return textwrap.dedent(f"""
    [SYSTEM]
    {sys}

    [CONTEXT]
    {context_block}

    [QUESTION]
    {query}

    [INSTRUCTIONS]
    - Keep the answer concise.
    - Cite sources inline like (source: filename, chunk #id).
    """)

def ollama_generate(prompt: str, model: str = OLLAMA_MODEL, temperature: float = 0.2) -> str:
    url = f"{OLLAMA_URL}/api/generate"
    resp = requests.post(url, json={
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature}
    }, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()

def relevance_confidence(query_vec: np.ndarray, chunks_vecs: List[np.ndarray]) -> Tuple[float, float]:
    sims = np.array([cosine(query_vec, v) for v in chunks_vecs], dtype=np.float32)
    top = np.sort(sims)[-3:]
    coverage = float((sims >= 0.40).mean())
    return float(np.mean(top)), coverage

def main():
    # 1) Make collection
    dim = emb_model.get_sentence_embedding_dimension()
    ensure_collection(dim)

    # 2) Upsert seed docs (disable if collection already populated)
    if SEED_DOCS:
        print("Upserting seed docs into Qdrant...")
        upsert_docs()

    # 3) Ask something factual
    query = "What are the phases in the disaster recovery process and the RTO/RPO targets?"
    print("\nQuery:", query)

    # search (vector)
    hits = search(query, k=TOPK)
    if not hits:
        print("No hits returned from Qdrant.")
        return

    # compute quick recall proxy (embedding-based)
    qvec = emb_model.encode([query], normalize_embeddings=True)[0]
    chunk_vecs = emb_model.encode([h.text for h in hits], normalize_embeddings=True)
    recall, coverage = relevance_confidence(qvec, chunk_vecs)
    print(f"Recall proxy(avg top3): {recall:.3f}  | Coverage>=0.40: {coverage:.2f}")

    # rerank
    ranked, ce_scores = rerank(query, hits)
    print("Top reranked passages (doc_id :: score):")
    for p, s in list(zip(ranked, ce_scores))[:3]:
        print(f" - {p.doc_id:18} :: {s:.3f}")

    # prompt build
    prompt = build_prompt(query, ranked, k=CONTEXT_K)
    # call LLM
    print("\nCalling Ollama model:", OLLAMA_MODEL)
    answer = ollama_generate(prompt, OLLAMA_MODEL)
    print("\n=== ANSWER ===\n", answer)

    # integrity: simple token overlap check
    def tokset(s): return set([t.lower() for t in s.split()])
    a = tokset(answer)
    overlaps = [len(a & tokset(p.text)) / (len(a)+1e-9) for p in ranked[:CONTEXT_K]]
    best_overlap = max(overlaps) if overlaps else 0.0
    has_citation = "(source:" in answer
    print(f"\nIntegrity → overlap: {best_overlap:.3f}  | cites present: {has_citation}")
    if not has_citation or (recall < 0.35 and coverage < 0.40):
        print("⚠️ Low confidence; consider escalating to Azure model or answering 'not found'.")

if __name__ == "__main__":
    main()
