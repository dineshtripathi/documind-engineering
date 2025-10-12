# DocuMind Engineering

🚀 **Hybrid AI Platform** for intelligent document processing combining local GPU training with Azure cloud services.

## 🏗️ Architecture

### Hybrid Computing Model
```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Local GPU         │    │   Smart Router       │    │   Azure Cloud       │
│   RTX 5090 24GB     │◄──►│   Cost Optimizer     │◄──►│   OpenAI + Search   │
│   LoRA Training     │    │   Model Selector     │    │   Production Scale  │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### System Design
- **3-Tier Architecture**: Local training → Smart routing → Cloud inference
- **Cost Optimization**: Automatic local/cloud selection based on task complexity
- **Scalability**: Local development to cloud production seamless transition
- **Privacy Control**: Sensitive training data stays local, inference scales globally

## 🛠️ Tech Stack

### Core Technologies
- **Backend**: FastAPI (Python) - High-performance async API
- **AI Framework**: PyTorch + Transformers + PEFT (LoRA fine-tuning)
- **Cloud Services**: Azure OpenAI + Azure AI Search
- **Infrastructure**: Manual Azure resource provisioning
- **Containerization**: Docker for flexible deployment

### AI/ML Stack
- **Local Training**: PEFT (Parameter-Efficient Fine-Tuning)
- **Model Format**: GGUF (quantized models for inference)
- **Training Optimization**: LoRA/QLoRA for memory efficiency
- **Experiment Tracking**: Weights & Biases integration

## 🤖 Models Used

### Local Models (RTX 5090)
- **Phi-3.5 Mini Instruct** (3.8B parameters) - Fast training, good performance
- **Llama 3.1 8B Instruct** - Balanced capability and resource usage
- **Custom LoRA Adapters** - Domain-specific fine-tuned models

### Cloud Models (Azure OpenAI)
- **GPT-4o Mini** - Production inference with cost optimization
- **Custom Fine-tuned Models** - Azure OpenAI fine-tuning pipeline

## 🔄 Workflow

### Development Workflow
1. **Local Training**: Fine-tune models on RTX 5090 with proprietary data
2. **Validation**: Test model performance and accuracy locally
3. **Deployment**: Deploy to Azure for production scaling
4. **Monitoring**: Track performance, costs, and model drift

### Training Pipeline
```
Data Preparation → LoRA Configuration → GPU Training → Model Validation → Deployment
```

### Inference Pipeline
```
User Request → Smart Router → Model Selection → Response Generation → Cost Tracking
```

## 🐍 Python Use Case

### Why Python
- **AI/ML Ecosystem**: Native support for PyTorch, Transformers, PEFT
- **Rapid Development**: FastAPI for quick API development and iteration
- **Azure Integration**: Comprehensive SDKs for all Azure services
- **Community**: Extensive libraries for AI/ML and data processing

### Python Components
- **FastAPI Service**: Main API gateway with hybrid routing logic
- **Training Scripts**: Local GPU training with LoRA fine-tuning
- **Data Processing**: Document parsing and preparation pipelines
- **Model Management**: Automated model loading and optimization

## 🔷 .NET Use Case

### Why .NET (Future Integration)
- **Enterprise Integration**: Seamless integration with existing enterprise systems
- **Performance**: High-throughput document processing workflows
- **Security**: Enterprise-grade authentication and authorization
- **Ecosystem**: Rich libraries for document formats (PDF, Word, Excel)

### Planned .NET Components
- **Document Processing API**: High-performance document parsing and analysis
- **Enterprise Gateway**: Authentication, rate limiting, and enterprise features
- **Workflow Orchestration**: Complex document processing pipelines
- **Legacy System Integration**: Connect with existing enterprise document systems

## 🎯 Key Features

### Performance Metrics
- **Local Training**: ~35 minutes for Llama 8B LoRA fine-tuning
- **Cost Efficiency**: ~$1.50 per training session vs cloud alternatives
- **Memory Optimization**: 24GB VRAM utilization with gradient accumulation
- **Inference Speed**: Sub-second response times with smart caching

### Production Capabilities
- **Auto-scaling**: Azure Container Apps for demand-based scaling
- **Monitoring**: Built-in health checks and performance tracking
- **Security**: Azure Key Vault integration for secrets management
- **Multi-model**: Support for multiple model formats and providers

## 🚀 Getting Started

```bash
# Install dependencies
cd src/python && pip install -r requirements.txt

# Set up environment
export AOAI_ENDPOINT="your-azure-endpoint"
export AOAI_KEY="your-api-key"

# Start the service
python app.py

# Test GPU training
cd ../../training && python quick_training_test.py
```

---

**Enterprise-ready hybrid AI platform optimized for document intelligence and custom model training.**