"""
Helper functions for easy LLM adapter usage
"""

from typing import List, Optional
from PIL import Image
import os

from utils.llm_adapter import (
    LLMAdapterFactory, ProviderType, LLMRequest, LLMResponse
)
from config.llm_config import LLMConfig

# Import all adapters to register them
import utils.adapters


def create_llm_adapter(provider: str = None, api_key: str = None, **kwargs):
    """
    Create an LLM adapter instance
    
    Args:
        provider: Provider name (openai, anthropic, gemini, etc.)
        api_key: API key (if not provided, will try to get from environment)
        **kwargs: Additional provider-specific arguments
    
    Returns:
        LLM adapter instance
    """
    # Get provider from environment if not specified
    if not provider:
        provider = LLMConfig.get_default_provider()
    
    provider = provider.lower()
    
    # Get API key from environment if not provided
    if not api_key:
        config = LLMConfig.get_provider_config(provider)
        api_key = config.get('api_key')
        
        if not api_key:
            raise ValueError(f"No API key found for provider: {provider}")
        
        # Add endpoint for Azure
        if provider == 'azure' and 'endpoint' not in kwargs:
            kwargs['endpoint'] = config.get('endpoint')
    
    # Map provider string to ProviderType enum
    provider_map = {
        'openai': ProviderType.OPENAI,
        'anthropic': ProviderType.ANTHROPIC,
        'gemini': ProviderType.GEMINI,
        'cohere': ProviderType.COHERE,
        'openrouter': ProviderType.OPENROUTER,
        'azure': ProviderType.AZURE,
        'huggingface': ProviderType.HUGGINGFACE,
        'groq': ProviderType.GROQ
    }
    
    if provider not in provider_map:
        raise ValueError(f"Unknown provider: {provider}")
    
    provider_type = provider_map[provider]
    
    return LLMAdapterFactory.create_adapter(provider_type, api_key, **kwargs)


def generate_with_llm(
    prompt: str,
    images: Optional[List[Image.Image]] = None,
    provider: str = None,
    model: str = None,
    temperature: float = 0.1,
    max_tokens: int = 4000,
    system_prompt: Optional[str] = None,
    api_key: str = None,
    **kwargs
) -> LLMResponse:
    """
    Simple function to generate text with any LLM provider
    
    Args:
        prompt: Text prompt
        images: Optional list of PIL images
        provider: Provider name
        model: Model name
        temperature: Temperature setting
        max_tokens: Maximum tokens to generate
        system_prompt: Optional system prompt
        api_key: Optional API key
        **kwargs: Additional provider-specific arguments
    
    Returns:
        LLMResponse object
    """
    # Create adapter
    adapter = create_llm_adapter(provider, api_key, **kwargs)
    
    # Create request
    request = LLMRequest(
        prompt=prompt,
        images=images,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        model=model
    )
    
    # Generate response
    return adapter.generate(request)


def get_available_providers_info():
    """Get information about available providers"""
    return LLMConfig.get_available_providers()


def get_provider_models(provider: str) -> List[str]:
    """Get available models for a provider"""
    try:
        adapter = create_llm_adapter(provider)
        return adapter.get_available_models()
    except Exception as e:
        return []
