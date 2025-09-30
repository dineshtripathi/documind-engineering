
import torch
import os, textwrap, re
from typing import List, Tuple
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import numpy as np

from pydantic import BaseModel
from fastapi import UploadFile, File, Form
import uuid

from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from fastapi import Body

# ------------ Config ------------
QDRANT_URL   = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
COLLECTION   = os.getenv("QDRANT_COLLECTION", "smoketest_docs")
EMBED_MODEL  = os.getenv("EMBED_MODEL", "BAAI/bge-m3")
RERANK_MODEL = os.getenv("RERANK_MODEL", "jinaai/jina-reranker-v1-turbo-en")  # fast; bge-reranker-v2-m3 for quality
TOPK         = int(os.getenv("TOPK", "12"))
CONTEXT_K    = int(os.getenv("CONTEXT_K", "4"))

OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3.5:3.8b-mini-instruct-q4_0")
RERANK_DEVICE = os.getenv("RERANK_DEVICE")  # optional override: "cpu" or "cuda"

# ------------ App ------------
app = FastAPI(title="DocuMind RAG API", version="0.2.0")

@app.get("/healthz")
def healthz():
    return {"ok": True, "qdrant": QDRANT_URL, "model": OLLAMA_MODEL}

# ------------ Tiny seed corpus ------------
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

# --- ONE canonical chunker ---
def chunk_text(text: str, max_tokens: int = 220, overlap_tokens: int = 40) -> list[str]:
    """
    Naive word-based chunking with word-overlap.
    max_tokens ~ words per chunk; overlap_tokens = words carried to next chunk.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    i = 0
    n = len(words)
    while i < n:
        j = min(i + max_tokens, n)
        chunk_words = words[i:j]
        chunks.append(" ".join(chunk_words))
        if j == n:  # finished
            break
        # move window with overlap
        i = max(0, j - overlap_tokens)
    return chunks


# ------------ Models & Qdrant ------------
_auto_device = "cuda" if torch.cuda.is_available() else "cpu"
_device = RERANK_DEVICE or _auto_device
print(f"[RAG] device -> {_device}")

emb = SentenceTransformer(EMBED_MODEL,device=_device)
#reranker = CrossEncoder(RERANK_MODEL, device="cuda" if emb.device.type == "cuda" else "cpu")
#reranker = CrossEncoder(RERANK_MODEL, device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES","") != "-1" else "cpu")
reranker = CrossEncoder(RERANK_MODEL, device=_device)

qc = QdrantClient(url=QDRANT_URL)

def rerank(query: str, passages: list[dict]):
    """
    passages: [{ 'text': str, 'doc_id': str, 'score': float, ...}]
    returns (ranked_list, scores_list)
    """
    pairs = [(query, p["text"]) for p in passages]
    scores = reranker.predict(pairs).tolist()
    order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
    ranked = [passages[i] for i in order]
    ranked_scores = [scores[i] for i in order]
    return ranked, ranked_scores

def ensure_collection(dim: int):
    names = [c.name for c in qc.get_collections().collections]
    if COLLECTION not in names:
        qc.create_collection(COLLECTION, vectors_config=VectorParams(size=dim, distance=Distance.COSINE))

def seed_docs():
    pts = []
    pid = 1
    for doc_id, txt in DOCS.items():
        for ch in chunk_text(txt):
            v = emb.encode([ch], normalize_embeddings=True)[0].tolist()
            pts.append(PointStruct(id=pid, vector=v, payload={"doc_id": doc_id, "text": ch}))
            pid += 1
    if pts:
        qc.upsert(COLLECTION, points=pts)

ensure_collection(emb.get_sentence_embedding_dimension())
# idempotent seed on first run (cheap for our tiny corpus)
try: seed_docs()
except Exception: pass

@dataclass
class Passage:
    id: str
    text: str
    doc_id: str
    score: float

def search(query: str, k: int = TOPK) -> List[Passage]:
    qv = emb.encode([query], normalize_embeddings=True)[0].tolist()
    try:
        # new API
        res = qc.query_points(collection_name=COLLECTION, query=qv, limit=k, with_payload=True, with_vectors=False)
        pts = getattr(res, "points", res)
        return [Passage(str(p.id), p.payload["text"], p.payload["doc_id"], float(p.score)) for p in pts]
    except Exception:
        # fallback older API
        res = qc.search(collection_name=COLLECTION, query_vector=qv, limit=k, with_payload=True, with_vectors=False)
        return [Passage(str(r.id), r.payload["text"], r.payload["doc_id"], float(r.score)) for r in res]

def rerank_passages(query: str, passages: List[Passage]) -> Tuple[List[Passage], List[float]]:
    if not passages: return [], []
    pairs = [(query, p.text) for p in passages]
    scores = reranker.predict(pairs).tolist()
    order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
    return [passages[i] for i in order], [scores[i] for i in order]

def build_numbered_prompt(query: str, ranked: List[Passage], k: int = CONTEXT_K) -> str:
    numbered = []
    for i, p in enumerate(ranked[:k], start=1):
        numbered.append(f"[{i}] {p.text.strip()} (file: {p.doc_id}, chunk #{p.id})")
    ctx = "\n\n".join(numbered)
    sys = ("Answer ONLY using [CONTEXT]. If not present, reply exactly: not found.\n"
           "Every sentence MUST end with [n] citations from [CONTEXT]. Do not invent sources. Be concise.")
    return textwrap.dedent(f"""
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

class BuildPromptReq(BaseModel):
    query: str

