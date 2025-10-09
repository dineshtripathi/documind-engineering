#!/usr/bin/env python3
"""
Web Crawler Demo for DocuMind
Demonstrates crawling Python docs, Stack Overflow, and Microsoft docs
"""
import asyncio
import sys
import os
sys.path.append('/home/dinesh/documind-engineering')

async def demo_crawler_urls():
    """Demo the crawler URL generation without actual crawling."""
    print("🕷️  DocuMind Web Crawler Demo")
    print("=" * 50)

    # Import the crawler classes
    from src.python.services.rag_api.crawlers import (
        PythonDocsCrawler,
        StackOverflowCrawler,
        MicrosoftDocsCrawler,
        CrawlConfig
    )

    print("📋 Target Sites and URLs:")
    print()

    # Python Documentation URLs
    print("🐍 Python Documentation:")
    python_crawler = PythonDocsCrawler()
    python_urls = python_crawler.get_python_docs_urls()[:8]
    for i, url in enumerate(python_urls, 1):
        print(f"  {i:2d}. {url}")

    print()

    # Stack Overflow URLs
    print("📚 Stack Overflow (Python topics):")
    so_crawler = StackOverflowCrawler()
    so_urls = so_crawler.get_python_stackoverflow_urls()[:6]
    for i, url in enumerate(so_urls, 1):
        print(f"  {i:2d}. {url}")

    print()

    # Microsoft Documentation URLs
    print("🏢 Microsoft Documentation:")
    ms_crawler = MicrosoftDocsCrawler()
    ms_urls = ms_crawler.get_microsoft_docs_urls()[:6]
    for i, url in enumerate(ms_urls, 1):
        print(f"  {i:2d}. {url}")

    print()
    print("🔧 Crawler Configuration Options:")
    config = CrawlConfig()
    print(f"  • Max pages per job: {config.max_pages}")
    print(f"  • Delay between requests: {config.delay_seconds}s")
    print(f"  • Max concurrent requests: {config.max_concurrent}")
    print(f"  • Content length limits: {config.min_content_length}-{config.max_content_length} chars")

    print()
    print("🎯 Domain Classification:")
    print("  • Technical: Python docs, Stack Overflow, Microsoft docs")
    print("  • Finance: Bloomberg, Reuters, Investopedia")
    print("  • Medical: PubMed, NIH, medical journals")
    print("  • Legal: Court documents, legal databases")
    print("  • Education: University sites, online courses")

    print()
    print("📊 Integration with Vector Database:")
    print("  1. 🕷️  Crawl websites → Extract content")
    print("  2. 🔍 Domain classification → Categorize content")
    print("  3. 📝 Text chunking → Split into manageable pieces")
    print("  4. 🧮 BGE-M3 embedding → Convert to vectors")
    print("  5. 💾 Qdrant storage → Index in vector database")
    print("  6. 🔎 Enhanced retrieval → Domain-aware search")

if __name__ == "__main__":
    asyncio.run(demo_crawler_urls())
