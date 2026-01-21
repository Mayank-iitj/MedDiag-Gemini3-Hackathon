"""
Anthropic (Claude) API Adapter
Supports Claude 3 models (Opus, Sonnet, Haiku)
"""

from typing import List, Dict, Any
import base64
import io
from PIL import Image

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse,
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude API"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.ANTHROPIC
        self.default_model = "claude-3-5-sonnet-20241022"
        
        # Initialize Anthropic client
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def get_available_models(self) -> List[str]:
        """Get available Claude models"""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for Claude models"""
        capabilities_map = {
            "claude-3-5-sonnet-20241022": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.003,
                cost_per_1k_output_tokens=0.015
            ),
            "claude-3-opus-20240229": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.015,
                cost_per_1k_output_tokens=0.075
            ),
            "claude-3-sonnet-20240229": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.003,
                cost_per_1k_output_tokens=0.015
            ),
            "claude-3-haiku-20240307": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.00025,
                cost_per_1k_output_tokens=0.00125
            )
        }
        return capabilities_map.get(model, ModelCapabilities())
    
    def _prepare_image_content(self, images: List[Image.Image]) -> List[Dict]:
        """Convert PIL images to Anthropic format"""
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
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_base64
                }
            })
        
        return image_contents
    
    @retry_with_exponential_backoff
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic API"""
        import time
        
        # Validate request
        self.validate_request(request)
        
        model = request.model or self.default_model
        start_time = time.time()
        
        # Prepare content
        content = []
        
        # Add images if provided
        if request.images:
            content.extend(self._prepare_image_content(request.images))
        
        # Add text prompt
        content.append({
            "type": "text",
            "text": request.prompt
        })
        
        # Make API call
        response = self.client.messages.create(
            model=model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system=request.system_prompt or "",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Extract response data
        response_text = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        return LLMResponse(
            text=response_text,
            provider="Anthropic",
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata={
                "stop_reason": response.stop_reason
            }
        )


# Register adapter with factory
from utils.llm_adapter import LLMAdapterFactory
LLMAdapterFactory.register_adapter(ProviderType.ANTHROPIC, AnthropicAdapter)
