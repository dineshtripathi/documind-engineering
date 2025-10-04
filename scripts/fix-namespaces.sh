#!/bin/bash
# Automatic namespace fixer script

echo "🔧 Fixing namespaces automatically..."

# Function to replace namespace in files
fix_namespace() {
    local old_namespace="$1"
    local new_namespace="$2"
    local file_pattern="$3"
    
    echo "Replacing '$old_namespace' with '$new_namespace' in $file_pattern files..."
    
    find . -name "$file_pattern" -type f -exec sed -i "s|$old_namespace|$new_namespace|g" {} \;
}

# Navigate to the dotnet source directory
cd "$(dirname "$0")/../src/dotnet"

# Fix common namespace issues
fix_namespace "DocuMind.Api.Models" "Documind.Contracts" "*.cs"
fix_namespace "DocuMind.Contracts.Contracts" "Documind.Contracts" "*.cs"

# Run dotnet format to organize usings
echo "🔧 Running dotnet format to organize imports..."
dotnet format DocuMind.Api.sln --include src/ --verbosity normal

# Build to check for errors
echo "🔨 Building solution..."
dotnet build DocuMind.Api.sln

echo "✅ Namespace fix complete!"