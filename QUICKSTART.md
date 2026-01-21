# 🚀 Quick Start Guide

## Getting Started in 3 Steps

### 1️⃣ Get Your Gemini 3 API Key
Visit: https://aistudio.google.com/app/apikey
- Sign in with Google account
- Click "Create API Key"
- Copy your API key

### 2️⃣ Install Dependencies
```bash
cd C:\Users\MS\.gemini\antigravity\scratch\MedDiag-Gemini3-Hackathon
pip install -r requirements.txt
```

### 3️⃣ Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Using the Application

1. **Enter API Key**: Paste your Gemini 3 API key in the sidebar
2. **Try Demo Mode**: Toggle "Load Sample Case" for instant testing
3. **Or Upload Custom Data**:
   - Upload medical images (X-rays, CT, MRI)
   - Enter clinical notes and patient history
4. **Click Analyze**: Wait 5-10 seconds for Gemini 3 analysis
5. **Explore Results**:
   - View differential diagnoses with reasoning
   - Check interactive timeline chart
   - See urgency gauge
   - Ask follow-up "what-if" questions
   - Export reports as JSON or text

## Deployment to Streamlit Cloud

1. **Create GitHub repo** and push your code:
   ```bash
   git init
   git add .
   git commit -m "MedDiag Gemini 3 Hackathon"
   git remote add origin https://github.com/YOUR_USERNAME/MedDiag-Gemini3-Hackathon.git
   git push -u origin main
   ```

2. **Deploy**:
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository
   - Main file: `app.py`
   - Add Secret: `GEMINI_API_KEY = "your_key"`
   - Deploy!

## Troubleshooting

**Dependencies won't install?**
- Try: `pip install --upgrade pip`
- Or use conda: `conda install -c conda-forge streamlit google-generativeai plotly pandas pillow`

**App won't start?**
- Verify you're in the correct directory
- Check Python version: `python --version` (need 3.10+)

**API errors?**
- Verify your API key is valid
- Check internet connection
- Ensure you're using a Gemini 3 model name

## Features to Showcase

✅ Multimodal input (images + text)
✅ Gemini 3 structured reasoning
✅ Interactive Plotly visualizations
✅ Agentic follow-up chat
✅ English/Hindi multilingual support
✅ JSON & text export
✅ One-click demo mode

## Recommended Workspace

Would you like to set this as your active workspace? Open:
`C:\Users\MS\.gemini\antigravity\scratch\MedDiag-Gemini3-Hackathon`
