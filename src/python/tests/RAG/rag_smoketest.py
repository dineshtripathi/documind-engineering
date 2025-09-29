# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# """
# rag_smoketest.py
# ----------------
# Quick smoke test for local RAG pipeline:
# - HuggingFace embeddings (bge-m3)
# - Qdrant vector DB
# - Jina reranker
# - Ollama LLM generation
# """

# import os, textwrap, requests, numpy as np
# from typing import List, Tuple
# from dataclasses import dataclass
# from qdrant_client import QdrantClient
# from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
# from sentence_transformers import SentenceTransformer, CrossEncoder

# # ---------------- Config ----------------
# QDRANT_URL   = os.getenv("QDRANT_URL", "http://localhost:6333")
# COLLECTION   = os.getenv("QDRANT_COLLECTION", "smoketest_docs")
# EMBED_MODEL  = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
# RERANK_MODEL = os.getenv("RERANK_MODEL", "jinaai/jina-reranker-v1-turbo-en")
# OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3.5:3.8b-mini-instruct-q4_0")
# TOPK         = int(os.getenv("TOPK", "12"))
# CONTEXT_K    = int(os.getenv("CONTEXT_K", "6"))
# SEED_DOCS    = True  # set False if collection already populated

# # ---------------- Sample corpus ----------------
# DOCS = {
#     "dr_runbook.md": """
#     # Disaster Recovery Runbook
#     The DR process includes three phases: Preparation, Failover, and Validation.
#     Preparation: ensure backups are tested, RPO is under 15 minutes, and RTO under 1 hour.
#     Failover: promote the replica in the disaster region and switch DNS traffic.
#     Validation: run automated health checks and data consistency checks.
#     """,
#     "backup_policy.md": """
#     # Backup Policy
#     Daily incremental backups at 01:00 UTC, weekly full backups on Sunday 02:00 UTC.
#     Retention: incrementals for 30 days, full backups for 12 months.
#     Encryption: AES-256 at rest and TLS 1.2 in transit.
#     """,
#     "biryani.txt": """
#     Add basmati rice, marinate chicken with yogurt and spices, cook on low heat.
#     This is a cooking recipe unrelated to disaster recovery or backup policies.
#     """,
# }

# # ---------------- Helpers ----------------
# def chunk_text(text: str, max_tokens: int = 220, overlap: int = 40) -> List[str]:
#     paras = [p.strip() for p in text.splitlines() if p.strip()]
#     chunks, buf = [], []
#     count = 0
#     for p in paras:
#         w = len(p.split())
#         if count + w > max_tokens and buf:
#             chunks.append(" ".join(buf))
#             # crude overlap
#             last = " ".join(buf).split()[-overlap:]
#             buf, count = last, len(last)
#         buf.append(p)
#         count += w
#     if buf:
#         chunks.append(" ".join(buf))
#     return chunks

# def cosine(a: np.ndarray, b: np.ndarray) -> float:
#     return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

# @dataclass
# class Passage:
#     id: str
#     text: str
#     doc_id: str
#     score: float

# # ---------------- Init models ----------------
# print(f"Loading embedding model: {EMBED_MODEL}")
# emb_model = SentenceTransformer(EMBED_MODEL)
# print(f"Loading rerank model: {RERANK_MODEL}")
# rerank_model = CrossEncoder(RERANK_MODEL, device="cuda" if emb_model.device.type == "cuda" else "cpu")

# # ---------------- Qdrant ----------------
# qc = QdrantClient(url=QDRANT_URL)

# def ensure_collection(dim: int):
#     existing = [c.name for c in qc.get_collections().collections]
#     if COLLECTION not in existing:
#         qc.create_collection(
#             collection_name=COLLECTION,
#             vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
#         )
#         try:
#             qc.create_payload_index(COLLECTION, field_name="doc_id")
#         except Exception:
#             pass

