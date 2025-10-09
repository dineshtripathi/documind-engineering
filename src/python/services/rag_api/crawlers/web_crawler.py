# services/rag_api/crawlers/web_crawler.py
import asyncio
import aiohttp
import time
import re
import json
from urllib.parse import urljoin, urlparse, quote_plus
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

@dataclass
class CrawlConfig:
    max_pages: int = 50
    delay_seconds: float = 1.0
    max_concurrent: int = 5
    timeout_seconds: int = 30
    user_agent: str = "DocuMind-Crawler/1.0"

    # Content filtering
    min_content_length: int = 100
    max_content_length: int = 50000
    allowed_content_types: Optional[List[str]] = None

    def __post_init__(self):
        if self.allowed_content_types is None:
            self.allowed_content_types = ["text/html", "text/plain"]

@dataclass
class CrawledDocument:
    url: str
    title: str
    content: str
    domain: str
    metadata: Dict
    timestamp: float
    content_type: str

class WebCrawler:
    def __init__(self, config: Optional[CrawlConfig] = None):
        self.config = config or CrawlConfig()
        self.visited_urls: Set[str] = set()
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.config.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        headers = {"User-Agent": self.config.user_agent}

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove common navigation elements
        text = re.sub(r'(Skip to|Navigation|Breadcrumb|Cookie policy|Privacy policy)', '', text, flags=re.IGNORECASE)
        return text

    def _extract_content(self, html: str, url: str) -> Tuple[str, str]:
        """Extract title and main content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text() if title_tag else urlparse(url).path

        # Priority content selectors for different sites
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '#content',
            '.documentation',
            '.doc-content'
        ]

        content = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                content = content_element.get_text()
                break

        # Fallback to body if no specific content found
        if not content:
            body = soup.find('body')
            content = body.get_text() if body else soup.get_text()

        # Clean the content
        content = self._clean_text(content)
        title = self._clean_text(title)

        return title, content

    async def _fetch_page(self, url: str) -> Optional[CrawledDocument]:
        """Fetch and parse a single page."""
        if url in self.visited_urls or len(self.visited_urls) >= self.config.max_pages:
            return None

        try:
            self.visited_urls.add(url)
            logger.info(f"Fetching: {url}")

            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")

            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status}")
                    return None

                content_type = response.headers.get('content-type', '').lower()
                allowed_types = self.config.allowed_content_types or ["text/html", "text/plain"]
                if not any(ct in content_type for ct in allowed_types):
                    logger.info(f"Skipping {url}: unsupported content type {content_type}")
                    return None

                html = await response.text()
                title, content = self._extract_content(html, url)

                if len(content) < self.config.min_content_length:
                    logger.info(f"Skipping {url}: content too short ({len(content)} chars)")
                    return None

                if len(content) > self.config.max_content_length:
                    content = content[:self.config.max_content_length] + "..."

                # Determine domain/category based on URL
                domain = self._classify_domain(url, content)

                return CrawledDocument(
                    url=url,
                    title=title,
                    content=content,
                    domain=domain,
                    metadata={
                        "content_length": len(content),
                        "status_code": response.status,
                        "content_type": content_type
                    },
                    timestamp=time.time(),
                    content_type=content_type
                )

        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _classify_domain(self, url: str, content: str) -> str:
        """Classify content domain based on URL and content."""
        url_lower = url.lower()
        content_lower = content.lower()

        # Technical domains
        if any(term in url_lower for term in ['docs.python.org', 'stackoverflow.com', 'docs.microsoft.com', 'github.com']):
            return "technical"

        # Financial domains
        if any(term in url_lower for term in ['finance', 'bloomberg', 'reuters', 'investopedia']):
            return "finance"

        # Medical domains
        if any(term in url_lower for term in ['pubmed', 'nih.gov', 'medical', 'health']):
            return "medical"

        # Educational domains
        if any(term in url_lower for term in ['.edu', 'coursera', 'edx', 'khan']):
            return "education"

        # Legal domains
        if any(term in url_lower for term in ['law', 'legal', 'court', 'justice']):
            return "legal"

        # Content-based classification
        tech_keywords = ['python', 'javascript', 'api', 'framework', 'programming', 'software', 'code']
        if sum(1 for keyword in tech_keywords if keyword in content_lower) >= 3:
            return "technical"

        return "general"

    async def crawl_urls(self, urls: List[str]) -> List[CrawledDocument]:
        """Crawl a list of URLs and return documents."""
        documents = []
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def crawl_with_delay(url: str) -> Optional[CrawledDocument]:
            async with semaphore:
                doc = await self._fetch_page(url)
                await asyncio.sleep(self.config.delay_seconds)
                return doc

        tasks = [crawl_with_delay(url) for url in urls if url not in self.visited_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, CrawledDocument):
                documents.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Crawl task failed: {result}")

        return documents

class PythonDocsCrawler(WebCrawler):
    """Specialized crawler for Python documentation."""

    def get_python_docs_urls(self) -> List[str]:
        """Get a comprehensive list of Python documentation URLs."""
        base_urls = [
            # Core Python docs
            "https://docs.python.org/3/tutorial/",
            "https://docs.python.org/3/library/",
            "https://docs.python.org/3/reference/",
            "https://docs.python.org/3/howto/",

            # Popular Python libraries
            "https://fastapi.tiangolo.com/",
            "https://flask.palletsprojects.com/",
            "https://docs.djangoproject.com/",
            "https://pandas.pydata.org/docs/",
            "https://numpy.org/doc/",
            "https://scikit-learn.org/stable/",
            "https://pytorch.org/docs/",
            "https://tensorflow.org/guide/",

            # Python Package Index popular packages
            "https://requests.readthedocs.io/",
            "https://sqlalchemy.org/",
            "https://pydantic-docs.helpmanual.io/",
        ]

        # Expand to include sub-pages (simplified for demo)
        expanded_urls = []
        for base_url in base_urls:
            expanded_urls.append(base_url)
            # Add common sub-paths
            if base_url.endswith('/'):
                common_paths = ['quickstart/', 'tutorial/', 'guide/', 'api/', 'examples/']
                for path in common_paths:
                    expanded_urls.append(f"{base_url}{path}")

        return expanded_urls

class StackOverflowCrawler(WebCrawler):
    """Specialized crawler for Stack Overflow."""

    def get_stackoverflow_search_urls(self, tags: List[str], pages: int = 5) -> List[str]:
        """Generate Stack Overflow search URLs for specific tags."""
        urls = []
        for tag in tags:
            for page in range(1, pages + 1):
                # High-quality questions with good scores
                url = f"https://stackoverflow.com/questions/tagged/{tag}?tab=votes&page={page}"
                urls.append(url)
        return urls

    def get_python_stackoverflow_urls(self) -> List[str]:
        """Get Stack Overflow URLs for Python-related content."""
        python_tags = [
            'python', 'fastapi', 'django', 'flask', 'pandas',
            'numpy', 'machine-learning', 'data-science', 'async-await',
            'sqlalchemy', 'pydantic', 'pytest', 'docker', 'kubernetes'
        ]
        return self.get_stackoverflow_search_urls(python_tags, pages=3)

class MicrosoftDocsCrawler(WebCrawler):
    """Specialized crawler for Microsoft documentation."""

    def get_microsoft_docs_urls(self) -> List[str]:
        """Get Microsoft documentation URLs."""
        return [
            # .NET Core and C#
            "https://docs.microsoft.com/en-us/dotnet/",
            "https://docs.microsoft.com/en-us/aspnet/core/",
            "https://docs.microsoft.com/en-us/dotnet/csharp/",
            "https://docs.microsoft.com/en-us/dotnet/api/",

            # Azure
            "https://docs.microsoft.com/en-us/azure/",
            "https://docs.microsoft.com/en-us/azure/app-service/",
            "https://docs.microsoft.com/en-us/azure/functions/",
            "https://docs.microsoft.com/en-us/azure/cognitive-services/",
            "https://docs.microsoft.com/en-us/azure/container-instances/",
            "https://docs.microsoft.com/en-us/azure/aks/",

            # Visual Studio and Dev Tools
            "https://docs.microsoft.com/en-us/visualstudio/",
            "https://code.visualstudio.com/docs/",
        ]
