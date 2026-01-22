"""
API Key Manager
Handles API key retrieval from multiple sources with priority:
1. Session state (UI input)
2. Streamlit secrets
3. Environment variables
"""

import os
import streamlit as st
from typing import Optional, Dict, List, Tuple
from enum import Enum


class KeySource(Enum):
    """Source of API key"""
    SESSION = "session"
    SECRETS = "secrets"
    ENV = "environment"
    NOT_SET = "not_set"


class APIKeyManager:
    """Manages API keys from multiple sources"""
    
    # Provider key mappings
    PROVIDER_KEY_MAP = {
        'openai': 'OPENAI_API_KEY',
        'anthropic': 'ANTHROPIC_API_KEY',
        'gemini': 'GEMINI_API_KEY',
        'cohere': 'COHERE_API_KEY',
        'openrouter': 'OPENROUTER_API_KEY',
        'groq': 'GROQ_API_KEY',
        'huggingface': 'HUGGINGFACE_API_KEY',
        'azure': ['AZURE_OPENAI_KEY', 'AZURE_OPENAI_ENDPOINT'],
        # Custom providers are stored in session state with 'custom_' prefix
    }
    
    # Provider display information
    PROVIDER_INFO = {
        'openai': {
            'name': 'OpenAI',
            'icon': '🤖',
            'help_url': 'https://platform.openai.com/api-keys',
            'placeholder': 'sk-...'
        },
        'anthropic': {
            'name': 'Anthropic (Claude)',
            'icon': '🧠',
            'help_url': 'https://console.anthropic.com/settings/keys',
            'placeholder': 'sk-ant-...'
        },
        'gemini': {
            'name': 'Google Gemini',
            'icon': '✨',
            'help_url': 'https://aistudio.google.com/app/apikey',
            'placeholder': 'AIza...'
        },
        'groq': {
            'name': 'Groq',
            'icon': '⚡',
            'help_url': 'https://console.groq.com/keys',
            'placeholder': 'gsk_...'
        },
        'cohere': {
            'name': 'Cohere',
            'icon': '🔮',
            'help_url': 'https://dashboard.cohere.com/api-keys',
            'placeholder': 'your-api-key'
        },
        'openrouter': {
            'name': 'OpenRouter',
            'icon': '🌐',
            'help_url': 'https://openrouter.ai/keys',
            'placeholder': 'sk-or-...'
        },
        'huggingface': {
            'name': 'Hugging Face',
            'icon': '🤗',
            'help_url': 'https://huggingface.co/settings/tokens',
            'placeholder': 'hf_...'
        },
        'azure': {
            'name': 'Azure OpenAI',
            'icon': '☁️',
            'help_url': 'https://portal.azure.com/',
            'placeholder': 'your-azure-key'
        }
    }
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state for API keys"""
        if 'api_keys' not in st.session_state:
            st.session_state.api_keys = {}
        if 'azure_endpoint' not in st.session_state:
            st.session_state.azure_endpoint = ''
        if 'custom_providers' not in st.session_state:
            st.session_state.custom_providers = {}
    
    @staticmethod
    def get_api_key(provider: str) -> Tuple[Optional[str], KeySource]:
        """
        Get API key for a provider from available sources
        
        Args:
            provider: Provider name (e.g., 'openai', 'gemini')
            
        Returns:
            Tuple of (api_key, source)
        """
        APIKeyManager.initialize_session_state()
        
        # Handle Azure separately (needs both key and endpoint)
        if provider == 'azure':
            return APIKeyManager._get_azure_credentials()
        
        key_name = APIKeyManager.PROVIDER_KEY_MAP.get(provider)
        if not key_name:
            return None, KeySource.NOT_SET
        
        # Priority 1: Session state (UI input)
        if provider in st.session_state.api_keys and st.session_state.api_keys[provider]:
            return st.session_state.api_keys[provider], KeySource.SESSION
        
        # Priority 2: Streamlit secrets
        try:
            if hasattr(st, 'secrets') and key_name in st.secrets:
                return st.secrets[key_name], KeySource.SECRETS
        except Exception:
            pass
        
        # Priority 3: Environment variables
        env_key = os.getenv(key_name)
        if env_key:
            return env_key, KeySource.ENV
        
        return None, KeySource.NOT_SET
    
    @staticmethod
    def _get_azure_credentials() -> Tuple[Optional[Dict[str, str]], KeySource]:
        """Get Azure OpenAI credentials (key + endpoint)"""
        key_source = KeySource.NOT_SET
        
        # Check session state
        if 'azure' in st.session_state.api_keys and st.session_state.api_keys['azure']:
            key = st.session_state.api_keys['azure']
            endpoint = st.session_state.get('azure_endpoint', '')
            if key and endpoint:
                return {'key': key, 'endpoint': endpoint}, KeySource.SESSION
        
        # Check secrets
        try:
            if hasattr(st, 'secrets'):
                if 'AZURE_OPENAI_KEY' in st.secrets and 'AZURE_OPENAI_ENDPOINT' in st.secrets:
                    return {
                        'key': st.secrets['AZURE_OPENAI_KEY'],
                        'endpoint': st.secrets['AZURE_OPENAI_ENDPOINT']
                    }, KeySource.SECRETS
        except Exception:
            pass
        
        # Check environment
        key = os.getenv('AZURE_OPENAI_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        if key and endpoint:
            return {'key': key, 'endpoint': endpoint}, KeySource.ENV
        
        return None, KeySource.NOT_SET
    
    @staticmethod
    def set_api_key(provider: str, api_key: str, endpoint: Optional[str] = None):
        """
        Set API key in session state
        
        Args:
            provider: Provider name
            api_key: API key value
            endpoint: Azure endpoint (only for Azure provider)
        """
        APIKeyManager.initialize_session_state()
        
        if api_key and api_key.strip():
            st.session_state.api_keys[provider] = api_key.strip()
            
            if provider == 'azure' and endpoint:
                st.session_state.azure_endpoint = endpoint.strip()
    
    @staticmethod
    def clear_api_key(provider: str):
        """Clear API key from session state"""
        APIKeyManager.initialize_session_state()
        
        if provider in st.session_state.api_keys:
            del st.session_state.api_keys[provider]
        
        if provider == 'azure' and 'azure_endpoint' in st.session_state:
            st.session_state.azure_endpoint = ''
    
    @staticmethod
    def get_all_configured_providers() -> Dict[str, Tuple[str, KeySource]]:
        """
        Get all providers with configured API keys
        
        Returns:
            Dict mapping provider name to (masked_key, source)
        """
        configured = {}
        
        for provider in APIKeyManager.PROVIDER_KEY_MAP.keys():
            key, source = APIKeyManager.get_api_key(provider)
            
            if key and source != KeySource.NOT_SET:
                if provider == 'azure':
                    # Azure returns a dict
                    masked = APIKeyManager._mask_key(key['key']) if isinstance(key, dict) else '***'
                else:
                    masked = APIKeyManager._mask_key(key)
                
                configured[provider] = (masked, source)
        
        return configured
    
    @staticmethod
    def _mask_key(key: str) -> str:
        """Mask API key for display"""
        if not key or len(key) < 8:
            return '***'
        
        return f"{key[:4]}...{key[-4:]}"
    
    @staticmethod
    def validate_key_format(provider: str, api_key: str) -> Tuple[bool, str]:
        """
        Validate API key format
        
        Args:
            provider: Provider name
            api_key: API key to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key or not api_key.strip():
            return False, "API key cannot be empty"
        
        key = api_key.strip()
        
        # Basic format validation
        validations = {
            'openai': lambda k: k.startswith('sk-'),
            'anthropic': lambda k: k.startswith('sk-ant-'),
            'gemini': lambda k: k.startswith('AIza') or len(k) > 20,
            'groq': lambda k: k.startswith('gsk_'),
            'huggingface': lambda k: k.startswith('hf_'),
            'openrouter': lambda k: k.startswith('sk-or-'),
        }
        
        if provider in validations:
            if not validations[provider](key):
                expected = APIKeyManager.PROVIDER_INFO[provider]['placeholder']
                return False, f"Invalid format. Expected format: {expected}"
        
        return True, ""
    
    @staticmethod
    def export_to_env_format() -> str:
        """
        Export configured keys to .env file format
        
        Returns:
            String in .env format
        """
        lines = [
            "# API Keys Configuration",
            "# Generated by MedDiag Gemini 3",
            "",
            "# ===== LLM Provider API Keys =====",
            ""
        ]
        
        configured = APIKeyManager.get_all_configured_providers()
        
        for provider, (masked_key, source) in configured.items():
            if source == KeySource.SESSION:
                # Only export session keys (user entered)
                key, _ = APIKeyManager.get_api_key(provider)
                
                if provider == 'azure':
                    lines.append(f"AZURE_OPENAI_KEY={key['key']}")
                    lines.append(f"AZURE_OPENAI_ENDPOINT={key['endpoint']}")
                else:
                    key_name = APIKeyManager.PROVIDER_KEY_MAP[provider]
                    lines.append(f"{key_name}={key}")
        
        return "\n".join(lines)
    
    @staticmethod
    def get_provider_info(provider: str) -> Dict:
        """Get display information for a provider"""
        # Check if it's a custom provider
        if provider.startswith('custom_'):
            APIKeyManager.initialize_session_state()
            if provider in st.session_state.custom_providers:
                custom_config = st.session_state.custom_providers[provider]
                return {
                    'name': custom_config.get('name', 'Custom Provider'),
                    'icon': '🔧',
                    'help_url': '',
                    'placeholder': 'your-api-key'
                }
        
        return APIKeyManager.PROVIDER_INFO.get(provider, {
            'name': provider.capitalize(),
            'icon': '🔑',
            'help_url': '',
            'placeholder': 'your-api-key'
        })
    
    @staticmethod
    def add_custom_provider(name: str, base_url: str, api_key: str, default_model: str = 'gpt-4o', custom_headers: Dict = None) -> str:
        """Add a custom provider configuration
        
        Args:
            name: Display name for the provider
            base_url: Base URL for the API endpoint
            api_key: API key for authentication
            default_model: Default model to use
            custom_headers: Optional custom headers
            
        Returns:
            Provider ID (custom_<sanitized_name>)
        """
        APIKeyManager.initialize_session_state()
        
        # Create provider ID
        provider_id = f"custom_{name.lower().replace(' ', '_').replace('-', '_')}"
        
        # Store configuration
        st.session_state.custom_providers[provider_id] = {
            'name': name,
            'base_url': base_url,
            'default_model': default_model,
            'custom_headers': custom_headers or {}
        }
        
        # Store API key
        st.session_state.api_keys[provider_id] = api_key
        
        return provider_id
    
    @staticmethod
    def remove_custom_provider(provider_id: str):
        """Remove a custom provider"""
        APIKeyManager.initialize_session_state()
        
        if provider_id in st.session_state.custom_providers:
            del st.session_state.custom_providers[provider_id]
        
        if provider_id in st.session_state.api_keys:
            del st.session_state.api_keys[provider_id]
    
    @staticmethod
    def get_custom_providers() -> Dict[str, Dict]:
        """Get all custom provider configurations"""
        APIKeyManager.initialize_session_state()
        return st.session_state.custom_providers.copy()
    
    @staticmethod
    def get_custom_provider_config(provider_id: str) -> Dict:
        """Get configuration for a specific custom provider"""
        APIKeyManager.initialize_session_state()
        return st.session_state.custom_providers.get(provider_id, {})
