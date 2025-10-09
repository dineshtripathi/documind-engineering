# services/rag_api/routers/crawler.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import logging
from ..core import core
from ..crawlers import WebCrawler, PythonDocsCrawler, StackOverflowCrawler, MicrosoftDocsCrawler, CrawlConfig

router = APIRouter(prefix="/crawler", tags=["web-crawler"])
logger = logging.getLogger(__name__)

# Global state for tracking crawl jobs
crawl_jobs: Dict[str, Dict] = {}

class CrawlRequest(BaseModel):
    urls: List[str]
    max_pages: int = 20
    delay_seconds: float = 1.0
    domain_hint: Optional[str] = None
    job_id: Optional[str] = None

class CrawlJobStatus(BaseModel):
    job_id: str
    status: str  # "running", "completed", "failed"
    total_urls: int
    processed_urls: int
    ingested_docs: int
    started_at: float
    completed_at: Optional[float] = None
    error_message: Optional[str] = None

class CrawlResponse(BaseModel):
    job_id: str
    status: str
    message: str

async def crawl_and_ingest(job_id: str, urls: List[str], config: CrawlConfig, domain_hint: Optional[str] = None):
    """Background task to crawl URLs and ingest into vector database."""
    import time
    import uuid

    try:
        crawl_jobs[job_id]["status"] = "running"
        crawl_jobs[job_id]["started_at"] = time.time()

        async with WebCrawler(config) as crawler:
            documents = await crawler.crawl_urls(urls)

            # Ingest documents into vector database
            ingested_count = 0
            for doc in documents:
                try:
                    # Use domain hint or detected domain
                    doc_domain = domain_hint or doc.domain

                    # Create enhanced document text with metadata
                    enhanced_content = f"""
Title: {doc.title}
URL: {doc.url}
Domain: {doc_domain}
Content Type: {doc.content_type}

{doc.content}

Metadata: {doc.metadata}
"""

                    # Generate unique doc_id
                    doc_id = f"web_{doc_domain}_{hash(doc.url) % 1000000}"

                    # Ingest into vector database
                    chunks = core.ingest_text(doc_id, enhanced_content)
                    if chunks > 0:
                        ingested_count += 1
                        logger.info(f"Ingested {chunks} chunks from {doc.url}")

                except Exception as e:
                    logger.error(f"Failed to ingest {doc.url}: {e}")

            # Update job status
            crawl_jobs[job_id].update({
                "status": "completed",
                "processed_urls": len(documents),
                "ingested_docs": ingested_count,
                "completed_at": time.time()
            })

        logger.info(f"Crawl job {job_id} completed: {ingested_count} documents ingested")

    except Exception as e:
        logger.error(f"Crawl job {job_id} failed: {e}")
        crawl_jobs[job_id].update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": time.time()
        })

@router.post("/crawl", response_model=CrawlResponse)
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Start a web crawling job."""
    import uuid
    import time

    job_id = request.job_id or str(uuid.uuid4())

    if job_id in crawl_jobs:
        raise HTTPException(status_code=400, detail=f"Job {job_id} already exists")

    # Initialize job status
    crawl_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "total_urls": len(request.urls),
        "processed_urls": 0,
        "ingested_docs": 0,
        "started_at": 0,
        "completed_at": None,
        "error_message": None
    }

    # Create crawl configuration
    config = CrawlConfig(
        max_pages=request.max_pages,
        delay_seconds=request.delay_seconds,
        max_concurrent=3  # Conservative for public sites
    )

    # Start background crawling task
    background_tasks.add_task(
        crawl_and_ingest,
        job_id,
        request.urls,
        config,
        request.domain_hint
    )

    return CrawlResponse(
        job_id=job_id,
        status="queued",
        message=f"Crawl job started for {len(request.urls)} URLs"
    )

@router.get("/status/{job_id}", response_model=CrawlJobStatus)
async def get_crawl_status(job_id: str):
    """Get the status of a crawl job."""
    if job_id not in crawl_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job_data = crawl_jobs[job_id]
    return CrawlJobStatus(**job_data)

@router.get("/jobs", response_model=List[CrawlJobStatus])
async def list_crawl_jobs():
    """List all crawl jobs."""
    return [CrawlJobStatus(**job_data) for job_data in crawl_jobs.values()]

@router.post("/python-docs", response_model=CrawlResponse)
async def crawl_python_docs(background_tasks: BackgroundTasks, max_pages: int = 30):
    """Crawl Python documentation sites."""
    import uuid

    job_id = f"python_docs_{uuid.uuid4().hex[:8]}"

    crawler = PythonDocsCrawler()
    urls = crawler.get_python_docs_urls()[:max_pages]  # Limit URLs

    request = CrawlRequest(
        urls=urls,
        max_pages=max_pages,
        delay_seconds=1.5,  # Be respectful to Python docs
        domain_hint="technical",
        job_id=job_id
    )

    return await start_crawl(request, background_tasks)

@router.post("/stackoverflow", response_model=CrawlResponse)
async def crawl_stackoverflow(background_tasks: BackgroundTasks, max_pages: int = 20):
    """Crawl Stack Overflow for Python-related content."""
    import uuid

    job_id = f"stackoverflow_{uuid.uuid4().hex[:8]}"

    crawler = StackOverflowCrawler()
    urls = crawler.get_python_stackoverflow_urls()[:max_pages]  # Limit URLs

    request = CrawlRequest(
        urls=urls,
        max_pages=max_pages,
        delay_seconds=2.0,  # Be respectful to Stack Overflow
        domain_hint="technical",
        job_id=job_id
    )

    return await start_crawl(request, background_tasks)

@router.post("/microsoft-docs", response_model=CrawlResponse)
async def crawl_microsoft_docs(background_tasks: BackgroundTasks, max_pages: int = 25):
    """Crawl Microsoft documentation."""
    import uuid

    job_id = f"microsoft_docs_{uuid.uuid4().hex[:8]}"

    crawler = MicrosoftDocsCrawler()
    urls = crawler.get_microsoft_docs_urls()[:max_pages]  # Limit URLs

    request = CrawlRequest(
        urls=urls,
        max_pages=max_pages,
        delay_seconds=1.0,
        domain_hint="technical",
        job_id=job_id
    )

    return await start_crawl(request, background_tasks)

@router.delete("/jobs/{job_id}")
async def delete_crawl_job(job_id: str):
    """Delete a crawl job from memory."""
    if job_id not in crawl_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    del crawl_jobs[job_id]
    return {"message": f"Job {job_id} deleted"}

@router.get("/stats")
async def get_crawler_stats():
    """Get crawler statistics."""
    total_jobs = len(crawl_jobs)
    running_jobs = sum(1 for job in crawl_jobs.values() if job["status"] == "running")
    completed_jobs = sum(1 for job in crawl_jobs.values() if job["status"] == "completed")
    failed_jobs = sum(1 for job in crawl_jobs.values() if job["status"] == "failed")
    total_ingested = sum(job["ingested_docs"] for job in crawl_jobs.values())

    return {
        "total_jobs": total_jobs,
        "running_jobs": running_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "total_documents_ingested": total_ingested,
        "vector_db_collection": core.cfg.collection
    }
