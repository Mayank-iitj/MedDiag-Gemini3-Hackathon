"""
Groq API Adapter
Supports ultra-fast inference with Llama, Mixtral, and Gemma models
"""

from typing import List, Dict, Any
import base64
import io
from PIL import Image

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse,
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class GroqAdapter(BaseLLMAdapter):
    """Adapter for Groq API (ultra-fast inference)"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.GROQ
        self.default_model = "llama-3.3-70b-versatile"
        
        # Initialize Groq client (OpenAI-compatible)
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def get_available_models(self) -> List[str]:
        """Get available Groq models"""
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
            "llama-3.2-90b-vision-preview",  # Vision support
            "llama-3.2-11b-vision-preview"   # Vision support
        ]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for Groq models"""
        # Vision models
        vision_models = [
            "llama-3.2-90b-vision-preview",
            "llama-3.2-11b-vision-preview"
        ]
        
        supports_vision = model in vision_models
        
        # Model-specific configurations
        capabilities_map = {
            "llama-3.3-70b-versatile": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.00059,
                cost_per_1k_output_tokens=0.00079
            ),
            "llama-3.1-70b-versatile": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.00059,
                cost_per_1k_output_tokens=0.00079
            ),
            "llama-3.1-8b-instant": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.00005,
                cost_per_1k_output_tokens=0.00008
            ),
            "mixtral-8x7b-32768": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=32768,
                cost_per_1k_input_tokens=0.00024,
                cost_per_1k_output_tokens=0.00024
            ),
            "gemma2-9b-it": ModelCapabilities(
                supports_vision=False,
                supports_streaming=True,
                supports_function_calling=False,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.0002,
                cost_per_1k_output_tokens=0.0002
            ),
            "llama-3.2-90b-vision-preview": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=False,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.0009,
                cost_per_1k_output_tokens=0.0009
            ),
            "llama-3.2-11b-vision-preview": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=False,
                max_tokens=8192,
                cost_per_1k_input_tokens=0.00018,
                cost_per_1k_output_tokens=0.00018
            )
        }
        
        return capabilities_map.get(model, ModelCapabilities(
            supports_vision=supports_vision,
            supports_streaming=True,
            max_tokens=8192
        ))
    
    def _prepare_image_content(self, images: List[Image.Image]) -> List[Dict]:
        """Convert PIL images to Groq format"""
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
        """Generate response using Groq API"""
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
            "content": user_content if request.images else request.prompt
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
            provider="Groq",
            model=model,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "speed": "ultra-fast" if latency < 1.0 else "fast"
            }
        )


# Register adapter with factory
from utils.llm_adapter import LLMAdapterFactory
LLMAdapterFactory.register_adapter(ProviderType.GROQ, GroqAdapter)
