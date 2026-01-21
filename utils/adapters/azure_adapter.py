"""
Azure OpenAI API Adapter
Enterprise Azure OpenAI support
"""

from typing import List, Dict, Any
import base64
import io
from PIL import Image

from utils.llm_adapter import (
    BaseLLMAdapter, LLMRequest, LLMResponse,
    ModelCapabilities, ProviderType, retry_with_exponential_backoff
)


class AzureOpenAIAdapter(BaseLLMAdapter):
    """Adapter for Azure OpenAI API"""
    
    def __init__(self, api_key: str, endpoint: str = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.provider_type = ProviderType.AZURE
        self.default_model = "gpt-4o"
        self.endpoint = endpoint
        
        if not endpoint:
            raise ValueError("Azure OpenAI endpoint is required")
        
        # Initialize Azure OpenAI client
        try:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=api_key,
                azure_endpoint=endpoint,
                api_version="2024-02-15-preview"
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def get_available_models(self) -> List[str]:
        """Get available Azure OpenAI deployments"""
        # Note: These are deployment names, not model names
        return [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4-vision",
            "gpt-4",
            "gpt-35-turbo"
        ]
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for Azure OpenAI models"""
        capabilities_map = {
            "gpt-4o": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.005,
                cost_per_1k_output_tokens=0.015
            ),
            "gpt-4-turbo": ModelCapabilities(
                supports_vision=True,
                supports_streaming=True,
                supports_function_calling=True,
                max_tokens=4096,
                cost_per_1k_input_tokens=0.01,
                cost_per_1k_output_tokens=0.03
            ),
            "gpt-4-vision": ModelCapabilities(
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
            "gpt-35-turbo": ModelCapabilities(
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
        """Convert PIL images to Azure OpenAI format"""
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
        """Generate response using Azure OpenAI API"""
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
            model=model,  # This is the deployment name in Azure
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
            provider="Azure OpenAI",
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
LLMAdapterFactory.register_adapter(ProviderType.AZURE, AzureOpenAIAdapter)
