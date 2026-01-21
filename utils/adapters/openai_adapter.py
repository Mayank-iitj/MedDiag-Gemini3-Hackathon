"""
OpenAI API Adapter
Supports GPT-4, GPT-4 Vision, GPT-3.5 models
"""

from typing import List, Dict, Any
import base64
import io
from PIL import Image

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse, 
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI API"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.OPENAI
        self.default_model = "gpt-4o"
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4-vision-preview",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for OpenAI models"""
        capabilities_map = {
            "gpt-4o": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.005,
                cost_per_1k_output_tokens=0.015
            ),
            "gpt-4o-mini": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=16384,
                cost_per_1k_input_tokens=0.00015,
                cost_per_1k_output_tokens=0.0006
            ),
            "gpt-4-turbo": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.01,
                cost_per_1k_output_tokens=0.03
            ),
            "gpt-4-vision-preview": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=False,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.01,
                cost_per_1k_output_tokens=0.03
            ),
            "gpt-4": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.03,
                cost_per_1k_output_tokens=0.06
            ),
            "gpt-3.5-turbo": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.0005,
                cost_per_1k_output_tokens=0.0015
            )
        }
        return capabilities_map.get(model, ModelCapabilities())
    
    def _prepare_image_content(self, images: List[Image.Image]) -> List[Dict]:
        """Convert PIL images to OpenAI format"""
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
                    "url": f"data:image/png;base64,{img_base64}",
                    "detail": "high"
                }
            })
        
        return image_contents
    
    @retry_with_exponential_backoff
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
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
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        return LLMResponse(
            text=response_text,
            provider="OpenAI",
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
LLMAdapterFactory.register_adapter(ProviderType.OPENAI, OpenAIAdapter)
