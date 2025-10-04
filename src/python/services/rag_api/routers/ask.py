# services/rag_api/routers/ask.py
from fastapi import APIRouter, Body, Query
from pydantic import BaseModel
from ..core import core

router = APIRouter(tags=["ask"])

class BuildPromptReq(BaseModel):
    query: str

class BuildPromptResp(BaseModel):
    prompt: str
    contextK: int
    contextMap: list
    topScores: list

@router.post("/build-prompt", response_model=BuildPromptResp)
def build_prompt(req: BuildPromptReq):
    hits = core.search(req.query, k=core.cfg.topk)
    ranked, scores = core.rerank(req.query, hits)
    prompt, cmap = core.build_prompt(req.query, ranked, k=core.cfg.context_k)
    return BuildPromptResp(
        prompt=prompt,
        contextK=core.cfg.context_k,
        contextMap=cmap,
        topScores=[float(s) for s in scores[:3]]
    )

class AskRequest(BaseModel):
    q: str

@router.get("/ask")
def ask_get(q: str = Query(...)):
    return core.ask_local(q)

@router.post("/ask")
def ask_post(payload: AskRequest = Body(...)):
    return core.ask_local(payload.q)

@router.get("/rag/search")
def rag_search(q: str, k: int = 8):
    hits = core.search(q, k=k)
    ranked, scores = core.rerank(q, hits)
    top = []
    for p, s in list(zip(ranked, scores))[:k]:
        top.append({
            "doc_id": p["doc_id"],
            "chunk": p["id"],
            "score": float(s),
            "preview": p["text"][:160],
        })
    return {"query": q, "top": top}
