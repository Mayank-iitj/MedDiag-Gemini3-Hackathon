# Custom LLM Provider Guide

Complete guide for configuring custom LLM providers in MedDiag Gemini 3.

---

## 🎯 Overview

MedDiag supports **any OpenAI-compatible API endpoint**, enabling you to use:

- **Local LLMs** (Ollama, LM Studio, LocalAI)
- **Alternative Cloud Providers** (Together AI, Fireworks AI, Replicate)
- **Self-hosted Models** (vLLM, TGI, FastChat)
- **Custom Endpoints** (Your own API)

---

## 🚀 Quick Start

### Method 1: Via UI (Recommended)

1. Start the app: `streamlit run app.py`
2. Go to sidebar → **"🔧 Custom Provider"**
3. Click **"➕ Add Custom Provider"**
4. Fill in the form:
   - **Provider Name**: Display name (e.g., "My Local Ollama")
   - **Base URL**: API endpoint (e.g., `http://localhost:11434/v1`)
   - **API Key**: Authentication key (use `not-needed` for local)
   - **Default Model**: Model name (e.g., `llama3`)
5. Click **"💾 Add Provider"**
6. Select your custom provider from the dropdown

### Method 2: Via Environment Variables

Add to `.env` file:

```bash
# Pattern: CUSTOM_<NAME>_<FIELD>=value
CUSTOM_OLLAMA_NAME="Local Ollama"
CUSTOM_OLLAMA_BASE_URL=http://localhost:11434/v1
CUSTOM_OLLAMA_API_KEY=not-needed
CUSTOM_OLLAMA_MODEL=llama3
```

---

## 📖 Provider-Specific Guides

### Ollama (Local LLM)

**Setup:**
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. Verify it's running: `ollama list`

**Configuration:**
- **Provider Name**: `Local Ollama`
- **Base URL**: `http://localhost:11434/v1`
- **API Key**: `not-needed`
- **Default Model**: `llama3` (or any model you pulled)

**Supported Models:**
- `llama3`, `llama3.1`, `llama3.2`
- `mistral`, `mixtral`
- `gemma`, `phi3`
- `codellama`, `deepseek-coder`

**Notes:**
- Ollama provides OpenAI-compatible API at `/v1` endpoint
- No API key needed for local instances
- Image support varies by model

---

### LM Studio (Local GUI)

**Setup:**
1. Download LM Studio: https://lmstudio.ai
2. Download a model via the GUI
3. Start local server (default port: 1234)

**Configuration:**
- **Provider Name**: `LM Studio`
- **Base URL**: `http://localhost:1234/v1`
- **API Key**: `not-needed`
- **Default Model**: Check LM Studio UI for model name

**Notes:**
- LM Studio has a user-friendly GUI
- Good for beginners with local LLMs
- Automatically detects hardware (CPU/GPU)

---

### Together AI (Cloud)

**Setup:**
1. Sign up: https://together.ai
2. Get API key: https://api.together.xyz/settings/api-keys
3. Choose models: https://docs.together.ai/docs/inference-models

**Configuration:**
- **Provider Name**: `Together AI`
- **Base URL**: `https://api.together.xyz/v1`
- **API Key**: `your_together_api_key`
- **Default Model**: `meta-llama/Llama-3-70b-chat-hf`

**Popular Models:**
- `meta-llama/Llama-3-70b-chat-hf`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `google/gemma-2-27b-it`
- `Qwen/Qwen2-72B-Instruct`

**Pricing:**
- Pay-per-use
- Significantly cheaper than OpenAI
- Free trial credits available

---

### Fireworks AI (Cloud)

**Setup:**
1. Sign up: https://fireworks.ai
2. Get API key from dashboard
3. Browse models: https://fireworks.ai/models

**Configuration:**
- **Provider Name**: `Fireworks AI`
- **Base URL**: `https://api.fireworks.ai/inference/v1`
- **API Key**: `your_fireworks_api_key`
- **Default Model**: `accounts/fireworks/models/llama-v3-70b-instruct`

**Popular Models:**
- `accounts/fireworks/models/llama-v3-70b-instruct`
- `accounts/fireworks/models/mixtral-8x7b-instruct`
- `accounts/fireworks/models/qwen2-72b-instruct`

**Features:**
- Ultra-fast inference (optimized infrastructure)
- Competitive pricing
- Supports function calling

---

### OpenRouter (Multi-Model Gateway)

Already included as a built-in provider, but worth mentioning:

**Benefits:**
- Access 100+ models with one API key
- Automatic fallback
- Unified billing
- Rate limit management

