"""
LLM Adapters Package
Auto-imports all available adapters
"""

# Import all adapters to register them with the factory
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .gemini_adapter import GeminiAdapter
from .cohere_adapter import CohereAdapter
from .openrouter_adapter import OpenRouterAdapter
from .azure_adapter import AzureOpenAIAdapter
from .huggingface_adapter import HuggingFaceAdapter
from .groq_adapter import GroqAdapter
from .custom_adapter import CustomLLMAdapter

__all__ = [
    'OpenAIAdapter',
    'AnthropicAdapter',
    'GeminiAdapter',
    'CohereAdapter',
    'OpenRouterAdapter',
    'AzureOpenAIAdapter',
    'HuggingFaceAdapter',
    'GroqAdapter',
    'CustomLLMAdapter'
]
