# services/rag_api/routers/domain_analysis.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List
from ..core import core

router = APIRouter(prefix="/domain", tags=["domain-analysis"])

class DomainDetectionRequest(BaseModel):
    text: str

class DomainDetectionResponse(BaseModel):
    detected_domain: str
    confidence: float
    supported_domains: List[str]
    domain_keywords_matched: Dict[str, int]

class IngestWithDomainRequest(BaseModel):
    doc_id: str
    text: str
    domain_hint: str | None = None  # Optional domain override

@router.post("/detect", response_model=DomainDetectionResponse)
def detect_domain(req: DomainDetectionRequest):
    """Detect the domain of a given text"""
    domain, confidence = core.detect_domain(req.text)

    # Count matched keywords for each domain
    text_lower = req.text.lower()
    keyword_matches = {}
    for domain_name, keywords in core.domain_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        keyword_matches[domain_name] = matches

    return DomainDetectionResponse(
        detected_domain=domain,
        confidence=confidence,
        supported_domains=list(core.domain_keywords.keys()),
        domain_keywords_matched=keyword_matches
    )

@router.post("/ingest-with-domain")
def ingest_with_domain(req: IngestWithDomainRequest):
    """Ingest text with domain detection or hint"""
    # Override domain detection if hint provided
    if req.domain_hint and req.domain_hint in core.domain_keywords:
        domain = req.domain_hint
        confidence = 1.0
    else:
        domain, confidence = core.detect_domain(req.text)

    # Use the enhanced ingestion method
    chunks = core.ingest_text(req.doc_id, req.text)

    return {
        "ok": True,
        "doc_id": req.doc_id,
        "chunks": chunks,
        "detected_domain": domain,
        "domain_confidence": confidence,
        "accuracy_estimate": "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
    }

@router.get("/analytics")
def get_domain_analytics():
    """Get analytics about stored documents by domain"""
    try:
        # Get collection info
        collection_info = core.qc.get_collection(core.cfg.collection)

        # This is a simplified version - in production you'd want to
        # scroll through all points and aggregate by domain
        return {
            "total_documents": collection_info.points_count,
            "supported_domains": list(core.domain_keywords.keys()),
            "domain_detection_enabled": core.cfg.enable_domain_detection,
            "confidence_threshold": core.cfg.min_confidence_threshold,
            "embedding_model": core.cfg.embed_model,
            "status": "Domain-aware RAG enabled"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "Unable to retrieve analytics"
        }

@router.get("/test")
def test_domain_detection():
    """Test domain detection with sample texts"""
    test_texts = {
        "finance": "Our mortgage loan portfolio shows a 15% increase in default risk. The investment committee recommends reviewing credit policies and compliance procedures.",
        "legal": "This contract agreement contains liability clauses that require jurisdiction review. The legal team must assess potential lawsuit exposure.",
        "medical": "Patient diagnosis indicates symptoms requiring immediate treatment. The doctor prescribed medication following clinical protocols.",
        "technical": "The API configuration requires system architecture updates. Deploy the new software using proper protocols and programming standards.",
        "education": "Students enrolled in the curriculum must complete academic requirements. The university teaching standards emphasize learning outcomes."
    }

    results = {}
    for expected_domain, text in test_texts.items():
        detected_domain, confidence = core.detect_domain(text)
        results[expected_domain] = {
            "text_sample": text[:100] + "...",
            "detected_domain": detected_domain,
            "confidence": confidence,
            "correct_detection": detected_domain == expected_domain
        }

    return {
        "test_results": results,
        "overall_accuracy": sum(1 for r in results.values() if r["correct_detection"]) / len(results)
    }
