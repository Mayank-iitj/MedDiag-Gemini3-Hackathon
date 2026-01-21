# Universal LLM API Adapter Guide

## Overview

The Universal LLM API Adapter provides a unified interface for working with multiple LLM providers. Switch between OpenAI, Anthropic, Google Gemini, Cohere, OpenRouter, Azure OpenAI, and Hugging Face with a single, consistent API.

## Features

- 🔌 **7 Provider Adapters**: OpenAI, Anthropic (Claude), Google Gemini, Cohere, OpenRouter, Azure OpenAI, Hugging Face
- 🖼️ **Multimodal Support**: Unified interface for text + image inputs
- 🔄 **Easy Switching**: Change providers without code changes
- 💰 **Cost Tracking**: Automatic token usage and cost estimation
- 🛡️ **Error Handling**: Automatic retries with exponential backoff
- 📊 **Capability Detection**: Automatic detection of model capabilities (vision, streaming, etc.)

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
# Add at least one provider API key
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
# ... etc
```

### 3. Basic Usage

```python
from utils.llm_helpers import generate_with_llm

# Simple text generation
response = generate_with_llm(
    prompt="Explain differential diagnosis",
    provider="gemini",  # or "openai", "anthropic", etc.
    temperature=0.7,
    max_tokens=200
)

print(response.text)
print(f"Cost: ${response.cost:.4f}")
```

### 4. Multimodal Usage (with Images)

```python
from PIL import Image
from utils.llm_helpers import generate_with_llm

# Load image
image = Image.open("medical_scan.jpg")

# Analyze image
response = generate_with_llm(
    prompt="Describe this medical image",
    images=[image],
    provider="gemini",  # Must support vision
    temperature=0.3
)

