"""
Cohere API Adapter
Supports Command R+, Command models
"""

from typing import List, Dict, Any
from PIL import Image

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse,
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class CohereAdapter(BaseLLMAdapter):
    """Adapter for Cohere API"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.COHERE
        self.default_model = "command-r-plus"
        
        # Initialize Cohere client
        try:
            import cohere
            self.client = cohere.Client(api_key=api_key)
        except ImportError:
            raise ImportError("cohere package not installed. Run: pip install cohere")
    
    def get_available_models(self) -> List[str]:
        """Get available Cohere models"""
        return [
            "command-r-plus",
            "command-r",
            "command",
            "command-light"
        ]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for Cohere models"""
        capabilities_map = {
            "command-r-plus": ModelCapabilities(
                supports_vision=False,  # Limited vision support
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.003,
                cost_per_1k_output_tokens=0.015
            ),
            "command-r": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.0005,
                cost_per_1k_output_tokens=0.0015
            ),
            "command": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=False,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.001,
                cost_per_1k_output_tokens=0.002
            ),
            "command-light": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=False,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.0003,
                cost_per_1k_output_tokens=0.0006
            )
        }
        return capabilities_map.get(model, ModelCapabilities())
    
    @retry_with_exponential_backoff
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Cohere API"""
        import time
        
        # Validate request
        self.validate_request(request)
        
        model = request.model or self.default_model
        
        # Cohere doesn't support images in the same way
        if request.images:
            raise ValueError(f"Cohere model {model} does not support image inputs")
        
        start_time = time.time()
        
        # Prepare message with system prompt if provided
        message = request.prompt
        if request.system_prompt:
            message = f"{request.system_prompt}\n\n{message}"
        
        # Make API call
        response = self.client.chat(
            model=model,
            message=message,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Extract response data
        response_text = response.text
        
        # Cohere provides token counts
        input_tokens = response.meta.tokens.input_tokens if hasattr(response.meta, 'tokens') else 0
        output_tokens = response.meta.tokens.output_tokens if hasattr(response.meta, 'tokens') else 0
        
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        return LLMResponse(
            text=response_text,
            provider="Cohere",
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata={
                "finish_reason": response.finish_reason if hasattr(response, 'finish_reason') else None
            }
        )


# Register adapter with factory
from utils.llm_adapter import LLMAdapterFactory
LLMAdapterFactory.register_adapter(ProviderType.COHERE, CohereAdapter)
