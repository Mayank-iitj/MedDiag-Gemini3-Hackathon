"""
LLM Configuration
Provider configurations, model capabilities, and settings
"""

from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


class LLMConfig:
    """Configuration for LLM providers"""
    
    # Provider API Keys from environment
    PROVIDERS = {
        'openai': {
            'api_key_env': 'OPENAI_API_KEY',
            'display_name': 'OpenAI',
            'icon': '🤖',
            'default_model': 'gpt-4o',
            'requires_endpoint': False
        },
        'anthropic': {
            'api_key_env': 'ANTHROPIC_API_KEY',
            'display_name': 'Anthropic (Claude)',
            'icon': '🧠',
            'default_model': 'claude-3-5-sonnet-20241022',
            'requires_endpoint': False
        },
        'gemini': {
            'api_key_env': 'GEMINI_API_KEY',
            'display_name': 'Google Gemini',
            'icon': '✨',
            'default_model': 'gemini-2.0-flash-exp',
            'requires_endpoint': False
        },
        'cohere': {
            'api_key_env': 'COHERE_API_KEY',
            'display_name': 'Cohere',
            'icon': '🔷',
            'default_model': 'command-r-plus',
            'requires_endpoint': False
        },
        'openrouter': {
            'api_key_env': 'OPENROUTER_API_KEY',
            'display_name': 'OpenRouter (Multi-Model)',
            'icon': '🔀',
            'default_model': 'google/gemini-2.0-flash-exp:free',
            'requires_endpoint': False
        },
        'azure': {
            'api_key_env': 'AZURE_OPENAI_KEY',
            'endpoint_env': 'AZURE_OPENAI_ENDPOINT',
            'display_name': 'Azure OpenAI',
            'icon': '☁️',
            'default_model': 'gpt-4o',
            'requires_endpoint': True
        },
        'huggingface': {
            'api_key_env': 'HUGGINGFACE_API_KEY',
            'display_name': 'Hugging Face',
            'icon': '🤗',
            'default_model': 'meta-llama/Meta-Llama-3-8B-Instruct',
            'requires_endpoint': False
        },
        'groq': {
            'api_key_env': 'GROQ_API_KEY',
            'display_name': 'Groq (Ultra-Fast)',
            'icon': '⚡',
            'default_model': 'llama-3.3-70b-versatile',
            'requires_endpoint': False
        }
    }
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Get list of providers with available API keys"""
        available = {}
        
        for provider_id, config in cls.PROVIDERS.items():
            api_key = os.getenv(config['api_key_env'])
            
            if api_key:
                provider_info = config.copy()
                provider_info['has_api_key'] = True
                
                # Check for endpoint if required
                if config.get('requires_endpoint'):
                    endpoint = os.getenv(config.get('endpoint_env', ''))
                    provider_info['has_endpoint'] = bool(endpoint)
                    provider_info['endpoint'] = endpoint
                else:
                    provider_info['has_endpoint'] = True
                
                available[provider_id] = provider_info
        
        return available
    
    @classmethod
    def get_provider_config(cls, provider_id: str) -> Dict[str, Any]:
        """Get configuration for a specific provider"""
        if provider_id not in cls.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_id}")
        
        config = cls.PROVIDERS[provider_id].copy()
        config['api_key'] = os.getenv(config['api_key_env'], '')
        
        if config.get('requires_endpoint'):
            config['endpoint'] = os.getenv(config.get('endpoint_env', ''), '')
        
        return config
    
    @classmethod
    def get_default_provider(cls) -> str:
        """Get default provider from environment or first available"""
        default = os.getenv('DEFAULT_PROVIDER', '').lower()
        
        if default and default in cls.PROVIDERS:
            api_key = os.getenv(cls.PROVIDERS[default]['api_key_env'])
            if api_key:
                return default
        
        # Return first available provider
        available = cls.get_available_providers()
        if available:
            return list(available.keys())[0]
        
        return 'gemini'  # Fallback
    
    # Model capability matrix
    MODEL_CAPABILITIES = {
        # OpenAI
        'gpt-4o': {'vision': True, 'streaming': True, 'max_tokens': 4096},
        'gpt-4o-mini': {'vision': True, 'streaming': True, 'max_tokens': 16384},
        'gpt-4-turbo': {'vision': True, 'streaming': True, 'max_tokens': 4096},
        
        # Anthropic
        'claude-3-5-sonnet-20241022': {'vision': True, 'streaming': True, 'max_tokens': 8192},
        'claude-3-opus-20240229': {'vision': True, 'streaming': True, 'max_tokens': 4096},
        'claude-3-haiku-20240307': {'vision': True, 'streaming': True, 'max_tokens': 4096},
        
        # Gemini
        'gemini-2.0-flash-exp': {'vision': True, 'streaming': True, 'max_tokens': 8192},
        'gemini-1.5-pro': {'vision': True, 'streaming': True, 'max_tokens': 8192},
        'gemini-1.5-flash': {'vision': True, 'streaming': True, 'max_tokens': 8192},
        
        # Cohere
        'command-r-plus': {'vision': False, 'streaming': True, 'max_tokens': 4096},
        'command-r': {'vision': False, 'streaming': True, 'max_tokens': 4096},
    }
