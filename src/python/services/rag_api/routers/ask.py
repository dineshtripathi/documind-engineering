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
    task_type: str = "general"  # general, code_generation, code_explanation, technical

class EnhancedAskRequest(BaseModel):
    q: str
    task_type: str = "general"
    preferred_model: str | None = None

@router.get("/ask")
def ask_get(q: str = Query(...), task_type: str = Query("general")):
    """Simple ask endpoint with optional task type for model selection."""
    return core.ask_local_with_model_selection(q, task_type)

@router.post("/ask")
def ask_post(payload: AskRequest = Body(...)):
    """Enhanced ask endpoint with model selection based on task type."""
    return core.ask_local_with_model_selection(payload.q, payload.task_type)

@router.post("/ask/enhanced")
def ask_enhanced(payload: EnhancedAskRequest = Body(...)):
    """Advanced ask endpoint with explicit model control."""
    if payload.preferred_model:
        # Use specific model if requested
        hits = core.search(payload.q, k=core.cfg.topk)
        ranked, scores = core.rerank(payload.q, hits)
        prompt, cmap = core.build_prompt(payload.q, ranked, k=core.cfg.context_k)
        ans = core._ollama_generate_with_model(prompt, payload.preferred_model, temperature=0.1).strip()

        if ans and ans.lower() != "not found" and core._has_valid_citations(ans, core.cfg.context_k):
            return {
                "route": "local",
                "answer": ans,
                "contextMap": cmap,
                "model_used": payload.preferred_model,
                "task_type": payload.task_type
            }
        return {
            "route": "abstain",
            "answer": "not found",
            "contextMap": cmap,
            "model_used": payload.preferred_model,
            "task_type": payload.task_type
        }
    else:
        # Use automatic model selection
        return core.ask_local_with_model_selection(payload.q, payload.task_type)

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
