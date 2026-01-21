"""
Universal LLM API Adapter System
Provides a unified interface for all major LLM providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    COHERE = "cohere"
    OPENROUTER = "openrouter"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    GROQ = "groq"


@dataclass
class ModelCapabilities:
    """Model capability flags"""
    supports_vision: bool = False
    supports_streaming: bool = False
    supports_function_calling: bool = False
    max_tokens: int = 4096
    supports_system_prompt: bool = True
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0


@dataclass
class LLMRequest:
    """Standardized LLM request format"""
    prompt: str
    images: Optional[List[Any]] = None
    temperature: float = 0.1
    max_tokens: int = 4000
    system_prompt: Optional[str] = None
    stream: bool = False
    model: Optional[str] = None


@dataclass
class LLMResponse:
    """Standardized LLM response format"""
    text: str
    provider: str
    model: str
    latency: float
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = None


class BaseLLMAdapter(ABC):
    """Base class for all LLM adapters"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.kwargs = kwargs
        self.provider_type = None
        self.default_model = None
        self.capabilities = ModelCapabilities()
        
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text response"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for a specific model"""
        pass
    
    def validate_request(self, request: LLMRequest) -> bool:
        """Validate request against model capabilities"""
        model = request.model or self.default_model
        capabilities = self.get_model_capabilities(model)
        
        if request.images and not capabilities.supports_vision:
            raise ValueError(f"Model {model} does not support vision/images")
        
        if request.max_tokens > capabilities.max_tokens:
            logger.warning(f"Requested tokens {request.max_tokens} exceeds max {capabilities.max_tokens}")
            request.max_tokens = capabilities.max_tokens
        
        return True
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost based on token usage"""
        capabilities = self.get_model_capabilities(model)
        input_cost = (input_tokens / 1000) * capabilities.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * capabilities.cost_per_1k_output_tokens
        return input_cost + output_cost


class LLMAdapterFactory:
    """Factory for creating appropriate LLM adapters"""
    
    _adapters = {}
    
    @classmethod
    def register_adapter(cls, provider: ProviderType, adapter_class):
        """Register an adapter class for a provider"""
        cls._adapters[provider] = adapter_class
    
    @classmethod
    def create_adapter(cls, provider: ProviderType, api_key: str, **kwargs) -> BaseLLMAdapter:
        """Create an adapter instance for the specified provider"""
        if provider not in cls._adapters:
            raise ValueError(f"Unsupported provider: {provider}")
        
        adapter_class = cls._adapters[provider]
        return adapter_class(api_key=api_key, **kwargs)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get list of supported providers"""
        return [p.value for p in cls._adapters.keys()]


def retry_with_exponential_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """Decorator for retrying failed API calls with exponential backoff"""
    def wrapper(*args, **kwargs):
        delay = initial_delay
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= exponential_base
                
                if jitter:
                    import random
                    delay *= (0.5 + random.random())
        
    return wrapper
