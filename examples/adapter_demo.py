"""
Universal LLM Adapter Demo
Demonstrates how to use the adapter system with different providers
"""

import os
import sys
from PIL import Image
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import the helper functions
from utils.llm_helpers import (
    generate_with_llm,
    get_available_providers_info,
    get_provider_models,
    create_llm_adapter
)
from utils.llm_adapter import LLMRequest


def demo_text_generation():
    """Demo: Simple text generation"""
    print("=" * 60)
    print("DEMO 1: Simple Text Generation")
    print("=" * 60)
    
    prompt = "Explain what a differential diagnosis is in medical terms, in 2-3 sentences."
    
    # Get available providers
    providers = get_available_providers_info()
    
    if not providers:
        print("⚠️  No API keys found in environment variables!")
        print("Please add at least one API key to your .env file")
        return
    
    print(f"\n✓ Found {len(providers)} available provider(s):")
    for provider_id, info in providers.items():
        print(f"  • {info['icon']} {info['display_name']}")
    
    # Use first available provider
    provider_id = list(providers.keys())[0]
    provider_info = providers[provider_id]
    
    print(f"\n🚀 Using provider: {provider_info['display_name']}")
    print(f"📝 Prompt: {prompt}")
    print("\n⏳ Generating response...")
    
    try:
        response = generate_with_llm(
            prompt=prompt,
            provider=provider_id,
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"\n✅ Response received!")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Latency: {response.latency:.2f}s")
        print(f"   Tokens: {response.input_tokens} in / {response.output_tokens} out")
        print(f"   Cost: ${response.cost:.4f}")
        print(f"\n📄 Response:\n{response.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def demo_multimodal_generation():
    """Demo: Multimodal generation with images"""
    print("\n" + "=" * 60)
    print("DEMO 2: Multimodal Generation (Text + Images)")
    print("=" * 60)
    
    # Check for sample image
    sample_image_path = "assets/sample_xray.jpg"
    
    if not os.path.exists(sample_image_path):
        print(f"\n⚠️  Sample image not found at {sample_image_path}")
        print("Skipping multimodal demo")
        return
    
    # Load image
    image = Image.open(sample_image_path)
    print(f"\n✓ Loaded image: {sample_image_path}")
    
    prompt = "Describe what you see in this medical image. What type of imaging is this?"
    
    # Get providers that support vision
    providers = get_available_providers_info()
    vision_providers = []
    
    for provider_id, info in providers.items():
        try:
            adapter = create_llm_adapter(provider_id)
            models = adapter.get_available_models()
            if models:
                # Check if default model supports vision
                default_model = info.get('default_model')
                caps = adapter.get_model_capabilities(default_model)
                if caps.supports_vision:
                    vision_providers.append((provider_id, info))
        except:
            pass
    
    if not vision_providers:
        print("\n⚠️  No vision-capable providers found!")
        return
    
    provider_id, provider_info = vision_providers[0]
    
    print(f"\n🚀 Using provider: {provider_info['display_name']}")
    print(f"📝 Prompt: {prompt}")
    print("🖼️  With 1 image")
    print("\n⏳ Generating response...")
    
    try:
        response = generate_with_llm(
            prompt=prompt,
            images=[image],
            provider=provider_id,
            temperature=0.3,
            max_tokens=300
        )
        
        print(f"\n✅ Response received!")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Latency: {response.latency:.2f}s")
        print(f"   Tokens: {response.input_tokens} in / {response.output_tokens} out")
        print(f"   Cost: ${response.cost:.4f}")
        print(f"\n📄 Response:\n{response.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def demo_provider_comparison():
    """Demo: Compare responses from multiple providers"""
    print("\n" + "=" * 60)
    print("DEMO 3: Multi-Provider Comparison")
    print("=" * 60)
    
    prompt = "What are the top 3 causes of chest pain? List them briefly."
    
    providers = get_available_providers_info()
    
    if len(providers) < 2:
        print("\n⚠️  Need at least 2 providers for comparison")
        return
    
    print(f"\n📝 Prompt: {prompt}")
    print(f"\n🔄 Comparing {len(providers)} provider(s)...\n")
    
    for provider_id, provider_info in providers.items():
        print(f"\n{'─' * 60}")
        print(f"{provider_info['icon']} {provider_info['display_name']}")
        print(f"{'─' * 60}")
        
        try:
            response = generate_with_llm(
                prompt=prompt,
                provider=provider_id,
                temperature=0.5,
                max_tokens=200
            )
            
            print(f"Model: {response.model}")
            print(f"Latency: {response.latency:.2f}s | Tokens: {response.output_tokens} | Cost: ${response.cost:.4f}")
            print(f"\nResponse:\n{response.text}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def demo_model_listing():
    """Demo: List available models for each provider"""
    print("\n" + "=" * 60)
    print("DEMO 4: Available Models by Provider")
    print("=" * 60)
    
    providers = get_available_providers_info()
    
    for provider_id, provider_info in providers.items():
        print(f"\n{provider_info['icon']} {provider_info['display_name']}")
        print(f"{'─' * 40}")
        
        try:
            models = get_provider_models(provider_id)
            for i, model in enumerate(models, 1):
                # Check capabilities
                adapter = create_llm_adapter(provider_id)
                caps = adapter.get_model_capabilities(model)
                
                vision_icon = "🖼️ " if caps.supports_vision else "📝"
                stream_icon = "⚡" if caps.supports_streaming else ""
                
                print(f"  {i}. {vision_icon} {model} {stream_icon}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")


def main():
    """Run all demos"""
    print("\n🤖 Universal LLM Adapter - Demo Suite")
    print("=" * 60)
    
    # Run demos
    demo_text_generation()
    demo_multimodal_generation()
    demo_provider_comparison()
    demo_model_listing()
    
    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
