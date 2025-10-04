# services/rag_api/models/textblocks.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class TextBlock(BaseModel):
    page: int
    text: str
    confidence: Optional[float] = None
    bbox: Optional[List[float]] = None
    order: int

class Caption(BaseModel):
    page: int
    text: str
    confidence: Optional[float] = None

class TextBlocksDto(BaseModel):
    sourceId: str
    sourceUri: str
    sourceType: str
    language: str
    blocks: List[TextBlock]
    captions: List[Caption]
    tags: List[str]
    ingestedAt: datetime