class BuildPromptResp(BaseModel):
    prompt: str
    contextK: int
    contextMap: list
    topScores: list

@app.post("/build-prompt", response_model=BuildPromptResp)
def build_prompt(req: BuildPromptReq):
    hits = search(req.query, k=TOPK)
    ranked, scores = rerank_passages(req.query, hits)
    prompt = build_numbered_prompt(req.query, ranked, k=CONTEXT_K)
    cmap = [{"index": i+1, "doc_id": p.doc_id, "chunk_id": p.id, "score": float(scores[i])}
            for i, p in enumerate(ranked[:CONTEXT_K])]
    return BuildPromptResp(prompt=prompt, contextK=CONTEXT_K, contextMap=cmap, topScores=[float(s) for s in scores[:3]])

# ------------- /ask convenience (optional) -------------
def ollama_generate(prompt: str, temperature: float = 0.2) -> str:
    # Try /api/generate; fallback to /api/chat if needed
    r = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": temperature}
    }, timeout=180)
    if r.status_code == 200:
        return r.json().get("response", "") or ""
    c = requests.post(f"{OLLAMA_URL}/api/chat", json={
        "model": OLLAMA_MODEL, "stream": False,
        "messages": [{"role":"user","content": prompt}],
        "options": {"temperature": temperature}
    }, timeout=180)
    c.raise_for_status()
    j = c.json()
    msg = j.get("message", {})
    return msg.get("content", "")

def has_valid_citations(answer: str, k: int) -> bool:
    matches = re.findall(r"\[(\d+)\]", answer)
    if not matches: return False
    for m in matches:
        try:
            n = int(m)
            if n < 1 or n > k: return False
        except: return False
    return True

@app.get("/ask")
def ask(q: str):
    # 1) build prompt
    bp = build_prompt(BuildPromptReq(query=q))
    # 2) local model
    ans = ollama_generate(bp.prompt, temperature=0.1).strip()
    if ans and ans.lower() != "not found" and has_valid_citations(ans, bp.contextK):
        return {"route": "local", "answer": ans, "contextMap": bp.contextMap}
    # 3) abstain (cloud fallback should be done by .NET orchestrator)
    return {"route": "abstain", "answer": "not found", "contextMap": bp.contextMap}

# --- ADD SCHEMAS ---
class IngestTextRequest(BaseModel):
    doc_id: str
    text: str

class IngestUrlRequest(BaseModel):
    url: str
    doc_id: str | None = None

# --- HELPERS ---
def _upsert_passages(doc_id: str, passages: list[str]):
    vecs = emb.encode(passages, normalize_embeddings=True)
    points = []
    for i, (txt, vec) in enumerate(zip(passages, vecs), start=1):
        points.append(PointStruct(
            id=int(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}-{i}").int % 2**31),
            vector=vec.tolist(),
            payload={"text": txt, "doc_id": doc_id, "chunk": i}
        ))
    qc.upsert(COLLECTION, points=points)

# --- INGEST: RAW TEXT ---
@app.post("/ingest/text")
def ingest_text(req: IngestTextRequest):
    ensure_collection(emb.get_sentence_embedding_dimension())
    chunks = chunk_text(req.text, max_tokens=220, overlap_tokens=40)
    _upsert_passages(req.doc_id, chunks)
    return {"ok": True, "doc_id": req.doc_id, "chunks": len(chunks)}

# --- INGEST: FILE (PDF/DOCX/TXT) ---
@app.post("/ingest/file")
def ingest_file(file: UploadFile = File(...), doc_id: str = Form(None)):
    ensure_collection(emb.get_sentence_embedding_dimension())
    name = doc_id or file.filename
    raw = file.file.read()
    text = raw.decode("utf-8", errors="ignore")
    chunks = chunk_text(text, max_tokens=220, overlap_tokens=40)
    _upsert_passages(name, chunks)
    return {"ok": True, "doc_id": name, "chunks": len(chunks)}

# --- INGEST: URL (basic) ---
@app.post("/ingest/url")
def ingest_url(req: IngestUrlRequest):
    import requests, bs4
    ensure_collection(emb.get_sentence_embedding_dimension())
    html = requests.get(req.url, timeout=20).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    text = " ".join(soup.stripped_strings)
    doc_id = req.doc_id or req.url
    chunks = chunk_text(text, max_tokens=220, overlap_tokens=40)
    _upsert_passages(doc_id, chunks)
    return {"ok": True, "doc_id": doc_id, "chunks": len(chunks)}

# --- DEBUG: pure search (no LLM) ---
@app.get("/rag/search")
def rag_search(q: str, k: int = 8):
    hits: List[Passage] = search(q, k=k)
    ranked, scores = rerank_passages(q, hits)  # <-- correct helper
    return {
        "query": q,
        "top": [
            {
                "doc_id": p.doc_id,
                "chunk": p.id,
                "score": float(s),
                "preview": p.text[:160],
            }
            for p, s in list(zip(ranked, scores))[:k]
        ],
    }
class AskRequest(BaseModel):
    q: str

@app.post("/ask")
def ask_post(payload: AskRequest = Body(...)):
    return ask(payload.q)  # reuse the GET handler

@app.get("/ask")
def ask(q: str):
    bp = build_prompt(BuildPromptReq(query=q))
    ans = ollama_generate(bp.prompt, temperature=0.1).strip()
    if ans and ans.lower() != "not found" and has_valid_citations(ans, bp.contextK):
        return {"route": "local", "answer": ans, "contextMap": bp.contextMap}
    return {"route": "abstain", "answer": "not found", "contextMap": bp.contextMap}