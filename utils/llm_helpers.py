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
        api_key: API key (if not provided, will try to get from API key manager)
        **kwargs: Additional provider-specific arguments
    
    Returns:
        LLM adapter instance
    """
    from utils.api_key_manager import APIKeyManager, KeySource
    from utils.adapters.custom_adapter import CustomLLMAdapter
    
    # Get provider from environment if not specified
    if not provider:
        provider = LLMConfig.get_default_provider()
    
    provider = provider.lower()
    
    # Check if it's a custom provider
    if provider.startswith('custom_'):
        custom_config = APIKeyManager.get_custom_provider_config(provider)
        if not custom_config:
            raise ValueError(f"Custom provider not found: {provider}")
        
        # Get API key
        if not api_key:
            key_data, source = APIKeyManager.get_api_key(provider)
            if not key_data:
                raise ValueError(f"No API key found for custom provider: {provider}")
            api_key = key_data
        
        # Create custom adapter
        return CustomLLMAdapter(
            api_key=api_key,
            base_url=custom_config.get('base_url'),
            provider_name=custom_config.get('name', 'Custom'),
            default_model=custom_config.get('default_model', 'gpt-4o'),
            custom_headers=custom_config.get('custom_headers', {})
        )
    
    # Get API key using APIKeyManager if not provided
    if not api_key:
        key_data, source = APIKeyManager.get_api_key(provider)
        
        if not key_data:
            raise ValueError(f"No API key found for provider: {provider}")
        
        # Handle Azure (returns dict with key and endpoint)
        if provider == 'azure':
            if isinstance(key_data, dict):
                api_key = key_data['key']
                if 'endpoint' not in kwargs:
                    kwargs['endpoint'] = key_data['endpoint']
            else:
                raise ValueError("Azure requires both API key and endpoint")
        else:
            api_key = key_data
    
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
    """Get information about available providers (built-in + custom)"""
    from utils.api_key_manager import APIKeyManager
    
    # Get all supported providers definitions
    supported_providers = LLMConfig.get_supported_providers()
    available_providers = {}
    
    # Check which ones have keys in session
    for provider_id, config in supported_providers.items():
        api_key, source = APIKeyManager.get_api_key(provider_id)
        
        # For Azure, api_key is a dict if set
        has_key = False
        if provider_id == 'azure':
            if isinstance(api_key, dict) and api_key.get('key') and api_key.get('endpoint'):
                has_key = True
        elif api_key:
            has_key = True
            
        if has_key:
            provider_info = config.copy()
            provider_info['has_api_key'] = True
            provider_info['has_endpoint'] = True # Assumed true if key is valid/present
            available_providers[provider_id] = provider_info
            
    # Add custom providers
    custom_providers = APIKeyManager.get_custom_providers()
    for provider_id, config in custom_providers.items():
        # Check if has API key
        api_key, source = APIKeyManager.get_api_key(provider_id)
        if api_key:
            available_providers[provider_id] = {
                'display_name': config.get('name', 'Custom Provider'),
                'icon': '🔧',
                'default_model': config.get('default_model', 'gpt-4o'),
                'has_api_key': True,
                'has_endpoint': True,
                'is_custom': True
            }
    
    return available_providers


def get_provider_models(provider: str) -> List[str]:
    """Get available models for a provider"""
    try:
        adapter = create_llm_adapter(provider)
        return adapter.get_available_models()
    except Exception as e:
        return []
