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
        attn_implementation="eager"  # Use eager attention since flash-attn isn't available
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
