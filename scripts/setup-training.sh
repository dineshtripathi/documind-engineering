#!/bin/bash
# DocuMind Training Environment Setup for RTX 5090
set -e

echo "🚀 Setting up DocuMind Training Environment for RTX 5090..."

# Create training directory structure
mkdir -p /home/dinesh/documind-engineering/training/{local,cloud,data,models,logs}
mkdir -p /home/dinesh/documind-engineering/training/local/{scripts,configs,checkpoints}
mkdir -p /home/dinesh/documind-engineering/training/cloud/{azure,scripts}

echo "📁 Created training directory structure"

# Install training dependencies in conda environment
echo "📦 Installing training dependencies..."
conda run -n documind pip install --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
conda run -n documind pip install --quiet transformers accelerate peft bitsandbytes
conda run -n documind pip install --quiet datasets evaluate wandb tensorboard gradio
conda run -n documind pip install --quiet deepspeed

# Install Flash Attention for memory optimization
echo "⚡ Installing Flash Attention..."
conda run -n documind pip install --quiet flash-attn --no-build-isolation || echo "⚠️  Flash Attention install failed (optional)"

# Azure fine-tuning dependencies
echo "☁️  Installing Azure fine-tuning dependencies..."
conda run -n documind pip install --quiet azure-ai-ml azure-identity

# Create GPU test script
cat > /home/dinesh/documind-engineering/training/gpu_test.py << 'EOF'
"""
RTX 5090 Training Readiness Test
"""
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
import time

def test_gpu_setup():
    print("🔍 Testing RTX 5090 Training Setup...")
    
    # Check CUDA availability
    print(f"✅ CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA Version: {torch.version.cuda}")
        print(f"✅ Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        print(f"✅ Free VRAM: {torch.cuda.memory_reserved(0) / 1e9:.1f} GB")
    
    # Test model loading
    print("\n🧠 Testing Model Loading...")
    try:
        # Load a small model to test
        model_name = "microsoft/phi-3.5-mini-instruct"
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        start_time = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        load_time = time.time() - start_time
        
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        print(f"✅ Model device: {next(model.parameters()).device}")
        print(f"✅ Model dtype: {next(model.parameters()).dtype}")
        
        # Test inference
        inputs = tokenizer("Hello, RTX 5090!", return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=20, do_sample=True, temperature=0.7)
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"✅ Inference test: {response}")
        
        # Memory usage
        print(f"✅ VRAM used: {torch.cuda.memory_allocated(0) / 1e9:.1f} GB")
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
    
    print("\n🎯 RTX 5090 is ready for training!")

if __name__ == "__main__":
    test_gpu_setup()
EOF

# Create LoRA training script template
cat > /home/dinesh/documind-engineering/training/local/lora_training.py << 'EOF'
"""
LoRA Fine-tuning Script for RTX 5090
Optimized for 24GB VRAM
"""
import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset, Dataset
import wandb
import json
from datetime import datetime

