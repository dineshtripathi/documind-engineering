# services/rag_api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core import core
from .routers.ask import router as ask_router
from .routers.ingest_raw import router as ingest_raw_router
from .routers.ingest_ocr import router as ingest_ocr_router
from .routers.index_blocks import router as index_blocks_router
from .routers.domain_analysis import router as domain_router
from .routers.code_generation import router as code_router
from .routers.crawler import router as crawler_router

app = FastAPI(
    title="DocuMind RAG API",
    version="0.7.0",
    description="""
    ## DocuMind RAG API - Intelligent Document Processing

    This API provides comprehensive document intelligence capabilities with:

    ### 🧠 Multi-Model AI
    - **phi3.5** for general chat and document Q&A
    - **DeepSeek Coder 6.7B** for technical documentation and code generation
    - **CodeQwen 7B** for code explanation and analysis
    - **BGE-M3** embeddings for semantic search
    - **Jina Reranker** for result optimization

    ### 🕷️ Web Crawling
    - On-demand web content crawling
    - Specialized crawlers for Python docs, Microsoft docs, StackOverflow
    - Background job management with real-time status tracking

    ### 🎯 Domain Intelligence
    - Automatic domain detection (technical, finance, legal, medical, education)
    - Task-type based model selection
    - Context-aware response generation

    ### 📄 Document Ingestion
    - Text, file, and URL-based ingestion
    - Automatic chunking and vectorization
    - Multi-format support (PDF, DOCX, TXT)

    ### 🔍 Advanced Search
    - Semantic vector search with Qdrant
    - Re-ranking for improved relevance
    - Citation-enforced responses
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz",
         summary="Health Check",
         description="Get system health status and available models",
         tags=["System"])
def healthz():
    return core.health()

# Feature routers
app.include_router(ask_router)            # /ask, /build-prompt, /rag/search
app.include_router(ingest_raw_router)     # /ingest/text | /ingest/file | /ingest/url
app.include_router(ingest_ocr_router)     # /ingest/upload | /ingest/blob
app.include_router(index_blocks_router)   # /index/blocks
app.include_router(domain_router)         # /domain/* - Domain-aware capabilities
app.include_router(code_router)           # /code/* - Code generation capabilities
app.include_router(crawler_router)        # /crawler/* - Web crawling capabilities



# # app.py
# from __future__ import annotations
# import os
# from typing import List

# from fastapi import FastAPI, UploadFile, File, Form, Body, Query
# from pydantic import BaseModel

# from .core.rag_core import core
# from .vision_ingest import router as vision_router

# from pydantic import BaseModel
# app = FastAPI(title="DocuMind RAG API", version="0.3.0")

# from .vision_index import router as vision_index_router
# app.include_router(vision_index_router)    # adds POST /index/blocks
# app.include_router(vision_router)

# # ------------ Favicon ------------
# # @app.get("/favicon.ico")
# # def favicon():
# #     return Response(status_code=204)

# # ------------ Health ------------
# @app.get("/healthz")
# def healthz():
#     return core.health()


# # ------------ Build Prompt (debug) ------------
# class BuildPromptReq(BaseModel):
#     query: str

# class BuildPromptResp(BaseModel):
#     prompt: str
#     contextK: int
#     contextMap: list
#     topScores: list

# @app.post("/build-prompt", response_model=BuildPromptResp)
# def build_prompt(req: BuildPromptReq):
#     hits = core.search(req.query, k=core.cfg.topk)
#     ranked, scores = core.rerank(req.query, hits)
#     prompt, cmap = core.build_prompt(req.query, ranked, k=core.cfg.context_k)
#     return BuildPromptResp(
#         prompt=prompt,
#         contextK=core.cfg.context_k,
#         contextMap=cmap,
#         topScores=[float(s) for s in scores[:3]]
#     )


# # ------------ Ask (GET/POST) ------------
# class AskRequest(BaseModel):
#     q: str

# @app.get("/ask")
# def ask_get(q: str = Query(...)):
#     return core.ask_local(q)

# @app.post("/ask")
# def ask_post(payload: AskRequest = Body(...)):
#     return core.ask_local(payload.q)


# # ------------ Ingest (raw text) ------------
# class IngestTextRequest(BaseModel):
#     doc_id: str
#     text: str

# @app.post("/ingest/text")
# def ingest_text(req: IngestTextRequest):
#     n = core.ingest_text(req.doc_id, req.text)
#     return {"ok": True, "doc_id": req.doc_id, "chunks": n}


# # ------------ Ingest (file: txt-like only for now) ------------
# @app.post("/ingest/file")
# def ingest_file(file: UploadFile = File(...), doc_id: str = Form(None)):
#     # NOTE: vision/pdf OCR handled in vision_app via /ingest/blob
#     name = doc_id or file.filename
#     raw = file.file.read()
#     try:
#         text = raw.decode("utf-8", errors="ignore")
#     except Exception:
#         text = ""
#     n = core.ingest_text(name, text) if text else 0
#     return {"ok": bool(n), "doc_id": name, "chunks": n}


# # ------------ Ingest (URL basic) ------------
# class IngestUrlRequest(BaseModel):
#     url: str
#     doc_id: str | None = None

# @app.post("/ingest/url")
# def ingest_url(req: IngestUrlRequest):
#     import requests
#     text = ""
#     html = requests.get(req.url, timeout=30).text

#     # Try BeautifulSoup if available
#     try:
#         import bs4
#         soup = bs4.BeautifulSoup(html, "lxml")
#         text = " ".join(soup.stripped_strings)
#     except Exception:
#         # Fallback: naive strip tags
#         import re
#         text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html, flags=re.I)
#         text = re.sub(r"<[^>]+>", " ", text)
#         text = " ".join(text.split())

#     doc_id = req.doc_id or req.url
#     n = core.ingest_text(doc_id, text)
#     return {"ok": True, "doc_id": doc_id, "chunks": n}


# # ------------ Pure search (debug) ------------
# @app.get("/rag/search")
# def rag_search(q: str, k: int = 8):
#     hits = core.search(q, k=k)
#     ranked, scores = core.rerank(q, hits)
#     top = []
#     for p, s in list(zip(ranked, scores))[:k]:
#         top.append({
#             "doc_id": p["doc_id"],
#             "chunk": p["id"],
#             "score": float(s),
#             "preview": p["text"][:160],
#         })
#     return {"query": q, "top": top}


# # ------------ Mount vision ingest router ------------
# app.include_router(vision_router)
