# 🩺 MedDiag Gemini 3: Multimodal Medical Diagnostic Aid

[![Gemini 3 Hackathon](https://img.shields.io/badge/Gemini%203-Hackathon%20Submission-purple?style=for-the-badge)](https://aistudio.google.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)

**MedDiag Gemini 3** is a production-ready, AI-assisted clinical decision support tool that leverages Gemini 3's superior multimodal vision understanding and structured medical reasoning capabilities. Built exclusively with the Gemini 3 API, this application demonstrates the power of advanced AI in healthcare workflows.

## 🌟 What It Does

MedDiag accepts **medical images** (X-rays, CT scans, MRI), **clinical notes**, and **patient history** to generate:

- **Ranked Differential Diagnoses** with probability estimates
- **Step-by-Step Clinical Reasoning** explaining each diagnosis
- **Risk & Urgency Indicators** (Routine/Urgent/Critical)
- **Interactive Disease Progression Timelines**
- **Actionable Next-Test Recommendations**
- **Agentic Follow-up Chat** for "what-if" scenario exploration

## 🚀 Why Gemini 3?

This application showcases Gemini 3's unique strengths:

- **Multimodal Vision Understanding**: Simultaneously analyzes medical images and text
- **Structured Reasoning**: Produces consistent JSON outputs with detailed clinical logic
- **Low-Latency Inference**: Real-time analysis in 2-5 seconds
- **Interactive Intelligence**: Supports follow-up queries to refine differential diagnoses
- **Multilingual Capabilities**: English and Hindi medical reasoning

## 💡 Innovation Highlights

1. **Multimodal Fusion**: Combines visual radiological findings with clinical history for comprehensive analysis
2. **Explainable AI**: Transparent step-wise reasoning shows evidence for and against each diagnosis
3. **Timeline Visualization**: Interactive Plotly charts reveal disease progression probabilities over time
4. **Agentic Chat**: Dynamic follow-up questions allow clinicians to explore alternative scenarios
5. **Zero-Authentication Demo**: Public-ready deployment for instant accessibility

## 🌍 Real-World Impact

**MedDiag Gemini 3** addresses critical healthcare challenges:

- **Reduces Diagnostic Overload**: Helps clinicians prioritize high-risk cases
- **Democratizes Clinical AI**: Free, accessible tool for under-resourced medical facilities
- **Accelerates Decision-Making**: Rapid differential generation supports time-critical cases
- **Educational Value**: Transparent reasoning aids medical training and continuing education

⚠️ **Medical Disclaimer**: This is a decision-support tool, NOT a replacement for professional medical diagnosis. Always consult qualified healthcare providers.

## 📦 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/MedDiag-Gemini3-Hackathon.git
cd MedDiag-Gemini3-Hackathon
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Get your free Gemini 3 API key: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_api_key_here
```

### 4. Run Application
```bash
streamlit run app.py
```

## 🎬 Demo & Video

- **Live Demo**: [Streamlit Cloud Deployment](#) *(add link after deployment)*
- **3-Minute Video Walkthrough**: [YouTube Demo](#) *(add link)*

## 🏗️ Technical Architecture

```
MedDiag-Gemini3-Hackathon/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Dependencies
├── .env.example              # API key template
├── .streamlit/
│   └── config.toml           # Streamlit theme
├── assets/
│   └── sample_xray.jpg       # Demo medical image
└── utils/
    ├── prompt_builder.py     # Medical prompt engineering
    ├── json_parser.py        # Robust JSON parsing
    └── viz_helpers.py        # Plotly visualizations
```

**Core Technologies**:
- **Streamlit 1.38.0**: Interactive web UI
- **Google Generative AI 0.8.3**: Gemini 3 API client
- **Plotly 5.24.1**: Interactive medical visualizations
- **Pandas 2.2.3**: Data table formatting

## 🎯 Deployment

### Streamlit Cloud (Recommended)
1. Push repository to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Deploy from repository
4. Add `GEMINI_API_KEY` to Secrets (TOML format)

### Vercel
```bash
# Export as static site (requires streamlit-export)
streamlit run app.py --server.headless true
```

### Hugging Face Spaces
1. Create new Space with Streamlit SDK
2. Push repository
3. Add `GEMINI_API_KEY` to Settings → Repository Secrets

## 🏆 Hackathon Alignment

| Criterion | Implementation |
|-----------|----------------|
| **Technical Excellence (40%)** | Clean Gemini 3 integration, robust error handling, structured JSON parsing |
| **Innovation (30%)** | Timeline visualization, agentic chat, multimodal fusion reasoning |
| **Real-world Impact (20%)** | Clinical decision support, accessible AI for healthcare |
| **Presentation (10%)** | Clean UI, instant demo mode, comprehensive documentation |

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built exclusively with **Gemini 3 API** for the Gemini 3 Hackathon. Powered by Google's cutting-edge multimodal AI technology.

---

<div align="center">
  <strong>🩺 Advancing Healthcare with Gemini 3 AI</strong><br>
  <em>For educational and decision-support purposes only</em>
</div>