def setup_lora_training(
    model_name: str = "microsoft/phi-3.5-mini-instruct",
    dataset_name: str = "tatsu-lab/alpaca",
    output_dir: str = "/home/dinesh/documind-engineering/training/local/checkpoints",
    max_steps: int = 1000,
    learning_rate: float = 2e-4,
    batch_size: int = 4,
    gradient_accumulation_steps: int = 4
):
    """Setup LoRA training optimized for RTX 5090"""
    
    # Initialize wandb
    wandb.init(
        project="documind-training",
        name=f"lora-{model_name.split('/')[-1]}-{datetime.now().strftime('%Y%m%d_%H%M')}",
        config={
            "model": model_name,
            "dataset": dataset_name,
            "method": "lora",
            "gpu": "rtx-5090",
            "vram": "24GB",
            "max_steps": max_steps,
            "learning_rate": learning_rate,
            "batch_size": batch_size
        }
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with optimal settings for RTX 5090
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        max_memory={0: "22GB"},  # Reserve 2GB for system
        trust_remote_code=True,
        use_flash_attention_2=True  # If available
    )
    
    # LoRA configuration optimized for performance
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Load and prepare dataset
    dataset = load_dataset(dataset_name, split="train[:5000]")  # Small subset for testing
    
    def format_instruction(example):
        if "instruction" in example and "output" in example:
            text = f"### Instruction:\n{example['instruction']}\n### Response:\n{example['output']}"
        else:
            text = str(example)
        return {"text": text}
    
    dataset = dataset.map(format_instruction)
    
    def tokenize_function(examples):
        return tokenizer(
            examples["text"], 
            truncation=True, 
            padding=False, 
            max_length=1024
        )
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Training arguments optimized for RTX 5090
    training_args = TrainingArguments(
        output_dir=output_dir,
        max_steps=max_steps,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        weight_decay=0.01,
        logging_steps=10,
        save_steps=250,
        eval_steps=250,
        warmup_steps=100,
        fp16=False,
        bf16=True,  # Better on RTX 5090
        dataloader_num_workers=4,
        remove_unused_columns=False,
        report_to="wandb",
        run_name=f"lora-training-{datetime.now().strftime('%Y%m%d_%H%M')}"
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
        pad_to_multiple_of=8
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    return trainer, model, tokenizer

def main():
    print("🚀 Starting LoRA training on RTX 5090...")
    
    # Setup training
    trainer, model, tokenizer = setup_lora_training(
        model_name="microsoft/phi-3.5-mini-instruct",
        max_steps=500,  # Quick test
        batch_size=2,   # Conservative for safety
        gradient_accumulation_steps=8
    )
    
    # Start training
    print("🏋️  Training started...")
    trainer.train()
    
    # Save model
    output_path = "/home/dinesh/documind-engineering/training/local/models/phi3-lora-documind"
    trainer.save_model(output_path)
    tokenizer.save_pretrained(output_path)
    
    print(f"✅ Training completed! Model saved to {output_path}")
    
    # Test the trained model
    print("🧪 Testing trained model...")
    inputs = tokenizer("How can I improve document analysis?", return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7, do_sample=True)
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Model response: {response}")

if __name__ == "__main__":
    main()
EOF

# Create Azure fine-tuning script
cat > /home/dinesh/documind-engineering/training/cloud/azure_finetuning.py << 'EOF'
"""
Azure OpenAI Fine-tuning Script
"""
import openai
from azure.identity import DefaultAzureCredential
import json
import time
import os

def setup_azure_openai():
    """Setup Azure OpenAI client"""
    openai.api_type = "azure"
    openai.api_base = os.getenv("AOAI_ENDPOINT", "").replace("/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-06-01", "")
    openai.api_key = os.getenv("AOAI_KEY")
    openai.api_version = "2024-06-01"

def prepare_training_data(data_path: str, output_path: str):
    """Prepare data in Azure OpenAI format"""
    # Example: Convert your data to JSONL format
    training_data = []
    
    # Sample data structure
    samples = [
        {
            "messages": [
                {"role": "system", "content": "You are a helpful DocuMind assistant specialized in document analysis."},
                {"role": "user", "content": "How do I extract key insights from a PDF document?"},
                {"role": "assistant", "content": "To extract key insights from a PDF document, I recommend following these steps: 1. Use OCR if needed, 2. Identify document structure, 3. Extract entities and relationships, 4. Summarize key findings..."}
            ]
        }
    ]
    
    with open(output_path, 'w') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')
    
    print(f"Training data prepared: {output_path}")

def start_azure_finetuning(training_file_path: str):
    """Start Azure OpenAI fine-tuning job"""
    setup_azure_openai()
    
    # Upload training file
    with open(training_file_path, 'rb') as f:
        training_file = openai.File.create(
            file=f,
            purpose='fine-tune'
        )
    
    print(f"Training file uploaded: {training_file.id}")
    
    # Create fine-tuning job
    fine_tuning_job = openai.FineTuningJob.create(
        training_file=training_file.id,
        model="gpt-4o-mini",
        hyperparameters={
            "n_epochs": 3,
            "batch_size": 1,
            "learning_rate_multiplier": 0.1
        }
    )
    
    print(f"Fine-tuning job created: {fine_tuning_job.id}")
    return fine_tuning_job.id

def monitor_finetuning(job_id: str):
    """Monitor fine-tuning progress"""
    setup_azure_openai()
    
    while True:
        job = openai.FineTuningJob.retrieve(job_id)
        print(f"Status: {job.status}")
        
        if job.status in ["succeeded", "failed", "cancelled"]:
            break
        
        time.sleep(60)  # Check every minute
    
    if job.status == "succeeded":
        print(f"✅ Fine-tuning completed! Model: {job.fine_tuned_model}")
    else:
        print(f"❌ Fine-tuning failed: {job.status}")

if __name__ == "__main__":
    # Prepare sample data
    prepare_training_data("", "/tmp/training_data.jsonl")
    
    # Start fine-tuning
    job_id = start_azure_finetuning("/tmp/training_data.jsonl")
    
    # Monitor progress
    monitor_finetuning(job_id)
EOF

# Make scripts executable
chmod +x /home/dinesh/documind-engineering/training/gpu_test.py
chmod +x /home/dinesh/documind-engineering/training/local/lora_training.py
chmod +x /home/dinesh/documind-engineering/training/cloud/azure_finetuning.py

echo "✅ Training environment setup complete!"
echo ""
echo "🎯 Next Steps:"
echo "1. Test GPU setup: cd training && python gpu_test.py"
echo "2. Run LoRA training: cd training/local && python lora_training.py"  
echo "3. Azure fine-tuning: cd training/cloud && python azure_finetuning.py"
echo ""
echo "📚 Training guides available in:"
echo "   - .azure/training-strategy.md"
echo "   - training/ directory"