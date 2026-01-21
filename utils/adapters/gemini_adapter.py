"""
Google Gemini API Adapter
Supports Gemini 2.0, Gemini 1.5 Pro/Flash models
"""

from typing import List, Dict, Any
from PIL import Image

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse,
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class GeminiAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini API"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.GEMINI
        self.default_model = "gemini-2.0-flash-exp"
        
        # Initialize Gemini client
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    def get_available_models(self) -> List[str]:
        """Get available Gemini models"""
        return [
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b"
        ]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for Gemini models"""
        capabilities_map = {
            "gemini-2.0-flash-exp": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.0,  # Free tier
                cost_per_1k_output_tokens=0.0
            ),
            "gemini-1.5-pro": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.00125,
                cost_per_1k_output_tokens=0.005
            ),
            "gemini-1.5-flash": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.000075,
                cost_per_1k_output_tokens=0.0003
            ),
            "gemini-1.5-flash-8b": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.0000375,
                cost_per_1k_output_tokens=0.00015
            )
        }
        return capabilities_map.get(model, ModelCapabilities())
    
    @retry_with_exponential_backoff
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Gemini API"""
        import time
        
        # Validate request
        self.validate_request(request)
        
        model_name = request.model or self.default_model
        start_time = time.time()
        
        # Create model instance
        model = self.genai.GenerativeModel(model_name)
        
        # Prepare content parts
        content_parts = []
        
        # Add images if provided
        if request.images:
            for img in request.images:
                # Ensure RGB mode
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                content_parts.append(img)
        
        # Add prompt (with system prompt if provided)
        if request.system_prompt:
            full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
        else:
            full_prompt = request.prompt
        
        content_parts.append(full_prompt)
        
        # Make API call
        response = model.generate_content(
            content_parts,
            generation_config=self.genai.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens
            )
        )
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Extract response data
        response_text = response.text
        
        # Gemini doesn't always provide token counts, estimate if needed
        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0
        
        cost = self.calculate_cost(input_tokens, output_tokens, model_name)
        
        return LLMResponse(
            text=response_text,
            provider="Google Gemini",
            model=model_name,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata={
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else None
            }
        )


# Register adapter with factory
from utils.llm_adapter import LLMAdapterFactory
LLMAdapterFactory.register_adapter(ProviderType.GEMINI, GeminiAdapter)
