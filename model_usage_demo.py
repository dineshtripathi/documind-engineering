#!/usr/bin/env python3
"""
DocuMind Model Usage Demo
Shows how different models are used for different tasks
"""
import requests
import json

def test_api_endpoint(endpoint, data, description):
    """Test an API endpoint and display results."""
    print(f"\n🔧 {description}")
    print("=" * 60)

    try:
        response = requests.post(f"http://localhost:7001{endpoint}",
                               json=data, headers={"Content-Type": "application/json"}, timeout=30)

        if response.status_code == 200:
            result = response.json()

            # Display model used if available
            if "model_used" in result:
                print(f"🤖 Model Used: {result['model_used']}")
            if "detected_domain" in result:
                print(f"🎯 Domain: {result['detected_domain']} (confidence: {result.get('domain_confidence', 0):.2f})")
            if "task_type" in result:
                print(f"📋 Task Type: {result['task_type']}")

            # Display answer/code
            if "answer" in result:
                print(f"💬 Answer: {result['answer'][:300]}...")
            elif "code" in result:
                print(f"💻 Generated Code:\n{result['code'][:500]}...")

            print(f"✅ Status: Success")
        else:
            print(f"❌ Status: Failed ({response.status_code})")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 DocuMind Model Usage Demonstration")
    print("=" * 60)

    # Check health and available models
    try:
        health = requests.get("http://localhost:7001/healthz").json()
        print("📊 System Status:")
        print(f"   • Device: {health.get('device', 'N/A')}")
        print(f"   • Default Model: {health.get('ollama_model', 'N/A')}")
        print(f"   • Domain Detection: {health.get('domain_detection', False)}")

        specialized = health.get('specialized_models', {})
        if specialized:
            print("🎯 Specialized Models:")
            for task, model in specialized.items():
                print(f"   • {task}: {model}")

        available = health.get('available_models', [])
        print(f"📦 Available Models ({len(available)}):")
        for model in available[:6]:  # Show first 6
            print(f"   • {model}")
        if len(available) > 6:
            print(f"   ... and {len(available) - 6} more")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return

    # Test 1: General Q&A (should use phi3.5)
    test_api_endpoint("/ask", {
        "q": "What is machine learning?",
        "task_type": "general"
    }, "General Q&A - Default Model")

    # Test 2: Technical Q&A (should use technical model)
    test_api_endpoint("/ask", {
        "q": "How do I deploy a microservice architecture?",
        "task_type": "technical"
    }, "Technical Q&A - Technical Model")

    # Test 3: Code generation (should use code generation model)
    test_api_endpoint("/code/generate", {
        "prompt": "Create a REST API endpoint for user authentication",
        "language": "python",
        "framework": "fastapi",
        "include_docs": True
    }, "Code Generation - Automatic Model Selection")

    # Test 4: Code generation with specific model
    test_api_endpoint("/code/generate", {
        "prompt": "Create a binary search algorithm",
        "language": "python",
        "include_docs": True,
        "model": "codellama:13b"
    }, "Code Generation - Explicit Model (CodeLlama)")

    # Test 5: Domain detection
    try:
        print(f"\n🎯 Domain Detection Test")
        print("=" * 60)

        domain_response = requests.post("http://localhost:7001/domain/detect",
                                      json={"text": "Portfolio management involves asset allocation and risk assessment for investment strategies"})

        if domain_response.status_code == 200:
            domain_result = domain_response.json()
            print(f"📊 Detected Domain: {domain_result['detected_domain']}")
            print(f"🎯 Confidence: {domain_result['confidence']:.2f}")
            print(f"🔍 Keyword Matches: {domain_result['domain_keywords_matched']}")

    except Exception as e:
        print(f"❌ Domain detection failed: {e}")

    print(f"\n🏁 Demo Complete!")
    print("=" * 60)
    print("💡 Key Features Demonstrated:")
    print("   • 🤖 Automatic model selection based on task type")
    print("   • 🎯 Domain-aware processing")
    print("   • 💻 Specialized code generation models")
    print("   • 🔄 Fallback model handling")
    print("   • 📊 Model availability detection")
    print("   • 🏷️  Domain classification")

if __name__ == "__main__":
    main()
