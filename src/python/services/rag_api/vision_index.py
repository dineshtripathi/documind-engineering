# from datetime import datetime
# from typing import List, Optional, Dict
# from fastapi import APIRouter
# from pydantic import BaseModel

# from .core.rag_core import ingest_plain_chunks  # or core.ingest_text if that's your primitive

# router = APIRouter(tags=["vision-index"])  # no prefix; we keep /index/blocks

# # ----- C# TextBlocksDto mirrors -----
# class TextBlock(BaseModel):
#     page: int
#     text: str
#     confidence: Optional[float] = None
#     bbox: Optional[List[float]] = None
#     order: int

# class Caption(BaseModel):
#     page: int
#     text: str
#     confidence: Optional[float] = None

# class TextBlocksDto(BaseModel):
#     sourceId: str
#     sourceUri: str
#     sourceType: str
#     language: str
#     blocks: List[TextBlock]
#     captions: List[Caption]
#     tags: List[str]
#     ingestedAt: datetime

# def _group_lines_by_page(blocks: List[TextBlock]) -> Dict[int, List[str]]:
#     pages: Dict[int, List[str]] = {}
#     for b in sorted(blocks, key=lambda x: (x.page, x.order)):
#         pages.setdefault(b.page, []).append(b.text)
#     return pages

# @router.post("/index/blocks")
# def index_blocks(dto: TextBlocksDto):
#     pages = _group_lines_by_page(dto.blocks)
#     passages = ["\n".join(lines) for lines in pages.values() if lines]

#     if not passages and dto.blocks:
#         passages = ["\n".join(b.text for b in sorted(dto.blocks, key=lambda x: x.order))]

#     chunks_ingested = ingest_plain_chunks(dto.sourceId, passages)
#     batch_id = f"batch-{dto.sourceId}-{int(datetime.utcnow().timestamp())}"
#     return {"batchId": batch_id, "received": len(dto.blocks), "chunks": chunks_ingested}