# def upsert_docs():
#     points, pid = [], 1
#     for doc_id, txt in DOCS.items():
#         for ch in chunk_text(txt):
#             vec = emb_model.encode([ch], normalize_embeddings=True)[0]
#             points.append(PointStruct(
#                 id=pid,
#                 vector=vec.tolist(),
#                 payload={"text": ch, "doc_id": doc_id}
#             ))
#             pid += 1
#     if points:
#         qc.upsert(COLLECTION, points=points)

# def search(query: str, k: int = TOPK, filter_doc: str | None = None) -> List[Passage]:
#     qv = emb_model.encode([query], normalize_embeddings=True)[0].tolist()
#     flt = None
#     if filter_doc:
#         flt = Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=filter_doc))])
#     res = qc.search(
#         collection_name=COLLECTION,
#         query_vector=qv,
#         limit=k,
#         query_filter=flt,
#         with_payload=True,
#     )
#     return [Passage(str(r.id), r.payload["text"], r.payload["doc_id"], float(r.score)) for r in res]

# def rerank(query: str, passages: List[Passage]) -> Tuple[List[Passage], List[float]]:
#     pairs = [(query, p.text) for p in passages]
#     scores = rerank_model.predict(pairs).tolist()
#     order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
#     return [passages[i] for i in order], [scores[i] for i in order]

# def build_prompt(query: str, contexts: List[Passage], k: int = CONTEXT_K) -> str:
#     ctx = []
#     for p in contexts[:k]:
#         cite = f"(source: {p.doc_id}, chunk #{p.id})"
#         ctx.append(f"{p.text.strip()}\n{cite}")
#     context_block = "\n\n---\n\n".join(ctx)
#     sys = "You are a precise assistant. Answer ONLY using the context below. If not found, say 'not found'."
#     return textwrap.dedent(f"""
#     [SYSTEM]
#     {sys}

#     [CONTEXT]
#     {context_block}

#     [QUESTION]
#     {query}
#     """)

# def ollama_generate(prompt: str, model: str = OLLAMA_MODEL, temperature: float = 0.2) -> str:
#     resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
#         "model": model,
#         "prompt": prompt,
#         "stream": False,
#         "options": {"temperature": temperature}
#     }, timeout=120)
#     resp.raise_for_status()
#     return resp.json().get("response", "").strip()

# # ---------------- Main ----------------
# def main():
#     dim = emb_model.get_sentence_embedding_dimension()
#     ensure_collection(dim)
#     if SEED_DOCS:
#         print("Upserting seed docs...")
#         upsert_docs()

#     query = "What are the phases in the disaster recovery process and the RTO/RPO targets?"
#     print(f"\nQuery: {query}")

#     hits = search(query, k=TOPK)
#     if not hits:
#         print("❌ No hits from Qdrant.")
#         return

#     # rerank
#     ranked, ce_scores = rerank(query, hits)
#     print("Top reranked passages:")
#     for p, s in list(zip(ranked, ce_scores))[:3]:
#         print(f" - {p.doc_id} :: {s:.3f}")

#     # build + ask LLM
#     prompt = build_prompt(query, ranked, k=CONTEXT_K)
#     print("\nCalling Ollama model:", OLLAMA_MODEL)
#     answer = ollama_generate(prompt)
#     print("\n=== ANSWER ===\n", answer)