print(response.text)
```

## Supported Providers

### OpenAI
- **Models**: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo
- **Vision Support**: ✅ (GPT-4o, GPT-4 Turbo)
- **API Key**: `OPENAI_API_KEY`

```python
response = generate_with_llm(
    prompt="Your prompt",
    provider="openai",
    model="gpt-4o"
)
```

### Anthropic (Claude)
- **Models**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
- **Vision Support**: ✅
- **API Key**: `ANTHROPIC_API_KEY`

```python
response = generate_with_llm(
    prompt="Your prompt",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Google Gemini
- **Models**: Gemini 2.0 Flash, Gemini 1.5 Pro/Flash
- **Vision Support**: ✅
- **API Key**: `GEMINI_API_KEY`

```python
response = generate_with_llm(
    prompt="Your prompt",
    provider="gemini",
    model="gemini-2.0-flash-exp"
)
```

### Cohere
- **Models**: Command R+, Command R, Command
- **Vision Support**: ❌
- **API Key**: `COHERE_API_KEY`

```python
response = generate_with_llm(
    prompt="Your prompt",
    provider="cohere",
    model="command-r-plus"
)
```

### OpenRouter (Multi-Model)
- **Models**: Access to 50+ models from multiple providers
- **Vision Support**: ✅ (model-dependent)
- **API Key**: `OPENROUTER_API_KEY`

```python
response = generate_with_llm(
    prompt="Your prompt",
    provider="openrouter",
    model="google/gemini-2.0-flash-exp:free"
)
```

### Azure OpenAI
- **Models**: GPT-4o, GPT-4 Turbo (deployment-based)
- **Vision Support**: ✅
- **API Key**: `AZURE_OPENAI_KEY` + `AZURE_OPENAI_ENDPOINT`

```python
response = generate_with_llm(
    prompt="Your prompt",
    provider="azure",
    model="gpt-4o"  # Your deployment name
)
```

### Hugging Face
- **Models**: Llama 3, Mistral, Mixtral, Gemma, Phi-3
- **Vision Support**: ❌ (most models)
- **API Key**: `HUGGINGFACE_API_KEY`

```python
response = generate_with_llm(
    prompt="Your prompt",
    provider="huggingface",
    model="meta-llama/Meta-Llama-3-8B-Instruct"
)
```

## Advanced Usage

### Using the Adapter Directly

```python
from utils.llm_helpers import create_llm_adapter
from utils.llm_adapter import LLMRequest

# Create adapter
adapter = create_llm_adapter("openai")

# Create request
request = LLMRequest(
    prompt="Your prompt",
    temperature=0.7,
    max_tokens=500,
    system_prompt="You are a medical expert"
)

# Generate response
response = adapter.generate(request)
```

### Checking Provider Availability

```python
from utils.llm_helpers import get_available_providers_info

providers = get_available_providers_info()

for provider_id, info in providers.items():
    print(f"{info['icon']} {info['display_name']}")
    print(f"  Default model: {info['default_model']}")
```

### Checking Model Capabilities

```python
from utils.llm_helpers import create_llm_adapter

adapter = create_llm_adapter("openai")
caps = adapter.get_model_capabilities("gpt-4o")

print(f"Supports vision: {caps.supports_vision}")
print(f"Supports streaming: {caps.supports_streaming}")
print(f"Max tokens: {caps.max_tokens}")
print(f"Cost per 1K input tokens: ${caps.cost_per_1k_input_tokens}")
```

### Error Handling

The adapter includes automatic retry logic with exponential backoff:

```python
from utils.llm_helpers import generate_with_llm

try:
    response = generate_with_llm(
        prompt="Your prompt",
        provider="openai"
    )
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

## Architecture

### Class Hierarchy

```
BaseLLMAdapter (Abstract)
├── OpenAIAdapter
├── AnthropicAdapter
├── GeminiAdapter
├── CohereAdapter
├── OpenRouterAdapter
├── AzureOpenAIAdapter
└── HuggingFaceAdapter
```

### Key Components

1. **BaseLLMAdapter**: Abstract base class defining the interface
2. **LLMAdapterFactory**: Factory for creating provider-specific adapters
3. **LLMRequest**: Standardized request format
4. **LLMResponse**: Standardized response format
5. **ModelCapabilities**: Model capability flags
6. **LLMConfig**: Provider configuration management

## Adding a New Provider

To add support for a new LLM provider:

1. Create a new adapter class in `utils/adapters/`:

```python
from ..llm_adapter import BaseLLMAdapter, LLMRequest, LLMResponse

class NewProviderAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.NEWPROVIDER
        self.default_model = "model-name"
        # Initialize client
    
    def get_available_models(self) -> List[str]:
        return ["model-1", "model-2"]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        return ModelCapabilities(...)
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        # Implementation
        pass
```

2. Register the adapter:

```python
from ..llm_adapter import LLMAdapterFactory, ProviderType

LLMAdapterFactory.register_adapter(ProviderType.NEWPROVIDER, NewProviderAdapter)
```

3. Add configuration to `config/llm_config.py`

4. Import in `utils/adapters/__init__.py`

## Cost Estimation

The adapter automatically tracks token usage and estimates costs:

```python
response = generate_with_llm(prompt="Test", provider="openai")

print(f"Input tokens: {response.input_tokens}")
print(f"Output tokens: {response.output_tokens}")
print(f"Estimated cost: ${response.cost:.6f}")
```

## Best Practices

1. **Always use environment variables** for API keys
2. **Check model capabilities** before using vision features
3. **Handle errors gracefully** with try-except blocks
4. **Monitor costs** by tracking token usage
5. **Use appropriate temperature** settings (0.1-0.3 for factual, 0.7-1.0 for creative)
6. **Set reasonable max_tokens** to control costs

## Troubleshooting

### "No API key found"
- Ensure your `.env` file exists and contains the required API key
- Check that the key name matches exactly (e.g., `OPENAI_API_KEY`)

### "Model does not support vision"
- Check model capabilities before sending images
- Use a vision-capable model (GPT-4o, Claude 3, Gemini, etc.)

### "Rate limit exceeded"
- The adapter will automatically retry with exponential backoff
- Consider upgrading your API plan or using a different provider

### Import errors
- Run `pip install -r requirements.txt` to install all dependencies
- Ensure you're in the correct virtual environment

## Examples

See `examples/adapter_demo.py` for comprehensive usage examples:

```bash
python examples/adapter_demo.py
```

## License

This adapter system is part of the MedDiag Gemini 3 project.
