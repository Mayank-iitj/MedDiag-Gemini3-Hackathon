"""
Hugging Face API Adapter
Support for open-source models via Hugging Face Inference API
"""

from typing import List, Dict, Any
from PIL import Image

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse,
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class HuggingFaceAdapter(BaseLLMAdapter):
    """Adapter for Hugging Face Inference API"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.HUGGINGFACE
        self.default_model = "meta-llama/Meta-Llama-3-8B-Instruct"
        
        # Initialize Hugging Face client
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(token=api_key)
        except ImportError:
            raise ImportError("huggingface-hub package not installed. Run: pip install huggingface-hub")
    
    def get_available_models(self) -> List[str]:
        """Get available Hugging Face models"""
        return [
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "meta-llama/Meta-Llama-3-70B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.2",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "google/gemma-7b-it",
            "microsoft/Phi-3-mini-4k-instruct"
        ]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for Hugging Face models"""
        # Most HF models are text-only
        return ModelCapabilities(
            supports_vision=False,
            supports_streaming=True,
            supports_function_calling=False,
            max_tokens=4096,
            cost_per_1k_input_tokens=0.0,  # Free tier available
            cost_per_1k_output_tokens=0.0
        )
    
    @retry_with_exponential_backoff
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Hugging Face API"""
        import time
        
        # Validate request
        self.validate_request(request)
        
        model = request.model or self.default_model
        
        # Hugging Face Inference API doesn't support images for most models
        if request.images:
            raise ValueError(f"Hugging Face model {model} does not support image inputs")
        
        start_time = time.time()
        
        # Prepare message with system prompt if provided
        if request.system_prompt:
            full_prompt = f"System: {request.system_prompt}\n\nUser: {request.prompt}"
        else:
            full_prompt = request.prompt
        
        # Make API call
        response = self.client.text_generation(
            full_prompt,
            model=model,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            return_full_text=False
        )
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Extract response data
        response_text = response
        
        # HF doesn't always provide token counts, estimate
        input_tokens = len(full_prompt.split()) * 1.3  # Rough estimate
        output_tokens = len(response_text.split()) * 1.3
        
        cost = self.calculate_cost(int(input_tokens), int(output_tokens), model)
        
        return LLMResponse(
            text=response_text,
            provider="Hugging Face",
            model=model,
            latency=latency,
            input_tokens=int(input_tokens),
            output_tokens=int(output_tokens),
            cost=cost,
            metadata={}
        )


# Register adapter with factory
from utils.llm_adapter import LLMAdapterFactory
LLMAdapterFactory.register_adapter(ProviderType.HUGGINGFACE, HuggingFaceAdapter)