**Configuration:**
- Use the built-in "OpenRouter" provider
- Get key: https://openrouter.ai/keys
- Select from hundreds of models

---

## 🔧 Advanced Configuration

### Custom Headers

Some endpoints require custom headers. Configure via environment:

```bash
CUSTOM_MYPROVIDER_NAME="My Provider"
CUSTOM_MYPROVIDER_BASE_URL=https://api.myprovider.com/v1
CUSTOM_MYPROVIDER_API_KEY=your_key
CUSTOM_MYPROVIDER_MODEL=gpt-4
# Note: Custom headers not yet supported via env vars
# Use UI or modify code directly for advanced headers
```

### Vision Model Support

Not all models support vision (images). To check:

1. Add your custom provider
2. Try uploading an image
3. If it fails, the model doesn't support vision

**Models with Vision Support:**
- OpenAI: `gpt-4o`, `gpt-4-turbo`
- Anthropic: `claude-3-5-sonnet`, `claude-3-opus`
- Google: `gemini-2.0-flash`, `gemini-1.5-pro`
- Some local models: LLaVA variants

### Local Model Recommendations

For medical imaging, consider:

| Model | Size | Performance | Vision | Best For |
|-------|------|-------------|--------|----------|
| **Llama 3 70B** | 40GB | ⭐⭐⭐⭐ | ❌ | Text analysis |
| **LLaVA-1.6 34B** | 20GB | ⭐⭐⭐ | ✅ | Image + text |
| **BioMistral 7B** | 4GB | ⭐⭐⭐ | ❌ | Medical text |
| **Mixtral 8x7B** | 24GB | ⭐⭐⭐⭐ | ❌ | General analysis |

---

## 🧪 Testing Your Custom Provider

### 1. Connection Test

```bash
# Test if endpoint is reachable
curl http://localhost:11434/v1/models \
  -H "Authorization: Bearer not-needed"
```

Expected response: JSON with model list

### 2. Simple Prompt Test

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer not-needed" \
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

Expected response: JSON with completion

### 3. Vision Test (if supported)

Use the MedDiag UI:
1. Add custom provider
2. Select it from dropdown
3. Upload a medical image
4. Enter clinical notes
5. Click "Analyze"

If successful, you'll see differential diagnoses!

---

## ❓ Troubleshooting

### Error: "Cannot connect to <URL>"

**Solutions:**
- Verify the base URL is correct
- Check if the server is running: `curl <base_url>/v1/models`
- For local: ensure no firewall blocking
- For remote: check internet connection

### Error: "Model '<name>' not found"

**Solutions:**
- List available models: `curl <base_url>/v1/models`
- Update the "Default Model" field
- Some providers require full model paths

### Error: "Authentication failed"

**Solutions:**
- Verify API key is correct
- For local endpoints, try `not-needed` or empty string
- Check if endpoint requires specific auth format

### Error: "Vision not supported"

**Solutions:**
- Use a vision-capable model (e.g., LLaVA, gpt-4o)
- Test with text-only analysis first
- Check model documentation for capabilities

### Slow Response Times

**Solutions:**
- For local: ensure GPU acceleration is enabled
- Use smaller models for faster inference
- Consider cloud providers for production
- Reduce image resolution

---

## 💡 Best Practices

### For Development
✅ Use local models (free, private)  
✅ Start with smaller models (faster iteration)  
✅ Test with demo cases first  
✅ Keep API keys in `.env` (gitignored)

### For Production
✅ Use cloud providers (reliable, scalable)  
✅ Configure backup providers  
✅ Monitor API usage and costs  
✅ Use Streamlit Secrets for deployment  
✅ Test thoroughly before launch

### For Medical Use
⚠️ **IMPORTANT:** This is a decision-support tool only  
✅ Always review AI outputs with medical professionals  
✅ Keep audit trails of analyses  
✅ Use HIPAA-compliant providers if handling real PHI  
✅ Consider on-premise deployment for sensitive data

---

## 📚 Additional Resources

- **Ollama Docs**: https://ollama.ai/docs
- **LM Studio Docs**: https://lmstudio.ai/docs
- **Together AI Docs**: https://docs.together.ai
- **Fireworks AI Docs**: https://docs.fireworks.ai
- **OpenRouter Docs**: https://openrouter.ai/docs

---

## 🆘 Still Having Issues?

1. Check the main `README.md`
2. Review `DEPLOYMENT.md`
3. Open a GitHub issue
4. Include:
   - Provider name
   - Base URL
   - Error message
   - Steps to reproduce

---

**Happy customizing! 🎉**
