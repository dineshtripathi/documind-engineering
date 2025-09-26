# DocuMind Hybrid

**DocuMind Hybrid** is a hybrid AI orchestration stack that combines **local LLMs** (running on RTX 5090 via Ollama) with **Azure AI Foundry** for scalable, secure, and enterprise-ready AI.  
It integrates **.NET 8** (orchestration, APIs, agents) and **Python** (embeddings, data pipelines) into one cohesive system.

---

## 🚀 Key Capabilities

- **Hybrid LLM Orchestration**  
  Local Ollama models (Llama 3.1, Mistral, Phi) for fast inference.  
  Escalation to Azure AI Foundry for complex tasks or large models.

- **RAG (Retrieval-Augmented Generation)**  
  Store and search embeddings using **Qdrant** (local) or **Azure AI Search** (cloud).  
  Answer questions grounded in your documents with citations.

- **Agentic AI (Semantic Kernel)**  
  ReAct, Planner/Executor, and Supervisor patterns.  
  Tools: `files.read`, `vector.search`, `web.fetch`, `camera.capture`, and more.

- **Vision AI**  
  - Local OCR for lightweight tasks.  
  - Azure AI Foundry Vision (GPT-4o, Florence-2) for multimodal reasoning (images, tables, whiteboards, diagrams).

- **.NET + Python Hybrid**  
  - **.NET 8 / ASP.NET Core Minimal API** → Orchestrator + endpoint host  
  - **Python / FastAPI** → Ingestion pipelines, embeddings, CV tasks

---

## 🏗️ Architecture
           ┌─────────────┐
           │  .NET 8 API │   ← Orchestrator (ASP.NET, SK Agents)
           └──────┬──────┘
                  │
         ┌────────▼────────┐
         │   Router Logic  │───► Local Ollama (RTX 5090)
         │  (heuristics)   │───► Azure AI Foundry (LLMs, Vision)
         └────────┬────────┘
                  │
      ┌───────────▼───────────┐
      │    Vector DB (Qdrant) │
      │  (Azure AI Search opt)│
      └───────────┬───────────┘
                  │
       ┌──────────▼──────────────────┐
       │   Python Ingestion          │
       │ (chunk → embed → upsert)    │
       └─────────────────────────────┘

  
---

## ⚙️ Tech Stack

| Layer           | Technology                        | Purpose |
|-----------------|-----------------------------------|---------|
| API/Orchestrator| ASP.NET Core (.NET 8)             | Entry point, query orchestration, routing |
| Agentic AI      | Semantic Kernel (.NET)            | Agents, tools, ReAct, planning |
| LLM Inference   | Ollama (local), Azure AI Foundry  | Hybrid model hosting |
| Vector DB       | Qdrant (local), Azure Cognitive Search | RAG, embeddings |
| Embeddings      | SentenceTransformers (Python), Azure OpenAI | Document encoding |
| Vision AI       | OpenCV + OCR (local), GPT-4o/Florence-2 (Foundry) | Image + text multimodal |
| Ingestion       | Python (FastAPI, Scrapy, BS4)     | Docs, PDFs, feeds |
| Observability   | OpenTelemetry, Serilog            | Monitoring, tracing |
| Security        | Entra ID, Key Vault, guardrails   | Auth, secrets, compliance |

---

## 📂 Repo Layout (planned)


---

## 🔮 Roadmap

- [ ] **M0:** Infra setup (WSL2, .NET 8, Conda, Torch, Ollama, Qdrant)  
- [ ] **M1:** Minimal API `/ask` + ingest pipeline → RAG working end-to-end  
- [ ] **M2:** Vision endpoint `/vision/analyze` with Azure Foundry GPT-4o  
- [ ] **M3:** Router (local vs cloud) + heuristics  
- [ ] **M4:** Agentic workflows (Semantic Kernel + tools)  
- [ ] **M5:** Observability + security hardening (OpenTelemetry, Key Vault)  
- [ ] **M6:** UI (Blazor or React) for uploads + Q&A  

---

## ✨ Status
Early development — infra scripts + orchestration scaffolding in progress.  
Target: usable local RAG assistant with optional cloud escalation (LLM + Vision).  





