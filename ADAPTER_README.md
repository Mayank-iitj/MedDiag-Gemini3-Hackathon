# 🤖 Universal LLM API Adapter

> A production-ready adapter system providing a unified interface for all major LLM providers

## ✨ Features

- 🔌 **7 Provider Adapters**: OpenAI, Anthropic, Gemini, Cohere, OpenRouter, Azure, Hugging Face
- 🖼️ **Multimodal Support**: Unified text + image interface
- 💰 **Cost Tracking**: Automatic token counting and cost estimation
- 🔄 **Easy Switching**: Change providers without code changes
- 🛡️ **Error Handling**: Automatic retries with exponential backoff
- 📊 **Capability Detection**: Automatic model capability detection

## 🚀 Quick Start

```python
from utils.llm_helpers import generate_with_llm

# Simple text generation
response = generate_with_llm(
    prompt="Explain differential diagnosis",
    provider="gemini",
    temperature=0.7
)

print(response.text)
print(f"Cost: ${response.cost:.4f}")
```

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your API keys
```

## 🎯 Supported Providers

| Provider | Vision | Streaming | Free Tier |
|----------|--------|-----------|-----------|
| 🤖 OpenAI | ✅ | ✅ | ❌ |
| 🧠 Anthropic (Claude) | ✅ | ✅ | ❌ |
| ✨ Google Gemini | ✅ | ✅ | ✅ |
| 🔷 Cohere | ❌ | ✅ | ✅ |
| 🔀 OpenRouter | ✅ | ✅ | ✅ |
| ☁️ Azure OpenAI | ✅ | ✅ | ❌ |
| 🤗 Hugging Face | ❌ | ✅ | ✅ |

## 📖 Documentation

- **[Full Guide](docs/LLM_ADAPTER_GUIDE.md)** - Complete documentation
- **[Quick Reference](docs/ADAPTER_README.md)** - Quick start guide
- **[Examples](examples/adapter_demo.py)** - Demo script

## 🖼️ Multimodal Example

```python
from PIL import Image
from utils.llm_helpers import generate_with_llm

image = Image.open("medical_scan.jpg")

response = generate_with_llm(
    prompt="Analyze this medical image",
    images=[image],
    provider="openai",
    model="gpt-4o"
)
```

## 🔧 Configuration

Add API keys to `.env`:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AI...
COHERE_API_KEY=...
OPENROUTER_API_KEY=sk-or-...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
HUGGINGFACE_API_KEY=hf_...
DEFAULT_PROVIDER=gemini
```

## 🧪 Run Demo

```bash
python examples/adapter_demo.py
```

## 📁 Project Structure

```
├── utils/
│   ├── llm_adapter.py          # Base adapter system
│   ├── llm_helpers.py          # Helper functions
│   └── adapters/               # Provider adapters
├── config/
│   └── llm_config.py           # Configuration
├── examples/
│   └── adapter_demo.py         # Demo script
└── docs/
    └── LLM_ADAPTER_GUIDE.md    # Documentation
```

## 💡 Usage Examples

### Provider Comparison

```python
from utils.llm_helpers import generate_with_llm

providers = ["gemini", "openai", "anthropic"]

for provider in providers:
    response = generate_with_llm(
        prompt="What is AI?",
        provider=provider
    )
    print(f"{provider}: {response.text[:100]}...")
```

### Check Available Providers

```python
from utils.llm_helpers import get_available_providers_info

providers = get_available_providers_info()
for provider_id, info in providers.items():
    print(f"{info['icon']} {info['display_name']}")
```

### Model Capabilities

```python
from utils.llm_helpers import create_llm_adapter

adapter = create_llm_adapter("openai")
caps = adapter.get_model_capabilities("gpt-4o")

print(f"Supports vision: {caps.supports_vision}")
print(f"Max tokens: {caps.max_tokens}")
```

## 🎓 Learn More

- **Architecture**: See [LLM_ADAPTER_GUIDE.md](docs/LLM_ADAPTER_GUIDE.md#architecture)
- **Add Providers**: See [LLM_ADAPTER_GUIDE.md](docs/LLM_ADAPTER_GUIDE.md#adding-a-new-provider)
- **Best Practices**: See [LLM_ADAPTER_GUIDE.md](docs/LLM_ADAPTER_GUIDE.md#best-practices)

## 📝 License

Part of the MedDiag Gemini 3 project.

---

**Built with ❤️ for the Gemini 3 Hackathon**
