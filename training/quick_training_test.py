#!/usr/bin/env python3
"""
Quick LoRA Training Test for RTX 5090
Tests GPU training capabilities with minimal setup
"""

import torch
import torch.nn as nn
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
import os

def test_rtx5090_training():
    """Quick test to validate RTX 5090 training setup"""
    print("🚀 Quick RTX 5090 Training Test")
    print(f"✅ CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA Version: {torch.version.cuda}")
        print(f"✅ Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print(f"✅ Free VRAM: {torch.cuda.memory_reserved(0) / 1024**3:.1f} GB")
    
    # Use a smaller, faster model for testing
    model_name = "microsoft/DialoGPT-small"  # Much smaller for quick testing
    print(f"\n🧠 Loading model: {model_name}")
    
    try:
        start_time = time.time()
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Setup LoRA
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["c_attn"],  # DialoGPT specific
            lora_dropout=0.1,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        model = get_peft_model(model, lora_config)
        print(f"✅ LoRA configuration applied")
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        print(f"✅ Trainable parameters: {trainable_params:,} / {total_params:,} ({100 * trainable_params / total_params:.2f}%)")
        
        # Test forward pass
        test_input = tokenizer("Hello, how are you?", return_tensors="pt")
        if torch.cuda.is_available():
            test_input = {k: v.cuda() for k, v in test_input.items()}
        
        with torch.no_grad():
            outputs = model(**test_input)
            print(f"✅ Forward pass successful: Output shape {outputs.logits.shape}")
        
        # Test gradient computation
        print("\n🔥 Testing gradient computation...")
        model.train()
        
        # Create dummy training data
        batch_size = 4
        seq_length = 32
        
        dummy_input_ids = torch.randint(0, tokenizer.vocab_size, (batch_size, seq_length))
        dummy_labels = dummy_input_ids.clone()
        
        if torch.cuda.is_available():
            dummy_input_ids = dummy_input_ids.cuda()
            dummy_labels = dummy_labels.cuda()
        
        # Forward pass with loss
        outputs = model(input_ids=dummy_input_ids, labels=dummy_labels)
        loss = outputs.loss
        print(f"✅ Loss computed: {loss.item():.4f}")
        
        # Backward pass
        loss.backward()
        print(f"✅ Backward pass successful")
        
        # Check GPU memory usage
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated(0) / 1024**3
            memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
            print(f"✅ GPU Memory Used: {memory_used:.2f} GB")
            print(f"✅ GPU Memory Reserved: {memory_reserved:.2f} GB")
        
        print(f"\n🎯 RTX 5090 Training Test: SUCCESS!")
        print(f"🚀 Ready for full LoRA training on larger models")
        
        return True
        
    except Exception as e:
        print(f"❌ Training test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_rtx5090_training()
    if success:
        print("\n✅ RTX 5090 is ready for AI training!")
        print("💡 Next steps:")
        print("  - Run full LoRA training with Phi-3.5 or Llama models")
        print("  - Experiment with different LoRA ranks and learning rates")
        print("  - Use the 24GB VRAM for larger batch sizes")
    else:
        print("\n❌ RTX 5090 training setup needs fixing")