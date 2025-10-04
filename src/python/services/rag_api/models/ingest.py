# services/rag_api/models/ingest.py
from pydantic import BaseModel

class IngestTextRequest(BaseModel):
    doc_id: str
    text: str

class IngestUrlRequest(BaseModel):
    url: str
    doc_id: str | None = None
