# services/rag_api/routers/ingest_raw.py
from fastapi import APIRouter, UploadFile, File, Form
import requests, re
from ..core import core
from ..models.ingest import IngestTextRequest, IngestUrlRequest

router = APIRouter(prefix="/ingest", tags=["ingest-raw"])

@router.post("/text")
def ingest_text(req: IngestTextRequest):
    n = core.ingest_text(req.doc_id, req.text)
    return {"ok": True, "doc_id": req.doc_id, "chunks": n}

@router.post("/file")
async def ingest_file(file: UploadFile = File(...), doc_id: str | None = Form(None)):
    name = doc_id or file.filename
    raw = await file.read()
    try:
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        text = ""
    n = core.ingest_text(name, text) if text else 0
    return {"ok": bool(n), "doc_id": name, "chunks": n}

@router.post("/url")
def ingest_url(req: IngestUrlRequest):
    html = requests.get(req.url, timeout=30).text
    # naive strip tags (BeautifulSoup optional)
    try:
        import bs4
        soup = bs4.BeautifulSoup(html, "lxml")
        text = " ".join(soup.stripped_strings)
    except Exception:
        text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = " ".join(text.split())
    doc_id = req.doc_id or req.url
    n = core.ingest_text(doc_id, text)
    return {"ok": True, "doc_id": doc_id, "chunks": n}
