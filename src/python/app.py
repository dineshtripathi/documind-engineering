"""
DocuMind Engineering - Hybrid AI Service
FastAPI application for routing between               return InferenceResponse(
            response=f"Mock response to: {request.prompt[:50]}...",
            selected_model="gpt-4o-mini",
            tier="cloud",
            tokens_used=len(request.prompt) // 4,
            cost_usd=0.001,
            response_time_ms=150
        )InferenceResponse(
            response=f"Mock response to: {request.prompt[:50]}...",
            selected_model="gpt-4o-mini",
            tier="cloud",
            tokens_used=len(request.prompt) // 4,
            cost_usd=0.001,
            response_time_ms=150
        )PU and cloud AI models
"""

import os
import logging
import time
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import requests
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DocuMind Hybrid AI Service",
    description="Intelligent routing between local GPU models and Azure AI Foundry",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
class Config:
    AOAI_ENDPOINT = os.getenv("AOAI_ENDPOINT", "https://aoai-documind-weu01.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-06-01")
    AOAI_KEY = os.getenv("AOAI_KEY", "")
    AOAI_DEPLOYMENT = os.getenv("AOAI_DEPLOYMENT", "gpt-4o-mini")
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://search-documind-weu01.search.windows.net")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY", "")  # Set via environment variable
    AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "documind-knowledge")
    OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
    LLAMACPP_ENDPOINT = os.getenv("LLAMACPP_ENDPOINT", "http://localhost:8081")
    GPU_MEMORY_LIMIT = os.getenv("GPU_MEMORY_LIMIT", "24GB")

config = Config()

# Azure Search helper function
def perform_azure_search(query: str, top_k: int = 5):
    """
    Perform Azure AI Search with the given query
    """
    try:
        if not config.AZURE_SEARCH_ENDPOINT or not config.AZURE_SEARCH_KEY:
            logger.warning("Azure Search not configured, using mock results")
            return {
                "documents": [
                    {"title": "Mock Document", "content": f"Mock search result for: {query}", "score": 0.95}
                ]
            }
        
        # Initialize Azure Search client
        search_client = SearchClient(
            endpoint=config.AZURE_SEARCH_ENDPOINT,
            index_name=config.AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(config.AZURE_SEARCH_KEY)
        )
        
        # Perform search
        results = search_client.search(
            search_text=query,
            top=top_k,
            select=["title", "content", "url", "category"],
            highlight_fields="content",
            search_mode="all"  # Use "any" for broader results
        )
        
        # Format results
        documents = []
        for result in results:
            documents.append({
                "title": result.get("title", "Unknown"),
                "content": result.get("content", "No content available"),
                "url": result.get("url", ""),
                "category": result.get("category", ""),
                "score": result.get("@search.score", 0.0),
                "highlights": result.get("@search.highlights", {})
            })
        
        return {"documents": documents}
        
    except Exception as e:
        logger.error(f"Azure Search error: {str(e)}")
        # Fallback to mock results
        return {
            "documents": [
                {"title": "Search Error", "content": f"Search unavailable, using mock result for: {query}", "score": 0.5}
            ]
        }

# Request/Response models
class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.7
    preferred_model: Optional[str] = "auto"  # auto, local, cloud, search
    specialties: Optional[List[str]] = []
    use_search: Optional[bool] = False  # Enable real-time search
    search_query: Optional[str] = None  # Custom search query

class InferenceResponse(BaseModel):
    response: str
    selected_model: str
    tier: str
    tokens_used: int
    cost_usd: float
    response_time_ms: int

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for container"""
    return {
        "status": "healthy",
        "service": "documind-hybrid-ai",
        "version": "1.0.0",
        "azure_configured": bool(config.AOAI_ENDPOINT and config.AOAI_KEY),
        "search_configured": bool(config.AZURE_SEARCH_ENDPOINT and config.AZURE_SEARCH_KEY),
        "local_endpoints": {
            "ollama": config.OLLAMA_ENDPOINT,
            "llamacpp": config.LLAMACPP_ENDPOINT
        }
    }

# Cloud inference endpoint
@app.post("/inference/cloud", response_model=InferenceResponse)
async def cloud_inference(request: InferenceRequest):
    """
    Direct cloud inference using Azure OpenAI GPT-4o-mini
    """
    try:
        if not config.AOAI_ENDPOINT or not config.AOAI_KEY:
            raise HTTPException(status_code=503, detail="Azure OpenAI not configured")
        
        start_time = time.time()
        
        # Prepare Azure OpenAI request
        headers = {
            "Content-Type": "application/json",
            "api-key": config.AOAI_KEY
        }
        
        payload = {
            "messages": [
                {"role": "user", "content": request.prompt}
            ],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }
        
        # Call Azure OpenAI
        response = requests.post(
            config.AOAI_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Azure OpenAI API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=502, detail=f"Azure OpenAI API error: {response.status_code}")
        
        result = response.json()
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract response and token usage
        ai_response = result["choices"][0]["message"]["content"]
        tokens_used = result.get("usage", {}).get("total_tokens", 0)
        
        # Estimate cost (GPT-4o-mini pricing: ~$0.15/1M input tokens, ~$0.60/1M output tokens)
        input_tokens = result.get("usage", {}).get("prompt_tokens", 0)
        output_tokens = result.get("usage", {}).get("completion_tokens", 0)
        cost_usd = (input_tokens * 0.00000015) + (output_tokens * 0.0000006)
        
        return InferenceResponse(
            response=ai_response,
            selected_model=config.AOAI_DEPLOYMENT,
            tier="cloud",
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            response_time_ms=response_time_ms
        )
        
    except requests.RequestException as e:
        logger.error(f"Network error calling Azure OpenAI: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Cloud inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Search-enhanced inference endpoint
@app.post("/inference/search", response_model=InferenceResponse)
async def search_enhanced_inference(request: InferenceRequest):
    """
    Search-enhanced inference using Azure AI Search + Azure OpenAI
    """
    try:
        if not config.AZURE_SEARCH_ENDPOINT or not config.AZURE_SEARCH_KEY:
            raise HTTPException(status_code=503, detail="Azure Search not configured")
        
        start_time = time.time()
        
        # Extract search query from prompt or use custom query
        search_query = request.search_query or request.prompt
        
        # Perform real Azure Search
        search_results = perform_azure_search(search_query, top_k=3)
        
        # Combine search results with prompt
        enhanced_prompt = f"""
