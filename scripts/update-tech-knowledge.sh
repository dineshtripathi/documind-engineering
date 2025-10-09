#!/bin/bash
# Tech Update Automation Script
# Add this to your cron for daily tech updates

# File: scripts/update-tech-knowledge.sh

set -e

echo "🔄 Starting daily tech update ingestion..."

# Activate conda environment
source /home/dinesh/miniconda3/etc/profile.d/conda.sh
conda activate documind

# Change to project directory
cd /home/dinesh/documind-engineering

# Install additional requirements if needed
pip install feedparser requests python-dateutil

# Run tech update fetchers
echo "📦 Fetching PyPI latest versions..."
curl -X POST "http://localhost:7001/crawler/fetch-pypi-updates" \
     -H "Content-Type: application/json" \
     -d '{"packages": ["fastapi", "streamlit", "django", "pandas", "pytorch"]}'

echo "🔶 Fetching .NET releases..."
curl -X POST "http://localhost:7001/crawler/fetch-dotnet-releases"

echo "☁️ Fetching Azure updates..."
curl -X POST "http://localhost:7001/crawler/fetch-azure-updates"

echo "📈 Fetching GitHub trending..."
curl -X POST "http://localhost:7001/crawler/fetch-github-trending" \
     -H "Content-Type: application/json" \
     -d '{"language": "python"}'

echo "✅ Daily tech update completed!"

# Add to crontab with: crontab -e
# 0 6 * * * /home/dinesh/documind-engineering/scripts/update-tech-knowledge.sh > /tmp/tech-update.log 2>&1
