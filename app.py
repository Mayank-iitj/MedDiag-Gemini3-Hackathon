"""
MedDiag Gemini 3: Multimodal Medical Diagnostic Aid
A production-ready AI-assisted clinical decision support tool powered by Gemini 3 API

MEDICAL DISCLAIMER: This tool is for educational and decision-support purposes only.
It is NOT a replacement for professional medical diagnosis or clinical judgment.
Always consult with qualified healthcare providers for patient care decisions.
"""

import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time
import os
from dotenv import load_dotenv
import json
from openai import OpenAI

# Import demo cases library
from demo_cases import DEMO_CASES

# Import utility modules
from utils.prompt_builder import build_diagnostic_prompt, build_followup_prompt
from utils.json_parser import parse_gemini_response
from utils.viz_helpers import (
    create_timeline_chart,
    create_urgency_gauge,
    create_differential_table,
    format_reasoning_steps,
    create_confidence_badge
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🩺 MedDiag Gemini 3",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clinical theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066CC;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .disclaimer {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .hackathon-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        font-weight: bold;
    }
    .finding-box {
        background-color: #F0F8FF;
        border-left: 4px solid #0066CC;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .stExpander {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'language' not in st.session_state:
    st.session_state.language = 'english'

# Sidebar
with st.sidebar:
    st.markdown('<div class="hackathon-badge">🏆 Gemini 3 Hackathon Submission<br>Built Exclusively with Gemini 3 API</div>', unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Configuration")
    
    # API Configuration
    default_api = os.getenv('DEFAULT_API', 'openrouter')
    
    # Check for OpenRouter API key first (but don't show it in UI for security)
    openrouter_key = os.getenv('OPENROUTER_API_KEY', '')
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    
    # Determine which API to use
    if openrouter_key and default_api == 'openrouter':
        # Show placeholder instead of actual key for security
        api_key = st.text_input(
            "OpenRouter API Key (Multi-Model Access)",
            type="password",
            value="",
            placeholder="●●●●●●●● (loaded from .env)",
            help="API key loaded securely from .env file"
        )
        # Use the actual key from .env if user didn't enter one
        if not api_key:
            api_key = openrouter_key
        api_type = "openrouter"
        st.info("🔀 Using OpenRouter API (supports Gemini, GPT-4, Claude, etc.)")
    else:
        api_key = st.text_input(
            "Gemini 3 API Key",
            type="password",
            value="",
            placeholder="●●●●●●●● (loaded from .env)" if gemini_key else "Enter your API key",
            help="Get your free API key from https://aistudio.google.com/app/apikey"
        )
        # Use the actual key from .env if user didn't enter one
        if not api_key and gemini_key:
            api_key = gemini_key
        api_type = "gemini"
    
    if api_key:
        if api_type == "gemini":
            genai.configure(api_key=api_key)
        elif api_type == "openrouter":
            # Initialize OpenRouter client (OpenAI-compatible)
            st.session_state.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
        st.session_state.api_type = api_type
        st.session_state.api_key = api_key
        st.success(f"✓ API Key configured ({api_type})")
    else:
        st.warning("⚠️ API Key required to run analysis")
    
    st.markdown("---")
    
    # Language toggle
    st.markdown("### 🌐 Language")
    language = st.selectbox(
        "Output Language",
        options=['English', 'Hindi (हिंदी)'],
        index=0
    )
    st.session_state.language = 'hindi' if 'Hindi' in language else 'english'
    
    st.markdown("---")
    
    # Demo mode
    st.markdown("### 🎯 Demo Mode")
    demo_mode = st.selectbox(
        "Select a demo case",
        options=["None"] + list(DEMO_CASES.keys()),
        index=0,
        help=f"Choose from {len(DEMO_CASES)} realistic medical scenarios"
    )
    
    if demo_mode != "None":
        st.success(f"✓ Loaded: {demo_mode}")

    
    st.markdown("---")
    
    # Information
    st.markdown("### ℹ️ About")
    st.info("""
    **MedDiag Gemini 3** uses multimodal AI to analyze medical images and clinical data, providing:
    
    • Ranked differential diagnoses
    • Step-by-step reasoning
    • Risk & urgency indicators
    • Diagnostic timelines
    • Next-test recommendations
    """)
    
    st.markdown("---")
    st.caption("Powered by Gemini 3 API | v1.0")

# Main content
st.markdown('<div class="main-header">🩺 MedDiag Gemini 3</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Multimodal Medical Diagnostic Aid</div>', unsafe_allow_html=True)

# Medical disclaimer
st.markdown("""
    <div style="background-color: rgba(30, 136, 229, 0.1); padding: 15px; border-radius: 5px; border-left: 4px solid #1e88e5; margin-bottom: 20px;">
    <p style="color: #1e88e5; margin: 0; font-size: 14px;">
    <strong>⚠️ MEDICAL DISCLAIMER:</strong> This tool is a decision-support and educational aid, NOT a replacement for professional medical diagnosis. 
    All outputs should be reviewed by qualified healthcare providers. Never use this for emergency medical decisions.
    </p>
    </div>
    """, unsafe_allow_html=True)

# Multimodal input interface
st.markdown("## 📥 Patient Data Input")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🖼️ Medical Images")
    
    if demo_mode != "None":
        # Load sample image from selected demo case
        sample_image_path = "assets/sample_xray.jpg"
        if os.path.exists(sample_image_path):
            uploaded_files = [sample_image_path]
            st.info(f"✓ Demo mode: {demo_mode}")
        else:
            uploaded_files = st.file_uploader(
                "Upload medical images (X-rays, CT, MRI, etc.)",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                help="Maximum 4 images, up to 5MB each"
            )
    else:
        uploaded_files = st.file_uploader(
            "Upload medical images (X-rays, CT, MRI, etc.)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Maximum 4 images, up to 5MB each"
        )
    
    # Display thumbnails
    if uploaded_files:
        if len(uploaded_files) > 4:
            st.warning("⚠️ Maximum 4 images allowed. Only first 4 will be analyzed.")
            uploaded_files = uploaded_files[:4]
        
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            with cols[idx]:
                if isinstance(file, str):  # Demo mode path
                    img = Image.open(file)
                else:
                    img = Image.open(file)
                st.image(img, caption=f"Image {idx+1}", width='stretch')

with col2:
    st.markdown("### 📝 Clinical Information")
    
    if demo_mode != "None":
        # Load selected demo case
        selected_case = DEMO_CASES[demo_mode]
        clinical_notes = selected_case["clinical_notes"]
        patient_history = selected_case["patient_history"]
    else:
        clinical_notes = ""
        patient_history = ""
    
    clinical_notes = st.text_area(
        "Clinical Notes & Symptoms",
        value=clinical_notes,
        height=200,
        placeholder="""Example:
Symptoms: fever, cough, chest pain
Vitals: BP 120/80, HR 110, SpO2 95%
Labs: WBC 15k, CRP elevated"""
    )
    
    patient_history = st.text_area(
        "Patient History",
        value=patient_history,
        height=150,
        placeholder="""Example:
Age: 45, Male
PMH: Diabetes, Hypertension
Meds: Metformin, Lisinopril
Social: Non-smoker"""
    )

# Validation and analysis button
st.markdown("---")

has_valid_input = (uploaded_files and len(uploaded_files) > 0) or clinical_notes.strip() or patient_history.strip()

if not has_valid_input:
    st.warning("⚠️ Please provide at least one input modality (images, clinical notes, or patient history)")

analyze_button = st.button(
    "🔬 Analyze & Generate Differential Diagnosis",
    type="primary",
    disabled=not (has_valid_input and api_key),
    width='stretch'
)

# Analysis execution
if analyze_button:
    with st.spinner("🧠 Gemini 3 is analyzing your case... This may take 10-30 seconds"):
        try:
            start_time = time.time()
            
            # Prepare multimodal content
            content_parts = []
            
            # Add images
            images = []
            if uploaded_files:
                for file in uploaded_files:
                    if isinstance(file, str):  # Demo mode
                        img = Image.open(file)
                    else:
                        img = Image.open(file)
                    
                    # Ensure RGB mode
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    images.append(img)
                    content_parts.append(img)
            
            # Build prompt
            prompt = build_diagnostic_prompt(
                clinical_notes=clinical_notes,
                patient_history=patient_history,
                language=st.session_state.language
            )
            
            # Call appropriate API
            api_type = st.session_state.get('api_type', 'gemini')
            
            if api_type == 'openrouter':
                # Use OpenRouter API (OpenAI-compatible)
                import base64
                
                # Convert images to base64 for OpenRouter
                image_contents = []
                for img in images:
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    image_contents.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        }
                    })
                
                # Create messages for OpenRouter
                messages = [
                    {
                        "role": "user",
                        "content": [
                            *image_contents,
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
                
                # Call OpenRouter with Gemini 2.0 (Gemini 3)
                client = st.session_state.openrouter_client
                completion = client.chat.completions.create(
                    model="google/gemini-2.0-flash-exp:free",  # Gemini 3 - latest model
                    messages=messages,
                    temperature=0.1,
                    max_tokens=8000
                )
                
                response_text = completion.choices[0].message.content
                
            else:
                # Use Google Gemini API directly
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                content_parts = []
                for img in images:
                    content_parts.append(img)
                content_parts.append(prompt)
                
                response = model.generate_content(
                    content_parts,
                    generation_config=genai.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=4000,
                    )
                )
                response_text = response.text
            
            end_time = time.time()
            latency = end_time - start_time
            
            # Parse response
            analysis_result = parse_gemini_response(response_text)
            analysis_result['latency'] = latency
            analysis_result['images'] = images
            
            st.session_state.analysis_result = analysis_result
            st.success(f"✓ Analysis completed in {latency:.2f} seconds")
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.info("💡 Troubleshooting tips:\n- Verify your API key is valid\n- Check your internet connection\n- Ensure images are valid and < 5MB\n- Try with fewer images")

# Display results
if st.session_state.analysis_result:
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    result = st.session_state.analysis_result
    
    # Latency display
    st.caption(f"⚡ Analysis completed in {result.get('latency', 0):.2f} seconds")
    
    # Two-column layout
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.markdown("### 🔍 Image Findings & Reasoning")
        # Findings
        st.markdown("### 🔬 Key Findings")
        findings = result.get('findings', [])
        if findings:
            for idx, finding in enumerate(findings, 1):
                st.markdown(f"""
                <div style='background-color: rgba(30, 136, 229, 0.05); padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #1e88e5;'>
                    <p style='color: #1e88e5; margin: 0;'><strong>Finding {idx}:</strong> {finding}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Differential diagnoses with reasoning
        st.markdown("<h3 style='color: #9c27b0;'>🧬 Differential Diagnoses</h3>", unsafe_allow_html=True)
        
        differentials = result.get('differentials', [])
        for diff in differentials:
            rank = diff.get('rank', '?')
            diagnosis = diff.get('diagnosis', 'Unknown')
            probability = diff.get('probability', 'N/A')
            
            with st.expander(f"**#{rank} - {diagnosis}** ({probability})", expanded=(rank == 1)):
                reasoning_steps = format_reasoning_steps(diff)
                
                for step in reasoning_steps:
                    st.markdown(f"**{step['title']}**")
                    st.markdown(step['content'])
                    st.markdown("")
    
    with right_col:
        st.markdown("### 📋 Summary Table")
        
        # Differential table
        df = create_differential_table(differentials)
        st.dataframe(df, width='stretch', hide_index=True)
        
        st.markdown("### 📈 Disease Progression Timeline")
        
        # Timeline chart
        timeline = result.get('timeline', {})
        if timeline.get('days'):
            fig_timeline = create_timeline_chart(timeline)
            st.plotly_chart(fig_timeline, width='stretch')
        else:
            st.info("Timeline data not available")
        
        st.markdown("### ⚠️ Urgency Assessment")
        
        # Urgency gauge
        urgency = result.get('urgency', 'Unknown')
        fig_gauge = create_urgency_gauge(urgency)
        st.plotly_chart(fig_gauge, width='stretch')
        
        # Confidence badge
        confidence = result.get('confidence', 'Unknown')
        st.markdown(create_confidence_badge(confidence), unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("---")
    st.markdown("### 💡 Recommendations")
    
    recommendations = result.get('recommendations', [])
    for idx, rec in enumerate(recommendations):
        st.markdown(f"**{idx+1}.** {rec}")
    
    # Advanced features
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["💬 Follow-up Chat", "📄 Export Report", "ℹ️ Full Analysis"])
    
    with tab1:
        st.markdown("### 🔁 Agentic Follow-up Analysis")
        st.info("Ask 'what-if' questions to explore how additional information changes the differential diagnosis")
        
        followup_question = st.text_input(
            "Your question:",
            placeholder="What if the patient is also diabetic? What if WBC was normal? What if chest pain worsens?"
        )
        
        if st.button("Get Follow-up Analysis") and followup_question:
            with st.spinner("Analyzing your follow-up question..."):
                try:
                    followup_prompt = build_followup_prompt(
                        original_analysis=result,
                        followup_question=followup_question,
                        language=st.session_state.language
                    )
                    
                    model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    response = model.generate_content(
                        followup_prompt,
                        generation_config=genai.GenerationConfig(temperature=0.2, max_output_tokens=1500)
                    )
                    
                    st.markdown("#### 🤖 Follow-up Response:")
                    st.markdown(response.text)
                    
                    st.session_state.chat_history.append({
                        'question': followup_question,
                        'answer': response.text
                    })
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("#### 📜 Chat History")
            for idx, chat in enumerate(st.session_state.chat_history):
                st.markdown(f"**Q{idx+1}:** {chat['question']}")
                st.markdown(f"**A{idx+1}:** {chat['answer']}")
                st.markdown("---")
    
    with tab2:
        st.markdown("### 📥 Export Analysis Report")
        
        # JSON export
        json_report = json.dumps(result, indent=2, default=str)
        st.download_button(
            label="⬇️ Download JSON Report",
            data=json_report,
            file_name="meddiag_analysis.json",
            mime="application/json",
            width='stretch'
        )
        
        # Text summary
        text_summary = f"""MedDiag Gemini 3 - Analysis Report
{'='*50}

DIFFERENTIAL DIAGNOSES:
"""
        for diff in differentials:
            text_summary += f"\n#{diff.get('rank')}: {diff.get('diagnosis')} ({diff.get('probability')})\n"
            text_summary += f"Reasoning: {diff.get('reasoning', 'N/A')}\n"
        
        text_summary += f"\n\nUrgency: {urgency}\n"
        text_summary += f"Confidence: {confidence}\n"
        text_summary += f"\n\nRECOMMENDATIONS:\n"
        for idx, rec in enumerate(recommendations):
            text_summary += f"{idx+1}. {rec}\n"
        
        st.download_button(
            label="⬇️ Download Text Summary",
            data=text_summary,
            file_name="meddiag_summary.txt",
            mime="text/plain",
            width='stretch'
        )
        
        st.info("📄 PDF export coming soon!")
    
    with tab3:
        st.markdown("### 🔬 Complete Analysis JSON")
        st.json(result)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><strong>MedDiag Gemini 3</strong> - Built exclusively with Gemini 3 API for the Gemini 3 Hackathon</p>
    <p>⚠️ For educational and decision-support purposes only. Not a replacement for professional medical care.</p>
    <p style="font-size: 0.9rem;">Powered by Google Gemini 3 | Multimodal Medical AI</p>
</div>
""", unsafe_allow_html=True)
