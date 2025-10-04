# services/rag_api/routers/index_blocks.py
from datetime import datetime
from typing import Dict, List
from fastapi import APIRouter
from ..core import core
from ..models.textblocks import TextBlocksDto

router = APIRouter(tags=["index-blocks"])

def _group_lines_by_page(blocks):
    pages: Dict[int, List[str]] = {}
    for b in sorted(blocks, key=lambda x: (x.page, x.order)):
        pages.setdefault(b.page, []).append(b.text)
    return pages

@router.post("/index/blocks")
def index_blocks(dto: TextBlocksDto):
    pages = _group_lines_by_page(dto.blocks)
    passages = ["\n".join(lines) for lines in pages.values() if lines]
    if not passages and dto.blocks:
        passages = ["\n".join(b.text for b in sorted(dto.blocks, key=lambda x: x.order))]
    n = core.ingest_plain_chunks(dto.sourceId, passages)
    batch_id = f"batch-{dto.sourceId}-{int(datetime.utcnow().timestamp())}"
    return {"batchId": batch_id, "received": len(dto.blocks), "chunks": n}
