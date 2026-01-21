# MedDiag Gemini 3 - Streamlit Cloud Deployment Guide

## 🚀 Quick Deploy to Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)
- This repository pushed to GitHub

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - MedDiag Gemini 3"
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
   - In "Secrets" section, paste:
   ```toml
   GEMINI_API_KEY = "AIzaSyBHbUvWhkdAdaKDq9WOxrCSdJOkugr6mfg"
   DEFAULT_API = "gemini"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait 2-3 minutes for deployment

### Step 3: Access Your App
Your app will be live at: `https://<your-app-name>.streamlit.app`

## 🔒 Security Notes

- ✅ API keys are stored in Streamlit Secrets (encrypted)
- ✅ `.env` file is gitignored (never committed)
- ✅ Keys are hidden in UI
- ✅ Production-ready security

## 📝 Post-Deployment

1. **Test the app** with demo cases
2. **Share the URL** with hackathon judges
3. **Monitor usage** in Streamlit Cloud dashboard

## 🛠️ Troubleshooting

**Issue**: App won't start
- Check that all dependencies are in `requirements.txt`
- Verify secrets are correctly formatted

**Issue**: API errors
- Confirm API key is valid
- Check Gemini API quota limits

**Issue**: Slow performance
- Streamlit Cloud free tier has resource limits
- Consider upgrading for production use

## 📊 Features Enabled

- ✅ Multimodal medical image analysis
- ✅ 21 demo cases with unique X-ray images
- ✅ Interactive visualizations
- ✅ Follow-up chat functionality
- ✅ Export capabilities
- ✅ Dark mode theme
- ✅ Mobile responsive

## 🎯 Hackathon Submission

Your deployed app URL is your submission link!

**Example**: `https://meddiag-gemini3.streamlit.app`

Good luck! 🏆
