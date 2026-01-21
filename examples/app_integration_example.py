"""
Updated app.py integration code
This file contains the updated sidebar configuration section for app.py
to use the new universal LLM adapter system
"""

# Add these imports at the top of app.py (after existing imports)
from utils.llm_helpers import (
    create_llm_adapter,
    generate_with_llm,
    get_available_providers_info,
    get_provider_models
)
from config.llm_config import LLMConfig

# Replace the sidebar configuration section (lines 100-154) with this:

# Sidebar
with st.sidebar:
    st.markdown('<div class="hackathon-badge">🏆 Gemini 3 Hackathon Submission<br>Built with Universal LLM Adapter</div>', unsafe_allow_html=True)
    
    st.markdown("### ⚙️ LLM Provider Configuration")
    
    # Get available providers
    available_providers = get_available_providers_info()
    
    if not available_providers:
        st.error("⚠️ No API keys found! Please add at least one API key to your .env file")
        st.info("""
        Add one or more of these to your .env file:
        - OPENAI_API_KEY
        - ANTHROPIC_API_KEY
        - GEMINI_API_KEY
        - COHERE_API_KEY
        - OPENROUTER_API_KEY
        - AZURE_OPENAI_KEY + AZURE_OPENAI_ENDPOINT
        - HUGGINGFACE_API_KEY
        """)
        st.session_state.llm_adapter = None
    else:
        # Provider selection
        provider_options = {
            f"{info['icon']} {info['display_name']}": provider_id 
            for provider_id, info in available_providers.items()
        }
        
        default_provider = LLMConfig.get_default_provider()
        default_index = list(provider_options.values()).index(default_provider) if default_provider in provider_options.values() else 0
        
        selected_provider_display = st.selectbox(
            "Select LLM Provider",
            options=list(provider_options.keys()),
            index=default_index,
            help="Choose which LLM provider to use for analysis"
        )
        
        selected_provider = provider_options[selected_provider_display]
        provider_info = available_providers[selected_provider]
        
        # Model selection
        try:
            available_models = get_provider_models(selected_provider)
            
            if available_models:
                default_model = provider_info.get('default_model', available_models[0])
                model_index = available_models.index(default_model) if default_model in available_models else 0
                
                selected_model = st.selectbox(
                    "Select Model",
                    options=available_models,
                    index=model_index,
                    help="Choose which model to use"
                )
            else:
                selected_model = provider_info.get('default_model')
                st.info(f"Using default model: {selected_model}")
            
            # Create adapter
            st.session_state.llm_adapter = create_llm_adapter(selected_provider)
            st.session_state.selected_provider = selected_provider
            st.session_state.selected_model = selected_model
            
            # Show model capabilities
            caps = st.session_state.llm_adapter.get_model_capabilities(selected_model)
            
            capability_badges = []
            if caps.supports_vision:
                capability_badges.append("🖼️ Vision")
            if caps.supports_streaming:
                capability_badges.append("⚡ Streaming")
            if caps.supports_function_calling:
                capability_badges.append("🔧 Functions")
            
            if capability_badges:
                st.caption(f"Capabilities: {' • '.join(capability_badges)}")
            
            st.success(f"✓ {provider_info['display_name']} configured")
            
        except Exception as e:
            st.error(f"Error configuring provider: {str(e)}")
            st.session_state.llm_adapter = None
    
    st.markdown("---")
    
    # Rest of sidebar remains the same...
    # Language toggle, Demo mode, About section, etc.