Based on the following search results, please answer the user's question:

Search Query: {search_query}

Search Results:
{json.dumps(search_results, indent=2)}

User Question: {request.prompt}

Please provide a comprehensive answer using the search results as context.
"""
        
        # Create new request with enhanced prompt
        enhanced_request = InferenceRequest(
            prompt=enhanced_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            preferred_model="cloud"
        )
        
        # Call cloud inference with enhanced prompt
        result = await cloud_inference(enhanced_request)
        
        # Update response to indicate search was used
        result.selected_model = f"{result.selected_model} + Azure Search"
        result.tier = "search_enhanced"
        
        return result
        
    except Exception as e:
        logger.error(f"Search-enhanced inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Main inference endpoint with hybrid routing
@app.post("/inference", response_model=InferenceResponse)
async def inference(request: InferenceRequest):
    """
    Smart inference routing between local, cloud, and search-enhanced models
    """
    try:
        logger.info(f"Inference request: {request.prompt[:50]}...")
        
        # Determine if search is needed
        search_keywords = ["current", "latest", "recent", "news", "today", "2025", "what happened", "real-time"]
        needs_search = request.use_search or any(keyword in request.prompt.lower() for keyword in search_keywords)
        
        # Route based on preference and need
        if needs_search or request.preferred_model == "search":
            return await search_enhanced_inference(request)
        elif request.preferred_model == "cloud" or request.preferred_model == "auto":
            return await cloud_inference(request)
        else:
            # For demo purposes - return mock local response
            # In production, this would route to Ollama/llama.cpp
            return InferenceResponse(
                response=f"[LOCAL] Mock response to: {request.prompt[:50]}...",
                selected_model="llama3.1:8b",
                tier="local",
                tokens_used=len(request.prompt.split()) + 20,
                cost_usd=0.0,  # Local models have no API cost
                response_time_ms=100
            )
        
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Model status endpoint
@app.get("/models/status")
async def get_model_status():
    """Get status of all available models"""
    return {
        "local_models": {
            "ollama": {
                "endpoint": config.OLLAMA_ENDPOINT,
                "status": "configured",
                "models": ["llama3.1:8b", "phi3.5:3.8b", "deepseek-coder:6.7b"]
            },
            "llamacpp": {
                "endpoint": config.LLAMACPP_ENDPOINT,
                "status": "configured", 
                "models": ["llama-3.1-8b-q4", "phi3-mini-q4"]
            }
        },
        "cloud_models": {
            "azure_openai": {
                "endpoint": config.AOAI_ENDPOINT,
                "deployment": config.AOAI_DEPLOYMENT,
                "status": "configured" if config.AOAI_ENDPOINT and config.AOAI_KEY else "not_configured",
                "models": ["gpt-4o-mini"]
            }
        },
        "search_services": {
            "azure_ai_search": {
                "endpoint": config.AZURE_SEARCH_ENDPOINT,
                "index": config.AZURE_SEARCH_INDEX,
                "status": "configured" if config.AZURE_SEARCH_ENDPOINT and config.AZURE_SEARCH_KEY else "not_configured",
                "capabilities": ["vector_search", "full_text_search", "semantic_search", "real_time_retrieval"]
            }
        },
        "gpu_info": {
            "memory_limit": config.GPU_MEMORY_LIMIT,
            "status": "available"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "DocuMind Hybrid AI Service",
        "description": "Intelligent routing between local GPU models and Azure AI Foundry",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "inference": "/inference",
            "models": "/models/status",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False
    )