# if __name__ == "__main__":
#     main()
#----------


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG smoke test:
- Embeddings: HuggingFace (BGE-M3)
- Vector DB: Qdrant (query_points if present; else legacy search)
- Reranker: CrossEncoder (default BGE v2 m3 for quality)
- Generator: Ollama (generate -> chat fallback)
- Citations: Numbered [1][2] enforced; invalid -> 'not found'
"""

import os, re, textwrap, requests
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue
)

# ------------------ Config (env overrides) ------------------
QDRANT_URL   = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION   = os.getenv("QDRANT_COLLECTION", "smoketest_docs")

EMBED_MODEL  = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
# Quality (default): BAAI/bge-reranker-v2-m3   | Speed: jinaai/jina-reranker-v1-turbo-en
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")

OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
# Use any installed instruct model; examples you have: phi3.5:3.8b-mini-instruct-q4_0, mixtral:8x7b-instruct-v0.1-q4_0
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3.5:3.8b-mini-instruct-q4_0")

TOPK         = int(os.getenv("TOPK", "12"))
CONTEXT_K    = int(os.getenv("CONTEXT_K", "4"))  # tighter context
SEED_DOCS    = os.getenv("SEED_DOCS", "true").lower() in ("1","true","yes")

# ------------------ Tiny sample corpus ------------------
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

# ------------------ Helpers ------------------
def chunk_text(text: str, max_tokens: int = 180, overlap: int = 50) -> List[str]:
    """Naive sentence-ish chunker with overlap."""
    paras = [p.strip() for p in text.splitlines() if p.strip()]
    chunks, buf, count = [], [], 0
    for p in paras:
        w = len(p.split())
        if count + w > max_tokens and buf:
            chunks.append(" ".join(buf))
            # overlap by last N words
            last = " ".join(buf).split()[-overlap:]
            buf, count = last.copy(), len(last)
        buf.append(p); count += w
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

# ------------------ Models ------------------
print(f"Loading embedding model: {EMBED_MODEL}")
emb_model = SentenceTransformer(EMBED_MODEL)

print(f"Loading rerank model: {RERANK_MODEL}")
rerank_model = CrossEncoder(
    RERANK_MODEL,
    device=("cuda" if emb_model.device.type == "cuda" else "cpu"),
    trust_remote_code=("bge" in RERANK_MODEL.lower())  # needed for some BGE variants
)

# ------------------ Qdrant ------------------
qc = QdrantClient(url=QDRANT_URL)

def ensure_collection(dim: int):
    existing = [c.name for c in qc.get_collections().collections]
    if COLLECTION not in existing:
        qc.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        try:
            qc.create_payload_index(COLLECTION, field_name="doc_id")
        except Exception:
            pass

def upsert_docs():
    points, pid = [], 1
    for doc_id, txt in DOCS.items():
        for ch in chunk_text(txt):
            vec = emb_model.encode([ch], normalize_embeddings=True)[0]
            points.append(PointStruct(
                id=pid, vector=vec.tolist(),
                payload={"text": ch, "doc_id": doc_id}
            ))
            pid += 1
    if points:
        qc.upsert(COLLECTION, points=points)

def _search_legacy(qv, flt, k) -> List[Passage]:
    res = qc.search(
        collection_name=COLLECTION,
        query_vector=qv,
        limit=k,
        query_filter=flt,
        with_payload=True,
        with_vectors=False,
    )
    return [Passage(str(r.id), r.payload["text"], r.payload["doc_id"], float(r.score)) for r in res]

def search(query: str, k: int = TOPK, filter_doc: str | None = None) -> List[Passage]:
    qv = emb_model.encode([query], normalize_embeddings=True)[0].tolist()
    flt = None
    if filter_doc:
        flt = Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=filter_doc))])

    # Prefer new API if available
    if hasattr(qc, "query_points"):
        try:
            # many qdrant-client versions accept raw vector directly as 'query'
            res = qc.query_points(
                collection_name=COLLECTION,
                query=qv,
                limit=k,
                query_filter=flt,
                with_payload=True,
                with_vectors=False,
            )
            points = getattr(res, "points", res)
            return [Passage(str(p.id), p.payload["text"], p.payload["doc_id"], float(p.score)) for p in points]
        except TypeError:
            # signature mismatch; fall back to legacy
            pass

    return _search_legacy(qv, flt, k)

def rerank(query: str, passages: List[Passage]) -> Tuple[List[Passage], List[float]]:
    if not passages:
        return [], []
    pairs = [(query, p.text) for p in passages]
    scores = rerank_model.predict(pairs).tolist()
    order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
    return [passages[i] for i in order], [scores[i] for i in order]

def build_prompt_numbered(query: str, contexts: List[Passage], k: int = CONTEXT_K) -> str:
    """Numbered citations [1][2] so models comply better."""
    numbered = []
    for i, p in enumerate(contexts[:k], start=1):
        numbered.append(f"[{i}] {p.text.strip()} (file: {p.doc_id}, chunk #{p.id})")
    context_block = "\n\n".join(numbered)

    sys = (
        "You must answer ONLY using the [CONTEXT]. "
        "If the answer is not present, reply exactly: not found.\n"
        "Every sentence MUST end with bracket citation(s) like [1] or [1][2] "
        "using the numbers from [CONTEXT]. Do not invent numbers or sources. "
        "No bullet lists of sources. Be concise."
    )
    instr = (
        "Format rules:\n"
        "- Plain sentences; each ends with citation(s), e.g., ... [1]\n"
        "- If unsure or unsupported by context, reply: not found"
    )
    return textwrap.dedent(f"""
    [SYSTEM]
    {sys}

    [CONTEXT]
    {context_block}

    [QUESTION]
    {query}

    [INSTRUCTIONS]
    {instr}
    """)

def ollama_generate(prompt: str, model: str = OLLAMA_MODEL, temperature: float = 0.1, top_p: float = 0.9) -> str:
    base = OLLAMA_URL.rstrip("/")
    # Try /api/generate
    r = requests.post(f"{base}/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "top_p": top_p}
    }, timeout=120)
    if r.status_code == 200:
        return r.json().get("response", "").strip()

    try: print("Ollama /api/generate error payload:", r.json())
    except Exception: print("Ollama /api/generate error text:", r.text)

    # Fallback to /api/chat
    rc = requests.post(f"{base}/api/chat", json={
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature, "top_p": top_p}
    }, timeout=120)
    if rc.status_code != 200:
        try: print("Ollama /api/chat error payload:", rc.json())
        except Exception: print("Ollama /api/chat error text:", rc.text)
        raise RuntimeError(f"Ollama failed: generate={r.status_code}, chat={rc.status_code}. Check server/model: {model}")
    data = rc.json()
    msg = data.get("message", {}).get("content", "")
    if not msg and "choices" in data:
        msg = data["choices"][0]["message"]["content"]
    return (msg or "").strip()

def integrity_bracket_cites(answer: str, k_used: int) -> bool:
    """Require presence of [n] citations with allowed indices 1..k_used."""
    cites = re.findall(r"\[(\d+)\]", answer)
    if not cites:
        return False
    try:
        nums = [int(c) for c in cites]
    except ValueError:
        return False
    return all(1 <= n <= k_used for n in nums)

def main():
    dim = emb_model.get_sentence_embedding_dimension()
    ensure_collection(dim)
    if SEED_DOCS:
        print("Upserting seed docs...")
        upsert_docs()

    query = "What are the phases in the disaster recovery process and the RTO/RPO targets?"
    print(f"\nQuery: {query}")

    hits = search(query, k=TOPK)
    if not hits:
        print("❌ No hits from Qdrant.")
        return

    ranked, ce_scores = rerank(query, hits)
    print("Top reranked passages:")
    for p, s in list(zip(ranked, ce_scores))[:3]:
        print(f" - {p.doc_id:18} :: {s:.3f}")

    prompt = build_prompt_numbered(query, ranked, k=CONTEXT_K)
    print("\nCalling Ollama model:", OLLAMA_MODEL)
    answer = ollama_generate(prompt, temperature=0.1)

    # Integrity: must contain valid [n] citations within range
    if not integrity_bracket_cites(answer, k_used=min(CONTEXT_K, len(ranked))):
        print("⚠️ Missing/invalid bracket citations → returning 'not found'")
        answer = "not found"

    print("\n=== ANSWER ===\n", answer)

if __name__ == "__main__":
    main()
