# Enhanced AskOrchestrator Implementation

## Overview

The Enhanced AskOrchestrator now features intelligent query analysis and confidence-based routing, implementing two key enhancements:

### 1. QueryAnalyzer Service
- **Complexity Analysis**: Classifies queries as Simple/Moderate/Complex/Specialized
- **Domain Detection**: Identifies Technical, Legal, Medical, Financial, Code, Creative, Research domains
- **Intent Recognition**: Determines Question, Explanation, Summary, Analysis, Generation, Translation, Extraction
- **Intelligent Routing**: Recommends optimal route (local/cloud/hybrid) based on analysis
- **Cost & Latency Estimation**: Provides performance predictions

### 2. ConfidenceScorer Service
- **Citation Quality**: Validates references and detects hallucinations
- **Response Quality**: Assesses coherence, relevance, completeness, accuracy
- **Context Relevance**: Evaluates how well context matches the query
- **Escalation Logic**: Automatically escalates low-confidence responses

## Usage Examples

### Simple Query (Local Route)
```
Query: "What is the company name?"
Analysis: Simple/General/Question -> Local (confidence: 0.6)
Response: Fast local RAG lookup
```

### Complex Analysis (Cloud Route)
```
Query: "Analyze the legal implications of this contract clause regarding liability limitations"
Analysis: Complex/Legal/Analysis -> Cloud (confidence: 0.85)
Response: Direct to Azure OpenAI for advanced reasoning
```

### Document Extraction (Local Route)
```
Query: "Extract all financial data from quarterly reports"
Analysis: Moderate/Financial/Extraction -> Local (confidence: 0.7)
Response: Local RAG with document retrieval
```

### Confidence-Based Escalation
```
1. Query processed locally
2. ConfidenceScorer evaluates response quality
3. If confidence < threshold: automatically escalate to cloud
4. Return best available response
```

## Key Features

### Intelligent Query Analysis
- **Multi-dimensional Classification**: Complexity + Domain + Intent
- **Keyword-based Detection**: Technical terms, domain indicators
- **Pattern Recognition**: Question types, instruction patterns
- **Cost Optimization**: Route to most cost-effective model

### Advanced Confidence Scoring
- **Citation Validation**: Ensures references are within context range
- **Hallucination Detection**: Identifies AI-generated false information
- **Quality Metrics**: Coherence, relevance, completeness assessment
- **Context Alignment**: Measures query-context relevance

### Adaptive Routing Logic
- **Legacy Compatibility**: Respects existing FeatureFlags
- **Intelligent Defaults**: Smart routing when flags disabled
- **Escalation Support**: Automatic cloud fallback for low confidence
- **Performance Tracking**: Latency and cost monitoring

## Configuration

The services are registered in `Program.cs`:
```csharp
builder.Services.AddScoped<IQueryAnalyzer, QueryAnalyzer>();
builder.Services.AddScoped<IConfidenceScorer, ConfidenceScorer>();
```

## Benefits

1. **Cost Optimization**: Route simple queries to local RAG, complex to cloud
2. **Quality Assurance**: Confidence scoring prevents low-quality responses
3. **Performance**: Intelligent routing reduces latency for appropriate queries
4. **Reliability**: Automatic escalation ensures backup coverage
5. **Observability**: Detailed logging and metrics for analysis

## Architecture Flow

```
Query → QueryAnalyzer → Route Decision → Execute → ConfidenceScorer → Escalate? → Response
```

This implementation provides sophisticated AI orchestration while maintaining backward compatibility with existing feature flags and configuration.
