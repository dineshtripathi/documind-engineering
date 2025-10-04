# # vision_app.py
# from __future__ import annotations
# from fastapi import APIRouter
# from pydantic import BaseModel
# from typing import Optional, List
# from io import BytesIO
# import requests, mimetypes, os, tempfile

# from pypdf import PdfReader
# from PIL import Image

# from fastapi import APIRouter, UploadFile, File, Form
# import mimetypes
# try:
#     import fitz  # PyMuPDF for robust PDF rasterization
# except Exception:
#     fitz = None

# try:
#     from azure.ai.vision import (
#         VisionServiceOptions, VisionSource, VisionClient,
#         ImageAnalysisOptions, ImageAnalysisFeature
#     )
# except Exception:
#     VisionServiceOptions = VisionSource = VisionClient = ImageAnalysisOptions = ImageAnalysisFeature = None

# from .core.rag_core import core  # use the shared core

# router = APIRouter(prefix="/ingest", tags=["Vision Ingest"])


# class IngestBlobReq(BaseModel):
#     doc_id: str
#     blob_url: str              # SAS or public HTTP(S) URL
#     content_type: Optional[str] = None  # optional hint


# @router.post("/blob")
# def ingest_blob(req: IngestBlobReq):
#     data = _download(req.blob_url)
#     ctype = req.content_type or _guess_content_type(req.blob_url)

#     if ctype == "application/pdf":
#         text = _extract_pdf_text(data) or _ocr_pdf(data)
#     elif ctype.startswith("image/"):
#         text = _ocr_image(data)
#     else:
#         try:
#             text = data.decode("utf-8", errors="ignore")
#         except Exception:
#             text = ""

#     if not text.strip():
#         return {"ok": False, "doc_id": req.doc_id, "reason": "empty_text", "ctype": ctype}

#     n = core.ingest_text(req.doc_id, text)
#     return {"ok": True, "doc_id": req.doc_id, "bytes": len(data), "chunks": n, "ctype": ctype}


# # ---------- helpers ----------
# def _download(url: str) -> bytes:
#     r = requests.get(url, timeout=120)
#     r.raise_for_status()
#     return r.content

# def _guess_content_type(url: str) -> str:
#     ctype, _ = mimetypes.guess_type(url)
#     return ctype or "application/octet-stream"

# def _extract_pdf_text(data: bytes) -> str:
#     try:
#         reader = PdfReader(BytesIO(data))
#         return "\n".join((page.extract_text() or "") for page in reader.pages)
#     except Exception:
#         return ""

# def _ocr_pdf(data: bytes) -> str:
#     if fitz is None:
#         # weak fallback: try OCR of first page only if PyMuPDF missing
#         first = _pdf_first_page_as_png(data)
#         return _ocr_image(first) if first else ""
#     try:
#         with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as f:
#             f.write(data); f.flush()
#             doc = fitz.open(f.name)
#             out: List[str] = []
#             for p in doc:
#                 pix = p.get_pixmap(dpi=200)
#                 img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                 bio = BytesIO(); img.save(bio, format="PNG"); bio.seek(0)
#                 out.append(_ocr_image(bio.read()))
#             return "\n".join(out)
#     except Exception:
#         return ""

# def _pdf_first_page_as_png(data: bytes) -> bytes:
#     if fitz is None:
#         return b""
#     try:
#         with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as f:
#             f.write(data); f.flush()
#             doc = fitz.open(f.name)
#             p = doc[0]
#             pix = p.get_pixmap(dpi=200)
#             img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#             bio = BytesIO(); img.save(bio, format="PNG"); bio.seek(0)
#             return bio.read()
#     except Exception:
#         return b""

# def _ocr_image(img_bytes: bytes) -> str:
#     ep = os.environ.get("VISION_ENDPOINT")
#     key = os.environ.get("VISION_KEY")
#     if not ep or not key or VisionServiceOptions is None:
#         return ""  # Vision not configured or package not installed

#     service_options = VisionServiceOptions(ep, key)
#     source = VisionSource.from_bytes(img_bytes)
#     client = VisionClient(service_options)
#     opts = ImageAnalysisOptions(features=[ImageAnalysisFeature.READ])
#     result = client.analyze_image(source, opts)

#     if getattr(result, "reason", None) and result.reason.name != "ANALYZED":
#         return ""

#     lines = []
#     if getattr(result, "read", None):
#         for block in result.read.blocks:
#             for line in block.lines:
#                 lines.append(line.text)
#     return "\n".join(lines)

# @router.post("/upload")
# async def ingest_upload(file: UploadFile = File(...), doc_id: str = Form(None)):
#     """
#     Upload a local file (PDF/image/text). Auto-detects type and extracts text:
#       - PDF: pypdf extract → if empty → OCR via Vision
#       - Image: OCR via Vision
#       - Text: UTF-8 decode
#     """
#     raw = await file.read()
#     name = doc_id or file.filename
#     ctype = file.content_type or (mimetypes.guess_type(file.filename)[0] or "application/octet-stream")

#     # --- extract text ---
#     if ctype == "application/pdf":
#         text = _extract_pdf_text(raw) or _ocr_pdf(raw)
#     elif ctype.startswith("image/"):
#         text = _ocr_image(raw)
#     else:
#         try:
#             text = raw.decode("utf-8", errors="ignore")
#         except Exception:
#             text = ""

#     if not text.strip():
#         return {"ok": False, "doc_id": name, "reason": "empty_text", "ctype": ctype, "bytes": len(raw)}

#     chunks = core.ingest_text(name, text)
#     return {"ok": True, "doc_id": name, "chunks": chunks, "ctype": ctype, "bytes": len(raw)}
