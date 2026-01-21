"""
Prompt Builder for Medical Diagnostic Reasoning
Constructs structured prompts for Gemini 3 medical analysis
"""

def build_diagnostic_prompt(clinical_notes: str = "", patient_history: str = "", language: str = "english") -> str:
    """
    Build a comprehensive medical diagnostic prompt for Gemini 3
    
    Args:
        clinical_notes: Free-text clinical observations and symptoms
        patient_history: Structured patient medical history
        language: Output language (english/hindi)
    
    Returns:
        Structured prompt string with JSON schema enforcement
    """
    
    language_instruction = ""
    if language.lower() == "hindi":
        language_instruction = "\n\nIMPORTANT: Provide all reasoning and explanations in Hindi (हिंदी), but keep medical terms and JSON keys in English."
    
    # Few-shot examples based on real MIMIC-CXR patterns
    few_shot_examples = """
EXAMPLE CASE 1 - COMMUNITY-ACQUIRED PNEUMONIA:
Image Findings: Chest X-ray shows right lower lobe consolidation with air bronchograms. No pleural effusion. Cardiac silhouette normal size.
Clinical: 52-year-old male, fever 39.2°C for 3 days, productive cough with yellow sputum, pleuritic chest pain. WBC 16,500/μL, CRP 120 mg/L.
Patient History: No significant PMH, non-smoker.

Expected Analysis:
{
  "findings": [
    "Right lower lobe opacity with air bronchograms consistent with alveolar consolidation",
    "No pleural effusion or pneumothorax",
    "Normal cardiac silhouette",
    "Elevated inflammatory markers (WBC 16,500, CRP 120)"
  ],
  "differentials": [
    {
      "rank": 1,
      "diagnosis": "Community-acquired pneumonia (CAP), likely bacterial",
      "probability": "75-85%",
      "reasoning": "Classic presentation with acute onset fever, productive cough, pleuritic pain, and lobar consolidation on imaging. Elevated WBC and CRP strongly support bacterial etiology. Air bronchograms indicate alveolar filling process.",
      "evidence_pro": [
        "Lobar consolidation pattern typical for bacterial pneumonia",
        "Acute symptom onset (3 days)",
        "High fever (39.2°C) with productive cough",
        "Marked leukocytosis (16,500) and elevated CRP (120)",
        "Pleuritic chest pain suggests pleural involvement"
      ],
      "evidence_con": [
        "No risk factors for atypical pneumonia mentioned",
        "Relatively young patient without comorbidities"
      ],
      "next_tests": [
        "Sputum culture and Gram stain",
        "Blood cultures before antibiotics",
        "Pneumococcal and Legionella urinary antigens",
        "Consider CT chest if no improvement in 48-72 hours"
      ]
    },
    {
      "rank": 2,
      "diagnosis": "Aspiration pneumonia",
      "probability": "10-15%",
      "reasoning": "Right lower lobe location is consistent with aspiration pneumonia (most common site). However, no clear aspiration risk factors mentioned in history.",
      "evidence_pro": [
        "Right lower lobe location (dependent segment)"
      ],
      "evidence_con": [
        "No history of dysphagia, altered consciousness, or GERD",
        "No risk factors for aspiration identified"
      ],
      "next_tests": [
        "Detailed swallowing assessment if suspicion increases",
        "Review for alcoholism or neurological conditions"
      ]
    }
  ],
  "timeline": {
    "days": [0, 3, 7, 14],
    "events": ["Symptom onset", "Current presentation (Day 3)", "Expected improvement on antibiotics", "Resolution on follow-up"],
    "diagnosis_probs": [
      {"CAP": 0.8, "Aspiration": 0.15},
      {"CAP": 0.85, "Aspiration": 0.1},
      {"CAP": 0.9, "Aspiration": 0.05},
      {"CAP": 0.95, "Aspiration": 0.02}
    ]
  },
  "recommendations": [
    "Start empiric antibiotics (e.g., ceftriaxone + azithromycin for CAP)",
    "Supportive care: hydration, antipyretics, oxygen if SpO2 < 92%",
    "Follow-up chest X-ray in 6 weeks to confirm resolution",
    "Monitor for clinical improvement within 48-72 hours"
  ],
  "urgency": "Urgent",
  "confidence": "High - Classic presentation with strong radiological and laboratory correlation"
}

---

EXAMPLE CASE 2 - CARDIOGENIC PULMONARY EDEMA:
Image Findings: Bilateral perihilar opacities in a bat-wing pattern, cardiomegaly (cardiothoracic ratio > 0.5), Kerley B lines, cephalization of pulmonary vessels.
Clinical: 68-year-old female, progressive dyspnea over 2 days, orthopnea, paroxysmal nocturnal dyspnea. BP 170/95, JVP elevated, bilateral crackles on auscultation. BNP 1,200 pg/mL.
Patient History: Known CHF (EF 30%), hypertension, atrial fibrillation. Meds: Furosemide, metoprolol (reports missed doses recently).

Expected Analysis:
{
  "findings": [
    "Bilateral perihilar infiltrates with bat-wing distribution",
    "Cardiomegaly with CTR > 0.5",
    "Kerley B lines indicating interstitial edema",
    "Vascular redistribution to upper lobes (cephalization)"
  ],
  "differentials": [
    {
      "rank": 1,
      "diagnosis": "Acute decompensated heart failure with cardiogenic pulmonary edema",
      "probability": "85-95%",
      "reasoning": "Patient with known CHF and reduced EF presenting with classic pulmonary edema pattern on imaging. Bilateral perihilar opacities, cardiomegaly, Kerley B lines are pathognomonic for cardiogenic edema. Elevated BNP (1,200) confirms cardiac etiology. Recent medication non-compliance is likely trigger.",
      "evidence_pro": [
        "Known CHF with EF 30%",
        "Classic imaging: bilateral perihilar opacities, cardiomegaly, Kerley B lines",
        "Elevated BNP (1,200 pg/mL, normal < 100)",
        "Clinical signs: orthopnea, PND, elevated JVP, bilateral crackles",
        "Hypertensive (170/95) suggesting fluid overload",
        "Recent diuretic non-compliance"
      ],
      "evidence_con": [
        "No mention of leg edema (though absence doesn't rule out CHF)"
      ],
      "next_tests": [
        "Echocardiogram to assess current EF and valvular function",
        "ECG to rule out acute MI or arrhythmia as precipitant",
        "Troponin to exclude ACS",
        "Renal function and electrolytes before diuresis"
      ]
    },
    {
      "rank": 2,
      "diagnosis": "Bilateral pneumonia (less likely)",
      "probability": "5-10%",
      "reasoning": "Bilateral infiltrates could theoretically represent multifocal pneumonia, but absence of fever and symmetric perihilar distribution makes this unlikely.",
      "evidence_pro": [
        "Bilateral opacities on imaging"
      ],
      "evidence_con": [
        "No fever or elevated WBC mentioned",
        "BNP 1,200 strongly supports cardiac etiology",
        "Cardiomegaly and Kerley B lines not explained by pneumonia",
        "Classic CHF symptoms (orthopnea, PND)"
      ],
      "next_tests": [
        "Procalcitonin if infectious etiology still suspected"
      ]
    }
  ],
  "timeline": {
    "days": [0, 2, 5, 10],
    "events": ["Medication non-compliance", "Current presentation (Day 2)", "Expected response to diuresis", "Clinical stabilization"],
    "diagnosis_probs": [
      {"CHF exacerbation": 0.9, "Pneumonia": 0.08},
      {"CHF exacerbation": 0.95, "Pneumonia": 0.03},
      {"CHF exacerbation": 0.98, "Pneumonia": 0.01},
      {"CHF exacerbation": 0.99, "Pneumonia": 0.005}
    ]
  },
  "recommendations": [
    "IV diuresis (furosemide) with strict I/O monitoring",
    "Afterload reduction if BP allows (e.g., nitroglycerin)",
    "Supplemental oxygen to maintain SpO2 > 92%",
    "Daily weights and clinical reassessment",
    "Medication reconciliation and adherence counseling before discharge"
  ],
  "urgency": "Urgent",
  "confidence": "High - Classic cardiogenic pulmonary edema with strong clinical-radiological concordance"
}

---

EXAMPLE CASE 3 - NORMAL CHEST X-RAY:
Image Findings: Clear lung fields bilaterally, no infiltrates or consolidation. Cardiac silhouette within normal limits (CTR < 0.5). No pleural effusion or pneumothorax. Bony structures intact.
Clinical: 28-year-old male, persistent dry cough for 2 weeks, no fever, no dyspnea. Vitals normal. No smoking history.
Patient History: No significant PMH, recent upper respiratory infection 3 weeks ago.

Expected Analysis:
{
  "findings": [
    "Bilateral lung fields are clear without infiltrates, masses, or consolidation",
    "Cardiac silhouette normal size and contour",
    "No pleural effusion or pneumothorax",
    "Mediastinal contours within normal limits",
    "Bony structures without acute abnormality"
  ],
  "differentials": [
    {
      "rank": 1,
      "diagnosis": "Post-viral cough (bronchial hyperreactivity)",
      "probability": "60-70%",
      "reasoning": "Normal chest X-ray in patient with persistent dry cough following recent URI. Post-viral cough is common and can last 3-8 weeks. Absence of fever, dyspnea, and clear imaging rules out pneumonia or significant pulmonary pathology.",
      "evidence_pro": [
        "Recent URI 3 weeks ago (temporal correlation)",
        "Dry cough without systemic symptoms",
        "Normal chest X-ray excludes structural lung disease",
        "Young patient without risk factors"
      ],
      "evidence_con": [
        "Cough duration (2 weeks) is at upper limit for typical viral URI"
      ],
      "next_tests": [
        "Trial of over-the-counter cough suppressants",
        "Reassurance and expectant management",
        "Follow-up if symptoms persist > 6-8 weeks",
        "Consider spirometry if cough persists (assess for asthma)"
      ]
    },
    {
      "rank": 2,
      "diagnosis": "Early asthma or reactive airway disease",
      "probability": "20-25%",
      "reasoning": "Post-viral bronchial hyperreactivity can unmask underlying asthma. Normal chest X-ray does not exclude asthma.",
      "evidence_pro": [
        "Dry cough is common asthma presentation",
        "Post-viral trigger is classic for asthma exacerbation"
      ],
      "evidence_con": [
        "No wheezing reported",
        "No dyspnea or chest tightness",
        "No personal or family history of atopy mentioned"
      ],
      "next_tests": [
        "Spirometry with bronchodilator testing",
        "Peak flow monitoring",
        "Trial of inhaled bronchodilator if spirometry suggests obstruction"
      ]
    },
    {
      "rank": 3,
      "diagnosis": "GERD-related cough",
      "probability": "5-10%",
      "reasoning": "Gastroesophageal reflux can cause chronic cough without GI symptoms. However, no history of reflux mentioned.",
      "evidence_pro": [
        "Chronic dry cough can be sole manifestation of GERD"
      ],
      "evidence_con": [
        "No heartburn, regurgitation, or dysphagia reported",
        "Short duration (2 weeks) less typical for GERD cough"
      ],
      "next_tests": [
        "Empiric PPI trial if post-viral and asthma etiologies excluded",
        "pH monitoring if high suspicion"
      ]
    }
  ],
  "timeline": {
    "days": [0, 14, 28, 56],
    "events": ["Post-URI cough onset", "Current presentation (Day 14)", "Expected resolution", "Follow-up if persistent"],
    "diagnosis_probs": [
      {"Post-viral cough": 0.7, "Asthma": 0.2, "GERD": 0.08},
      {"Post-viral cough": 0.65, "Asthma": 0.25, "GERD": 0.08},
      {"Post-viral cough": 0.4, "Asthma": 0.4, "GERD": 0.15},
      {"Post-viral cough": 0.1, "Asthma": 0.6, "GERD": 0.25}
    ]
  },
  "recommendations": [
    "Reassurance that normal chest X-ray is encouraging",
    "Symptomatic treatment with cough suppressants (e.g., dextromethorphan)",
    "Adequate hydration",
    "Return if fever develops, dyspnea occurs, or cough persists > 6 weeks",
    "Consider pulmonary function testing if no improvement in 4 weeks"
  ],
  "urgency": "Routine",
  "confidence": "Moderate - Normal imaging is reassuring, but several benign etiologies possible"
}

---

These examples demonstrate the expected level of clinical reasoning and structured output. Now analyze the current case following this same rigorous approach.
"""
    
    prompt = f"""You are a senior radiologist and internal medicine physician using evidence-based medicine. Your role is to analyze medical images and clinical data to provide differential diagnoses with transparent reasoning.

{few_shot_examples}

CRITICAL MEDICAL ETHICS:
- You are a DECISION SUPPORT TOOL, not a replacement for physician judgment
- Always acknowledge uncertainty and limitations
- Never provide definitive diagnoses - only ranked differentials with probabilities
- Flag urgent/critical findings that require immediate attention

CLINICAL CONTEXT:

Patient History:
{patient_history if patient_history else "Not provided"}

Clinical Notes:
{clinical_notes if clinical_notes else "Not provided"}

ANALYSIS REQUIREMENTS:

1. IMAGE FINDINGS:
   - Systematically describe each uploaded image
   - Note normal and abnormal findings
   - Use precise anatomical and radiological terminology

2. DIFFERENTIAL DIAGNOSES:
   - Rank diagnoses by probability (most likely first)
   - For each differential, provide:
     * Clear diagnostic label
     * Estimated probability range (e.g., "40-60%", "likely", "possible")
     * Clinical reasoning explaining why this diagnosis fits
     * Evidence supporting this diagnosis (from images and clinical data)
     * Evidence against this diagnosis (contradictory findings)
     * Recommended next diagnostic tests or imaging

3. TIMELINE ANALYSIS:
   - Estimate disease progression timeline
   - Provide key temporal milestones (e.g., "Day 3: symptom onset", "Day 7: current presentation")
   - Show how differential probabilities might evolve over time

4. RISK ASSESSMENT:
   - Identify urgency level: Routine / Urgent / Critical
   - Flag red flags requiring immediate intervention (sepsis, PE, acute MI, etc.)
   - Note patient safety considerations

5. RECOMMENDATIONS:
   - Next diagnostic steps (labs, imaging, specialist consult)
   - Clinical monitoring parameters
   - Patient safety precautions

OUTPUT FORMAT (STRICT JSON):

You MUST respond with valid JSON matching this exact schema:

{{
  "findings": [
    "Finding 1 from image analysis",
    "Finding 2 from clinical data",
    "Finding 3 combining both modalities"
  ],
  "differentials": [
    {{
      "rank": 1,
      "diagnosis": "Most likely diagnosis name",
      "probability": "40-60% or 'likely' or 'possible'",
      "reasoning": "Multi-sentence clinical reasoning explaining why this diagnosis fits the presentation",
      "evidence_pro": [
        "Supporting finding 1",
        "Supporting finding 2"
      ],
      "evidence_con": [
        "Contradictory finding or absence of expected sign"
      ],
      "next_tests": [
        "Specific test 1 (e.g., CT chest with contrast)",
        "Specific test 2 (e.g., D-dimer, BNP)"
      ]
    }},
    {{
      "rank": 2,
      "diagnosis": "Second most likely diagnosis",
      "probability": "20-40%",
      "reasoning": "...",
      "evidence_pro": ["..."],
      "evidence_con": ["..."],
      "next_tests": ["..."]
    }}
  ],
  "timeline": {{
    "days": [0, 3, 7, 14],
    "events": [
      "Symptom onset",
      "Progression milestone",
      "Current presentation",
      "Expected evolution if untreated"
    ],
    "diagnosis_probs": [
      {{"diagnosis_1": 0.3, "diagnosis_2": 0.5}},
      {{"diagnosis_1": 0.4, "diagnosis_2": 0.4}},
      {{"diagnosis_1": 0.5, "diagnosis_2": 0.3}},
      {{"diagnosis_1": 0.6, "diagnosis_2": 0.2}}
    ]
  }},
  "recommendations": [
    "Immediate action 1",
    "Follow-up test 2",
    "Monitoring parameter 3"
  ],
  "urgency": "Routine / Urgent / Critical",
  "confidence": "High / Moderate / Low - brief explanation of confidence level"
}}

SAFETY GUARDRAILS:
- If images are unclear or insufficient, state "Image quality insufficient for definitive analysis"
- If clinical context is missing critical information, note "Additional history needed: [specific items]"
- Never fabricate findings not visible in the images
- Never provide treatment recommendations (only diagnostic workup)
- Always include disclaimer: "This is a decision support analysis, not a final diagnosis"{language_instruction}

Now analyze the provided medical images and clinical data following these requirements. Output ONLY the JSON response, no additional text.
"""
    
    return prompt


def build_followup_prompt(original_analysis: dict, followup_question: str, language: str = "english") -> str:
    """
    Build a follow-up prompt for agentic chat functionality
    
    Args:
        original_analysis: The original diagnostic analysis JSON
        followup_question: User's follow-up question (e.g., "What if patient is diabetic?")
        language: Output language
    
    Returns:
        Contextual follow-up prompt
    """
    
    language_instruction = ""
    if language.lower() == "hindi":
        language_instruction = " Respond in Hindi (हिंदी), keeping medical terms in English."
    
    prompt = f"""You are continuing a medical case discussion. Here is the original analysis:

ORIGINAL DIFFERENTIAL DIAGNOSES:
{original_analysis.get('differentials', [])}

ORIGINAL FINDINGS:
{original_analysis.get('findings', [])}

USER FOLLOW-UP QUESTION:
{followup_question}

Provide a focused, evidence-based response addressing how this new information changes the differential diagnosis or clinical approach. Be specific about probability shifts and reasoning changes.{language_instruction}

Keep your response concise (2-4 paragraphs) and clinically actionable.
"""
    
    return prompt
