# Universal LLM API Adapter

A unified interface for all major LLM providers with multimodal support.

## Quick Start

```python
from utils.llm_helpers import generate_with_llm

# Text generation
response = generate_with_llm(
    prompt="Explain machine learning",
    provider="gemini",
    temperature=0.7
)

print(response.text)
```

## Supported Providers

| Provider | Vision | Streaming | Models |
|----------|--------|-----------|--------|
| 🤖 OpenAI | ✅ | ✅ | GPT-4o, GPT-4 Turbo, GPT-3.5 |
| 🧠 Anthropic | ✅ | ✅ | Claude 3.5 Sonnet, Opus, Haiku |
| ✨ Google Gemini | ✅ | ✅ | Gemini 2.0, 1.5 Pro/Flash |
| 🔷 Cohere | ❌ | ✅ | Command R+, Command R |
| 🔀 OpenRouter | ✅ | ✅ | 50+ models |
| ☁️ Azure OpenAI | ✅ | ✅ | GPT-4o, GPT-4 Turbo |
| 🤗 Hugging Face | ❌ | ✅ | Llama 3, Mistral, Mixtral |

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Add API keys to `.env`:

```bash
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
# ... etc
```

## Documentation

See [LLM_ADAPTER_GUIDE.md](LLM_ADAPTER_GUIDE.md) for complete documentation.

## Examples

```bash
python examples/adapter_demo.py
```

## Features

- ✅ Unified interface for all providers
- ✅ Automatic multimodal support
- ✅ Cost tracking and token counting
- ✅ Error handling with retries
- ✅ Model capability detection
- ✅ Easy provider switching
