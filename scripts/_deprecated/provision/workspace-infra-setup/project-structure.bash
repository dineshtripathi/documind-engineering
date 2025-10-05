documind-engineering/
├─ README.md
├─ .gitignore
├─ .env.example
├─ infra/
│  ├─ compose.dev.yaml           # Qdrant, (optional) monitoring
│  └─ k8s/                       # later: manifests/helm
├─ scripts/
│  ├─ dev-up.sh                  # bring up Qdrant + services
│  ├─ dev-down.sh
│  ├─ seed-sample.sh             # tiny sample docs
│  └─ smoke-rag.sh               # one-shot smoke for /ask
├─ data/
│  ├─ docs/                      # your domain PDFs/MD/TXT
│  └─ staging/                   # pre-chunked/intermediate
├─ models/                       # (optional) local hf cache
├─ logs/
├─ src/
│  ├─ DocuMind.sln
│  ├─ DocuMind.Host.Api/         # .NET 8 API (orchestrator)
│  │  ├─ Program.cs
│  │  ├─ appsettings.json
│  │  └─ DocuMind.Host.Api.csproj
│  ├─ DocuMind.Common/           # shared contracts/helpers
│  │  └─ DocuMind.Common.csproj
│  └─ python/
│     ├─ services/
│     │  ├─ embedding_service.py # BGE-M3 GPU
│     │  └─ rerank_service.py    # BGE CE GPU
│     ├─ ingest/
│     │  └─ ingest_cli.py        # chunk→embed→upsert (Qdrant)
│     └─ tests/
│        └─ rag_smoketest.py     # in-memory end-to-end test
└─ notebooks/                    # explorations, evals later
