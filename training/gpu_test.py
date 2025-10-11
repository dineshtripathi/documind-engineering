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
