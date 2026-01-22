"""
Custom LLM API Adapter
Supports any OpenAI-compatible API endpoint
Enables users to configure custom providers like:
- Local LLMs (Ollama, LM Studio)
- Alternative cloud providers (Together AI, Replicate, Fireworks AI)
- Self-hosted models
- Any OpenAI-compatible endpoint
"""

from typing import List, Dict, Any
from PIL import Image
import base64
import io

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse,
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class CustomLLMAdapter(BaseLLMAdapter):
    """Adapter for custom OpenAI-compatible API endpoints"""
    
    def __init__(self, api_key: str, base_url: str = None, provider_name: str = "Custom", **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.OPENAI  # Use OpenAI type for compatibility
        self.provider_name = provider_name
        self.base_url = base_url or "https://api.openai.com/v1"
        self.default_model = kwargs.get('default_model', 'gpt-4o')
        self.custom_headers = kwargs.get('custom_headers', {})
        
        # Initialize OpenAI client with custom base URL
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.base_url,
                default_headers=self.custom_headers
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def get_available_models(self) -> List[str]:
        """Get available models from the custom endpoint"""
        try:
            # Try to fetch models from the API
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception:
            # If API doesn't support model listing, return default
            return [self.default_model]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for custom models"""
        # Default capabilities - can be customized per provider
        return ModelCapabilities(
            supports_vision=True,  # Assume vision support
            supports_streaming=True,
            supports_function_calling=True,
            max_tokens=4096,
            cost_per_1k_input_tokens=0.0,  # Unknown cost
            cost_per_1k_output_tokens=0.0
        )
    
    def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    @retry_with_exponential_backoff
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using custom OpenAI-compatible API"""
        import time
        
        # Validate request
        self.validate_request(request)
        
        model_name = request.model or self.default_model
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
        if request.images:
            # Multimodal message with images
            content = []
            
            # Add images
            for img in request.images:
                # Ensure RGB mode
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Encode image to base64
                img_base64 = self._encode_image(img)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": img_base64
                    }
                })
            
            # Add text prompt
            content.append({
                "type": "text",
                "text": request.prompt
            })
            
            messages.append({
                "role": "user",
                "content": content
            })
        else:
            # Text-only message
            messages.append({
                "role": "user",
                "content": request.prompt
            })
        
        # Make API call
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            end_time = time.time()
            latency = end_time - start_time
            
            # Extract response data
            response_text = response.choices[0].message.content
            
            # Get token usage
            input_tokens = getattr(response.usage, 'prompt_tokens', 0) if hasattr(response, 'usage') else 0
            output_tokens = getattr(response.usage, 'completion_tokens', 0) if hasattr(response, 'usage') else 0
            
            cost = self.calculate_cost(input_tokens, output_tokens, model_name)
            
            return LLMResponse(
                text=response_text,
                provider=self.provider_name,
                model=model_name,
                latency=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                metadata={
                    "finish_reason": response.choices[0].finish_reason if response.choices else None,
                    "base_url": self.base_url
                }
            )
        except Exception as e:
            # Provide helpful error message
            error_msg = str(e)
            if "404" in error_msg:
                raise ValueError(f"Model '{model_name}' not found at {self.base_url}. Check model name and endpoint.")
            elif "401" in error_msg or "403" in error_msg:
                raise ValueError(f"Authentication failed for {self.base_url}. Check your API key.")
            elif "connection" in error_msg.lower():
                raise ValueError(f"Cannot connect to {self.base_url}. Check the base URL and your internet connection.")
            else:
                raise ValueError(f"Error calling custom API: {error_msg}")


# Register adapter with factory
from utils.llm_adapter import LLMAdapterFactory, ProviderType

# Note: Custom adapters are registered dynamically when created
# This allows multiple custom providers with different configurations
