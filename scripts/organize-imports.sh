#!/bin/bash
# Quick script to organize imports and format code

echo "🔧 Organizing imports and formatting code..."

# Navigate to solution directory
cd "$(dirname "$0")/../src/dotnet"

# Format the solution
dotnet format DocuMind.Api.sln --verbosity minimal

echo "✅ Done! Imports organized and code formatted."
