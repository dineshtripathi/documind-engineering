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
