# Latest Technology Update Fetchers
# Add these to your existing crawler system for complete tech coverage

import json
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class TechUpdateFetcher:
    """Enhanced fetcher for latest technology updates via APIs and RSS feeds."""

    async def fetch_pypi_latest_versions(self, packages: List[str] = None) -> List[Dict]:
        """Fetch latest versions from PyPI for popular packages."""
        if not packages:
            packages = [
                'fastapi', 'streamlit', 'django', 'flask', 'pandas',
                'numpy', 'pytorch', 'tensorflow', 'opencv-python'
            ]

        results = []
        for package in packages:
            try:
                response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "source": "PyPI",
                        "package": package,
                        "latest_version": data["info"]["version"],
                        "release_date": data["releases"][data["info"]["version"]][0]["upload_time"],
                        "summary": data["info"]["summary"],
                        "home_page": data["info"]["home_page"]
                    })
            except Exception as e:
                print(f"Error fetching {package}: {e}")

        return results

    async def fetch_dotnet_releases(self) -> List[Dict]:
        """Fetch latest .NET releases from GitHub API."""
        try:
            response = requests.get(
                "https://api.github.com/repos/dotnet/core/releases",
                timeout=10
            )
            if response.status_code == 200:
                releases = response.json()[:5]  # Latest 5 releases
                return [{
                    "source": "GitHub-.NET",
                    "version": release["tag_name"],
                    "release_date": release["published_at"],
                    "title": release["name"],
                    "description": release["body"][:500] + "..." if len(release["body"]) > 500 else release["body"],
                    "url": release["html_url"]
                } for release in releases]
        except Exception as e:
            print(f"Error fetching .NET releases: {e}")
        return []

    async def fetch_azure_updates(self) -> List[Dict]:
        """Fetch Azure service updates from RSS feed."""
        try:
            feed = feedparser.parse("https://azure.microsoft.com/en-us/updates/feed/")
            updates = []
            for entry in feed.entries[:10]:  # Latest 10 updates
                updates.append({
                    "source": "Azure-Updates",
                    "title": entry.title,
                    "published": entry.published,
                    "summary": entry.summary,
                    "link": entry.link,
                    "categories": [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else []
                })
            return updates
        except Exception as e:
            print(f"Error fetching Azure updates: {e}")
        return []

    async def fetch_github_trending(self, language: str = "python") -> List[Dict]:
        """Fetch trending repositories for latest tech insights."""
        try:
            # GitHub search for recently updated repositories
            today = datetime.now()
            week_ago = today - timedelta(days=7)
            date_filter = week_ago.strftime("%Y-%m-%d")

            url = f"https://api.github.com/search/repositories?q=language:{language}+pushed:>{date_filter}&sort=updated&order=desc"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return [{
                    "source": f"GitHub-Trending-{language}",
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "stars": repo["stargazers_count"],
                    "updated_at": repo["updated_at"],
                    "url": repo["html_url"],
                    "topics": repo["topics"]
                } for repo in data["items"][:10]]
        except Exception as e:
            print(f"Error fetching GitHub trending: {e}")
        return []

# Usage in your existing system:
# 1. Add this to your crawler router
# 2. Set up scheduled jobs to run these fetchers daily
# 3. Ingest results into your RAG system automatically

"""
Example Integration:
1. Create endpoint: /crawler/fetch-latest-tech
2. Schedule daily execution via cron or cloud functions
3. Results automatically ingested into Qdrant for RAG queries
"""
