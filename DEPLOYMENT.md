# MedDiag Gemini 3 - Deployment Guide

Complete guide for deploying MedDiag to various platforms with custom LLM provider support.

---

## 🚀 Quick Deploy to Streamlit Cloud (Recommended)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)
- At least one LLM API key (Gemini recommended - free tier available)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "MedDiag Gemini 3 - Production Ready"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Sign in with GitHub

2. **Create New App**
   - Click "New app"
   - Select your repository: `MedDiag-Gemini3-Hackathon`
   - Branch: `main`
   - Main file path: `app.py`

3. **Configure Secrets**
   - Click "Advanced settings"
   - In "Secrets" section, paste (use `.streamlit/secrets.toml.example` as template):
   
   ```toml
   # Minimum configuration (at least one provider)
   GEMINI_API_KEY = "AIzaSy..."
   
   # Optional: Add more providers
   GROQ_API_KEY = "gsk_..."
   OPENAI_API_KEY = "sk-..."
   
   # Defaults
   DEFAULT_PROVIDER = "gemini"
   DEFAULT_MODEL = "gemini-2.0-flash-exp"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait 2-3 minutes for deployment

5. **Access Your App**
   - Your app will be live at: `https://<your-app-name>.streamlit.app`

---

## 🐳 Deploy with Docker

### Build and Run

```bash
# Build image
docker build -t meddiag-gemini3 .

# Run container
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_key_here \
  meddiag-gemini3
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  meddiag:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
    env_file:
      - .env
```

Run: `docker-compose up`

---

## 🤗 Deploy to Hugging Face Spaces

1. **Create New Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Select "Streamlit" as SDK

2. **Push Repository**
   ```bash
   git remote add hf https://huggingface.co/spaces/<username>/<space-name>
   git push hf main
   ```

3. **Add Secrets**
   - Go to Space Settings → Repository Secrets
   - Add `GEMINI_API_KEY` and other API keys

---

## 🌐 Custom Provider Setup

### Option 1: Via UI (Recommended)
1. Start the app
2. Go to sidebar → "🔧 Custom Provider"
3. Click "➕ Add Custom Provider"
4. Fill in:
   - Provider Name (e.g., "My Ollama")
   - Base URL (e.g., `http://localhost:11434/v1`)
   - API Key (use `not-needed` for local)
   - Default Model (e.g., `llama3`)
5. Click "Add Provider"

### Option 2: Via Environment Variables
Add to `.env` or Streamlit Secrets:

```bash
# Local Ollama
CUSTOM_OLLAMA_NAME="Local Ollama"
CUSTOM_OLLAMA_BASE_URL=http://localhost:11434/v1
CUSTOM_OLLAMA_API_KEY=not-needed
CUSTOM_OLLAMA_MODEL=llama3

# Together AI
CUSTOM_TOGETHER_NAME="Together AI"
CUSTOM_TOGETHER_BASE_URL=https://api.together.xyz/v1
CUSTOM_TOGETHER_API_KEY=your_key
CUSTOM_TOGETHER_MODEL=meta-llama/Llama-3-70b-chat-hf
```

### Popular Custom Providers

| Provider | Base URL | Notes |
|----------|----------|-------|
| **Ollama** | `http://localhost:11434/v1` | Local, free, OpenAI-compatible |
| **LM Studio** | `http://localhost:1234/v1` | Local, GUI-based |
| **Together AI** | `https://api.together.xyz/v1` | Cloud, affordable |
| **Fireworks AI** | `https://api.fireworks.ai/inference/v1` | Fast inference |
| **Replicate** | Use OpenRouter | Via OpenRouter gateway |

---

## 🔒 Security Best Practices

✅ **DO:**
- Use Streamlit Secrets for API keys in cloud deployments
- Use `.env` file locally (gitignored)
- Rotate API keys regularly
- Use environment-specific keys (dev/prod)

❌ **DON'T:**
- Commit `.env` to version control
- Hardcode API keys in code
- Share API keys in screenshots
- Use production keys in development

---

## 🛠️ Troubleshooting

### Issue: App won't start

**Solution:**
- Verify `requirements.txt` dependencies are correct
- Check Python version compatibility (3.10+)
- Ensure at least one API key is configured

### Issue: "No API keys found"

**Solution:**
- Check Streamlit Secrets or `.env` file
- Verify key format matches provider requirements
- Try entering key via UI instead

### Issue: Custom provider connection fails

**Solution:**
- Verify base URL is correct and accessible
- Check if endpoint is OpenAI-compatible
- Test with `curl` first:
  ```bash
  curl http://localhost:11434/v1/models \
    -H "Authorization: Bearer not-needed"
  ```
- Ensure model name matches available models

### Issue: Slow performance

**Solution:**
- Use faster providers (Groq, Gemini Flash)
- Reduce image resolution
- Enable Streamlit caching
- Upgrade to Streamlit Cloud Teams

### Issue: Rate limits

**Solution:**
- Use providers with higher limits (Groq has generous free tier)
- Implement request queuing
- Use multiple API keys with rotation

---

## 📊 Production Checklist

Before deploying to production:

- [ ] All dependencies pinned in `requirements.txt`
- [ ] At least one API key configured
- [ ] `.env` file gitignored
- [ ] Error handling tested
- [ ] Custom providers tested (if used)
- [ ] Medical disclaimer visible
- [ ] Analytics configured (optional)
- [ ] Monitoring set up (optional)
- [ ] Backup API provider configured
- [ ] Rate limiting considered

---

## 🎯 Platform Comparison

| Platform | Cost | Ease | Custom Providers | Best For |
|----------|------|------|------------------|----------|
| **Streamlit Cloud** | Free | ⭐⭐⭐⭐⭐ | ✅ (via UI) | Quick demos |
| **Docker** | Varies | ⭐⭐⭐ | ✅ Full support | Production |
| **Hugging Face** | Free | ⭐⭐⭐⭐ | ✅ (via secrets) | ML community |
| **AWS/GCP/Azure** | Pay-as-go | ⭐⭐ | ✅ Full support | Enterprise |

---

## 🆘 Support

- **GitHub Issues:** Report bugs and feature requests
- **Documentation:** See `README.md` and `CUSTOM_PROVIDER_GUIDE.md`
- **Community:** Hugging Face Spaces discussions

---

**Your deployed app URL is your submission link!**

Example: `https://meddiag-gemini3.streamlit.app`

Good luck! 🏆
