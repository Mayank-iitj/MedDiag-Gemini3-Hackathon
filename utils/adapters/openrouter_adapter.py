"""
OpenRouter API Adapter
Multi-model access through OpenRouter
"""

from typing import List, Dict, Any
import base64
import io
from PIL import Image

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse,
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class OpenRouterAdapter(BaseLLMAdapter):
    """Adapter for OpenRouter API (multi-model access)"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.OPENROUTER
        self.default_model = "google/gemini-2.0-flash-exp:free"
        
        # Initialize OpenRouter client (OpenAI-compatible)
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def get_available_models(self) -> List[str]:
        """Get available models through OpenRouter"""
        return [
            # Gemini models
            "google/gemini-2.0-flash-exp:free",
            "google/gemini-pro-1.5",
            "google/gemini-flash-1.5",
            # OpenAI models
            "openai/gpt-4o",
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
            # Anthropic models
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-haiku",
            # Meta models
            "meta-llama/llama-3.1-405b-instruct",
            "meta-llama/llama-3.1-70b-instruct",
            # Mistral models
            "mistralai/mistral-large",
            "mistralai/mixtral-8x7b-instruct"
        ]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for models available through OpenRouter"""
        # Simplified capability mapping
        vision_models = [
            "google/gemini-2.0-flash-exp:free",
            "google/gemini-pro-1.5",
            "google/gemini-flash-1.5",
            "openai/gpt-4o",
            "openai/gpt-4-turbo",
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus"
        ]
        
        supports_vision = any(vm in model for vm in vision_models)
        
        return ModelCapabilities(
            supports_vision=supports_vision,
            supports_streaming=True,
            supports_function_calling=True,
            max_tokens=8192,
            cost_per_1k_input_tokens=0.0,  # Varies by model
            cost_per_1k_output_tokens=0.0
        )
    
    def _prepare_image_content(self, images: List[Image.Image]) -> List[Dict]:
        """Convert PIL images to OpenRouter format"""
        image_contents = []
        
        for img in images:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            image_contents.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}"
                }
            })
        
        return image_contents
    
    @retry_with_exponential_backoff
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenRouter API"""
        import time
        
        # Validate request
        self.validate_request(request)
        
        model = request.model or self.default_model
        start_time = time.time()
        
        # Prepare messages
        messages = []
        
        # Add system prompt if provided
        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })
        
        # Prepare user message content
        user_content = []
        
        # Add images if provided
        if request.images:
            user_content.extend(self._prepare_image_content(request.images))
        
        # Add text prompt
        user_content.append({
            "type": "text",
            "text": request.prompt
        })
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        # Make API call
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Extract response data
        response_text = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        return LLMResponse(
            text=response_text,
            provider="OpenRouter",
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata={
                "finish_reason": response.choices[0].finish_reason
            }
        )


# Register adapter with factory
from utils.llm_adapter import LLMAdapterFactory
LLMAdapterFactory.register_adapter(ProviderType.OPENROUTER, OpenRouterAdapter)
