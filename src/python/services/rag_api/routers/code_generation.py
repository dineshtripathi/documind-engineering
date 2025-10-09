# services/rag_api/routers/code_generation.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from ..core import core
import requests

router = APIRouter(tags=["code-generation"], prefix="/code")

class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"  # python, csharp, javascript, typescript, java, etc.
    framework: Optional[str] = None  # fastapi, dotnet, react, spring, etc.
    domain: Optional[str] = None  # finance, legal, medical, technical, etc.
    include_tests: bool = False
    include_docs: bool = True
    context_docs: int = 3
    model: Optional[str] = None  # Specific model to use

class CodeGenerationResponse(BaseModel):
    code: str
    language: str
    framework: Optional[str]
    domain: Optional[str]
    explanation: str
    citations: List[Dict]
    confidence: float

@router.post("/generate", response_model=CodeGenerationResponse)
def generate_code(req: CodeGenerationRequest):
    """Generate code based on requirements with domain-aware context retrieval."""

    # Detect domain if not specified
    if not req.domain:
        detected_domain, confidence = core.detect_domain(req.prompt)
        if confidence > 0.3:  # Use detected domain if reasonably confident
            req.domain = detected_domain

    # Select appropriate model for code generation
    if req.model:
        selected_model = req.model
    else:
        selected_model = core.select_model_for_task("code_generation", req.domain or "technical", req.prompt)

    # Build enhanced search query for code generation
    search_terms = [req.prompt]
    if req.language:
        search_terms.append(req.language)
    if req.framework:
        search_terms.append(req.framework)
    if req.domain:
        search_terms.append(req.domain)

    search_query = " ".join(search_terms)

    # Retrieve relevant context
    hits = core.search(search_query, k=core.cfg.topk)
    ranked, scores = core.rerank(search_query, hits)

    # Build code generation prompt
    context_chunks = ranked[:req.context_docs]
    context_text = "\n\n".join([f"Context {i+1}: {chunk['text']}" for i, chunk in enumerate(context_chunks)])

    # Enhanced prompt for code generation
    code_prompt = f"""You are an expert software developer specializing in {req.language}"""
    if req.framework:
        code_prompt += f" with {req.framework} framework"
    if req.domain:
        code_prompt += f" for {req.domain} domain applications"

    code_prompt += f""".

Generate high-quality, production-ready code for the following request:
{req.prompt}

Requirements:
- Language: {req.language}
- Framework: {req.framework or 'standard library'}
- Domain: {req.domain or 'general'}
- Include tests: {req.include_tests}
- Include documentation: {req.include_docs}

Context from knowledge base:
{context_text}

Instructions:
1. Generate clean, well-structured code
2. Follow best practices and conventions for {req.language}
3. Add comprehensive comments and documentation
4. Include error handling where appropriate
5. Make the code production-ready
6. If context mentions specific patterns or libraries, use them
7. Start your response with the actual code in a code block

Generate the code now:"""

    # Generate code using intelligently selected model
    try:
        code_response = requests.post(
            f"{core.cfg.ollama_url}/api/generate",
            json={
                "model": selected_model,  # Use the intelligently selected model
                "prompt": code_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent code
                    "top_p": 0.9,
                    "top_k": 40
                }
            },
            timeout=180
        )

        if code_response.status_code == 200:
            generated_code = code_response.json().get("response", "")
        else:
            raise HTTPException(status_code=500, detail="Code generation failed")

    except Exception as e:
        # Fallback to standard generation with selected model
        generated_code = core._ollama_generate_with_model(code_prompt, selected_model, temperature=0.1)

    if not generated_code or generated_code.strip().lower() == "not found":
        raise HTTPException(status_code=404, detail="Unable to generate code for this request")

    # Calculate confidence based on context relevance
    avg_score = sum(scores[:req.context_docs]) / max(1, len(scores[:req.context_docs]))
    confidence = min(0.95, avg_score * 1.2)  # Cap at 95%

    # Build citations
    citations = []
    for i, (chunk, score) in enumerate(zip(context_chunks, scores[:req.context_docs])):
        citations.append({
            "index": i + 1,
            "doc_id": chunk["doc_id"],
            "chunk_id": chunk["id"],
            "score": float(score),
            "relevance": "high" if score > 0.7 else "medium" if score > 0.4 else "low"
        })

    # Extract code explanation (everything before or after code blocks)
    lines = generated_code.split('\n')
    explanation_lines = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        elif not in_code_block and line.strip() and not line.strip().startswith('#'):
            explanation_lines.append(line)

    explanation = '\n'.join(explanation_lines).strip() or "Generated code based on provided requirements."

    return CodeGenerationResponse(
        code=generated_code,
        language=req.language,
        framework=req.framework,
        domain=req.domain,
        explanation=explanation,
        citations=citations,
        confidence=confidence
    )

@router.post("/explain")
def explain_code(request: dict):
    """Explain existing code with domain-aware context."""

    code = request.get("code", "")
    language = request.get("language", "python")

    if not code:
        raise HTTPException(status_code=400, detail="Code is required")

    # Search for similar code patterns
    search_query = f"explain {language} code pattern function class"
    hits = core.search(search_query, k=6)
    ranked, scores = core.rerank(search_query, hits)

    context_text = "\n\n".join([f"Context: {chunk['text'][:200]}..." for chunk in ranked[:3]])

    explain_prompt = f"""You are an expert code reviewer and educator specializing in {language}.

Analyze and explain the following code:

```{language}
{code}
```

Context from knowledge base:
{context_text}

Provide a comprehensive explanation covering:
1. What the code does (high-level purpose)
2. How it works (step-by-step breakdown)
3. Key patterns and techniques used
4. Best practices demonstrated
5. Potential improvements or concerns
6. Domain-specific considerations if applicable

Explanation:"""

    explanation = core._ollama_generate(explain_prompt, temperature=0.2)

    return {
        "code": code,
        "language": language,
        "explanation": explanation,
        "context_used": len(ranked[:3])
    }

@router.get("/templates")
def get_code_templates():
    """Get available code templates by domain and language."""
    return {
        "domains": list(core.domain_keywords.keys()),
        "languages": ["python", "csharp", "javascript", "typescript", "java", "go", "rust"],
        "frameworks": {
            "python": ["fastapi", "django", "flask", "streamlit"],
            "csharp": ["dotnet", "aspnet", "blazor", "maui"],
            "javascript": ["node", "express", "react", "vue", "angular"],
            "typescript": ["node", "express", "react", "vue", "angular", "nest"],
            "java": ["spring", "springboot", "quarkus"],
            "go": ["gin", "echo", "fiber"],
            "rust": ["actix", "warp", "axum"]
        }
    }

@router.post("/optimize")
def optimize_code(code: str, language: str, optimization_type: str = "performance"):
    """Optimize existing code for performance, readability, or maintainability."""

    search_query = f"{language} optimization best practices {optimization_type}"
    hits = core.search(search_query, k=5)
    ranked, scores = core.rerank(search_query, hits)

    context_text = "\n\n".join([f"Best Practice: {chunk['text'][:150]}..." for chunk in ranked[:2]])

    optimize_prompt = f"""You are an expert {language} developer focused on code optimization.

Optimize the following code for {optimization_type}:

```{language}
{code}
```

Best practices context:
{context_text}

Provide:
1. Optimized version of the code
2. Explanation of changes made
3. Performance/maintainability improvements
4. Any trade-offs involved

Optimized code:"""

    optimized = core._ollama_generate(optimize_prompt, temperature=0.1)

    return {
        "original_code": code,
        "optimized_code": optimized,
        "optimization_type": optimization_type,
        "language": language
    }
