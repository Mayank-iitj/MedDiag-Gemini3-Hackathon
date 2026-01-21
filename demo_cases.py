"""
Demo Medical Cases Library
Collection of realistic medical cases for demonstration purposes
"""

DEMO_CASES = {
    "Pneumonia - Bacterial CAP": {
        "clinical_notes": """Patient presents with:
• Fever (38.5°C) for 3 days
• Productive cough with yellow sputum
• Shortness of breath on exertion
• Pleuritic chest pain (right side)

Vital Signs:
• BP: 125/82 mmHg
• HR: 108 bpm
• RR: 22/min
• SpO2: 94% on room air

Labs:
• WBC: 15,200/μL (elevated)
• CRP: 85 mg/L (elevated)
• Procalcitonin: 0.8 ng/mL""",
        "patient_history": """Age: 45 years
Sex: Male
PMH: Type 2 Diabetes (controlled), Hypertension
Medications: Metformin 1000mg BID, Lisinopril 10mg daily
Social: Non-smoker, occasional alcohol
Allergies: None known""",
        "image": "assets/pneumonia_bacterial.png"
    },
    
    "Pulmonary Edema - CHF": {
        "clinical_notes": """Patient presents with:
• Progressive dyspnea over 2 days
• Orthopnea (3 pillow)
• Paroxysmal nocturnal dyspnea
• Bilateral leg swelling

Vital Signs:
• BP: 170/95 mmHg
• HR: 102 bpm (irregular)
• RR: 26/min
• SpO2: 89% on room air

Physical Exam:
• JVP elevated at 10 cm
• Bilateral crackles to mid-lung fields
• S3 gallop present
• 2+ pitting edema bilaterally

Labs:
• BNP: 1,250 pg/mL (very elevated)
• Troponin: 0.08 ng/mL (mildly elevated)""",
        "patient_history": """Age: 68 years
Sex: Female
PMH: CHF (EF 30%), Hypertension, Atrial fibrillation
Medications: Furosemide 40mg daily, Metoprolol 50mg BID, Apixaban
Social: Non-smoker, denies alcohol
Recent: Missed diuretic doses for 3 days""",
        "image": "assets/sample_xray.jpg"
    },
    
    "Pneumothorax - Spontaneous": {
        "clinical_notes": """Patient presents with:
• Sudden onset right-sided chest pain (1 hour ago)
• Shortness of breath
• No trauma history

Vital Signs:
• BP: 118/75 mmHg
• HR: 115 bpm
• RR: 24/min
• SpO2: 92% on room air

Physical Exam:
• Decreased breath sounds on right
• Hyperresonant to percussion (right)
• Trachea deviated slightly to left

Labs:
• WBC: 8,500/μL (normal)""",
        "patient_history": """Age: 22 years
Sex: Male
PMH: None
Medications: None
Social: Smoker (1 pack/day for 4 years), tall and thin build
Family Hx: Brother had pneumothorax""",
        "image": "assets/pneumothorax.png"
    },
    
    "COPD Exacerbation": {
        "clinical_notes": """Patient presents with:
• Worsening shortness of breath for 5 days
• Increased sputum production (green)
• Wheezing
• Unable to complete sentences

Vital Signs:
• BP: 135/85 mmHg
• HR: 98 bpm
• RR: 28/min
• SpO2: 88% on 2L NC (baseline 92% on room air)

Physical Exam:
• Prolonged expiratory phase
• Diffuse expiratory wheezes
• Use of accessory muscles
• Barrel chest

Labs:
• WBC: 12,800/μL
• ABG: pH 7.32, pCO2 58, pO2 62""",
        "patient_history": """Age: 64 years
Sex: Male
PMH: COPD (GOLD Stage 3), HTN
Medications: Albuterol, Tiotropium, Lisinopril
Social: 40 pack-year smoking history, quit 2 years ago
Recent: Ran out of inhalers 1 week ago""",
        "image": "assets/copd_exacerbation.png"
    },
    
    "Pulmonary Embolism": {
        "clinical_notes": """Patient presents with:
• Sudden onset dyspnea (2 hours ago)
• Pleuritic chest pain (left sided)
• Hemoptysis (scant)
• Feeling of impending doom

Vital Signs:
• BP: 102/68 mmHg
• HR: 125 bpm
• RR: 30/min
• SpO2: 87% on room air

Physical Exam:
• Tachycardic, regular rhythm
• Clear lungs bilaterally
• Right calf tenderness and swelling

Labs:
• D-dimer: 4,500 ng/mL (markedly elevated)
• Troponin: 0.12 ng/mL (elevated)
• ABG: pH 7.48, pCO2 32, pO2 58""",
        "patient_history": """Age: 52 years
Sex: Female
PMH: Recent surgery (hysterectomy 2 weeks ago)
Medications: OCP (stopped post-op)
Social: Non-smoker, sedentary
Risk factors: Post-operative, estrogen use""",
        "image": "assets/pulmonary_embolism.png"
    },
    
    "Pleural Effusion - Large": {
        "clinical_notes": """Patient presents with:
• Progressive dyspnea over 3 weeks
• Dry cough
• Dull chest discomfort (right side)

Vital Signs:
• BP: 128/82 mmHg
• HR: 88 bpm
• RR: 22/min
• SpO2: 93% on room air

Physical Exam:
• Decreased breath sounds right base
• Dullness to percussion right base
• Decreased tactile fremitus

Labs:
• WBC: 7,200/μL (normal)
• LDH: 245 U/L""",
        "patient_history": """Age: 58 years
Sex: Male
PMH: Hepatitis C cirrhosis (Child-Pugh B)
Medications: Spironolactone, Furosemide
Social: Former IVDU, no current alcohol
Recent: Increased abdominal girth""",
        "image": "assets/pleural_effusion.png"
    },
    
    "Lung Cancer - Mass": {
        "clinical_notes": """Patient presents with:
• Persistent cough for 6 weeks
• Hemoptysis (intermittent)
• Unintentional weight loss (15 lbs in 2 months)
• Hoarseness

Vital Signs:
• BP: 132/78 mmHg
• HR: 82 bpm
• RR: 18/min
• SpO2: 96% on room air

Physical Exam:
• Decreased breath sounds left apex
• No lymphadenopathy
• Digital clubbing present

Labs:
• WBC: 8,900/μL
• Hemoglobin: 11.2 g/dL (anemia)""",
        "patient_history": """Age: 67 years
Sex: Male
PMH: None significant
Medications: None
Social: 50 pack-year smoking history (current smoker)
Occupational: Asbestos exposure (shipyard worker)""",
        "image": "assets/lung_cancer.png"
    },
    
    "Tuberculosis - Active PTB": {
        "clinical_notes": """Patient presents with:
• Chronic cough for 8 weeks (productive)
• Night sweats (drenching)
• Fever (low-grade, evening)
• Weight loss (20 lbs in 3 months)
• Hemoptysis (small amount)

Vital Signs:
• BP: 110/70 mmHg
• HR: 92 bpm
• RR: 20/min
• SpO2: 95% on room air
• Temperature: 38.2°C (evening)

Labs:
• WBC: 10,500/μL
• ESR: 68 mm/hr (elevated)
• QuantiFERON: Positive""",
        "patient_history": """Age: 34 years
Sex: Female
PMH: HIV (CD4 280, on ART)
Medications: Tenofovir/Emtricitabine/Dolutegravir
Social: Born in India, immigrated 2 years ago
Exposure: Mother diagnosed with TB 6 months ago""",
        "image": "assets/tuberculosis.png"
    },
    
    "Asthma Exacerbation": {
        "clinical_notes": """Patient presents with:
• Acute worsening dyspnea for 6 hours
• Wheezing
• Chest tightness
• No relief from rescue inhaler

Vital Signs:
• BP: 122/76 mmHg
• HR: 112 bpm
• RR: 32/min
• SpO2: 91% on room air
• Peak flow: 180 L/min (personal best 450)

Physical Exam:
• Diffuse expiratory wheezes
• Prolonged expiratory phase
• Speaking in short phrases
• Accessory muscle use

Labs:
• WBC: 9,200/μL
• ABG: pH 7.45, pCO2 35, pO2 68""",
        "patient_history": """Age: 28 years
Sex: Female
PMH: Asthma (moderate persistent)
Medications: Albuterol PRN, Fluticasone/Salmeterol BID (poor adherence)
Social: Non-smoker, cat at home
Trigger: Upper respiratory infection 3 days ago""",
        "image": "assets/asthma_exacerbation.png"
    },
    
    "Aspiration Pneumonia": {
        "clinical_notes": """Patient presents with:
• Fever (38.8°C) for 2 days
• Productive cough (foul-smelling sputum)
• Dyspnea
• Witnessed aspiration event 4 days ago

Vital Signs:
• BP: 108/65 mmHg
• HR: 105 bpm
• RR: 26/min
• SpO2: 91% on 3L NC

Physical Exam:
• Crackles right lower lobe
• Poor dentition noted
• Decreased level of consciousness

Labs:
• WBC: 18,500/μL (left shift)
• Lactate: 2.8 mmol/L""",
        "patient_history": """Age: 78 years
Sex: Male
PMH: CVA with residual dysphagia, dementia
Medications: Aspirin, Atorvastatin, Donepezil
Social: Nursing home resident
Recent: Choking episode 4 days ago during meal""",
        "image": "assets/sample_xray.jpg"
    },
    
    "COVID-19 Pneumonia": {
        "clinical_notes": """Patient presents with:
• Fever (39.1°C) for 5 days
• Dry cough
• Severe dyspnea (onset day 7)
• Myalgias, fatigue
• Anosmia, dysgeusia

Vital Signs:
• BP: 118/72 mmHg
• HR: 102 bpm
• RR: 30/min
• SpO2: 88% on room air

Labs:
• WBC: 6,200/μL (lymphopenia)
• D-dimer: 1,200 ng/mL (elevated)
• CRP: 156 mg/L (markedly elevated)
• IL-6: 88 pg/mL
• COVID PCR: Positive""",
        "patient_history": """Age: 55 years
Sex: Male
PMH: Type 2 DM, Obesity (BMI 34)
Medications: Metformin
Social: Unvaccinated
Exposure: Household contact positive 10 days ago""",
        "image": "assets/covid_pneumonia.png"
    },
    
    "Interstitial Lung Disease": {
        "clinical_notes": """Patient presents with:
• Progressive dyspnea on exertion (6 months)
• Dry cough
• No fever, weight loss stable

Vital Signs:
• BP: 135/82 mmHg
• HR: 78 bpm
• RR: 18/min at rest, 28/min with exertion
• SpO2: 96% at rest, 87% with exertion

Physical Exam:
• Bilateral fine inspiratory crackles (Velcro rales)
• Digital clubbing present

Labs:
• WBC: 7,800/μL
• ANA: Positive 1:320
• Anti-Scl-70: Positive
• PFTs: Restrictive pattern (FVC 58% predicted)""",
        "patient_history": """Age: 62 years
Sex: Female
PMH: Systemic sclerosis (limited cutaneous)
Medications: None currently
Social: Non-smoker
Occupational: No exposures""",
        "image": "assets/interstitial_lung_disease.png"
    },
    
    "Aortic Dissection": {
        "clinical_notes": """Patient presents with:
• Sudden severe chest pain (tearing, radiating to back)
• Started abruptly 1 hour ago
• Maximal at onset

Vital Signs:
• BP: Right arm 185/102, Left arm 142/88 (difference >20 mmHg)
• HR: 98 bpm
• RR: 22/min
• SpO2: 97% on room air

Physical Exam:
• Unequal pulses upper extremities
• No murmur
• Neurologically intact

Labs:
• Troponin: 0.02 ng/mL (normal)
• D-dimer: 2,800 ng/mL (elevated)
• ECG: Normal sinus rhythm, LVH""",
        "patient_history": """Age: 58 years
Sex: Male
PMH: Hypertension (poorly controlled), Marfan syndrome
Medications: Lisinopril (non-compliant)
Social: Non-smoker
Family Hx: Father died of aortic dissection at age 62""",
        "image": "assets/aortic_dissection.png"
    },
    
    "Pericardial Effusion with Tamponade": {
        "clinical_notes": """Patient presents with:
• Progressive dyspnea over 2 weeks
• Chest discomfort
• Lightheadedness
• Decreased exercise tolerance

Vital Signs:
• BP: 88/62 mmHg
• HR: 118 bpm
• RR: 24/min
• SpO2: 94% on room air
• Pulsus paradoxus: 18 mmHg

Physical Exam:
• JVP elevated, Kussmaul sign present
• Distant heart sounds
• No peripheral edema

Labs:
• Troponin: 0.03 ng/mL
• BNP: 280 pg/mL
• ECG: Low voltage, electrical alternans""",
        "patient_history": """Age: 46 years
Sex: Female
PMH: SLE, chronic kidney disease
Medications: Prednisone, Hydroxychloroquine
Social: Non-smoker
Recent: Stopped prednisone 3 weeks ago""",
        "image": "assets/pericardial_effusion.png"
    },
    
    "Sarcoidosis - Pulmonary": {
        "clinical_notes": """Patient presents with:
• Dyspnea on exertion (progressive over months)
• Dry cough
• Fatigue
• Skin lesions on face

Vital Signs:
• BP: 128/78 mmHg
• HR: 76 bpm
• RR: 16/min
• SpO2: 96% on room air

Physical Exam:
• Violaceous papules on nose (lupus pernio)
• Bilateral cervical lymphadenopathy
• Crackles bibasilar

Labs:
• WBC: 8,200/μL
• Calcium: 11.2 mg/dL (elevated)
• ACE level: 142 U/L (elevated)
• PFTs: Restrictive pattern""",
        "patient_history": """Age: 42 years
Sex: Female (African American)
PMH: None
Medications: None
Social: Non-smoker
Recent: Incidental finding on screening CXR""",
        "image": "assets/sarcoidosis.png"
    },
    
    "Rib Fractures - Trauma": {
        "clinical_notes": """Patient presents with:
• Severe right-sided chest wall pain
• Pain with breathing/coughing
• Motor vehicle collision 2 hours ago

Vital Signs:
• BP: 118/75 mmHg
• HR: 98 bpm
• RR: 24/min (shallow)
• SpO2: 94% on room air

Physical Exam:
• Point tenderness ribs 4-6 right
• Crepitus palpable
• No paradoxical movement
• Breath sounds equal

Labs:
• WBC: 11,200/μL
• Hemoglobin: 14.2 g/dL""",
        "patient_history": """Age: 38 years
Sex: Male
PMH: None
Medications: None
Mechanism: T-bone collision, driver side impact
Seatbelt: Yes, airbag deployed""",
        "image": "assets/rib_fractures.png"
    },
    
    "Bronchiectasis": {
        "clinical_notes": """Patient presents with:
• Chronic productive cough (years)
• Daily sputum production (copious, purulent)
• Recurrent pneumonias (3 in past year)
• Hemoptysis (occasional)

Vital Signs:
• BP: 125/80 mmHg
• HR: 82 bpm
• RR: 18/min
• SpO2: 95% on room air

Physical Exam:
• Coarse crackles bilateral lower lobes
• Digital clubbing
• Wheezing on forced expiration

Labs:
• WBC: 9,800/μL
• Sputum culture: Pseudomonas aeruginosa
• IgG: 450 mg/dL (low)""",
        "patient_history": """Age: 52 years
Sex: Female
PMH: Cystic fibrosis (diagnosed childhood), CFRD
Medications: Pancreatic enzymes, Insulin, Azithromycin (chronic)
Social: Never smoker
Recent: Exacerbation 2 months ago""",
        "image": "assets/sample_xray.jpg"
    },
    
    "Costochondritis": {
        "clinical_notes": """Patient presents with:
• Sharp chest pain (left parasternal)
• Pain worse with movement, deep breathing
• Duration: 3 days

Vital Signs:
• BP: 122/76 mmHg
• HR: 72 bpm
• RR: 14/min
• SpO2: 99% on room air

Physical Exam:
• Reproducible pain with palpation of costochondral junctions
• No swelling or erythema
• Lungs clear
• Heart sounds normal

Labs:
• Troponin: <0.01 ng/mL
• D-dimer: 180 ng/mL (normal)
• ECG: Normal""",
        "patient_history": """Age: 32 years
Sex: Male
PMH: None
Medications: None
Social: Gym enthusiast, recent heavy bench press workout
Recent: Upper respiratory infection 2 weeks ago""",
        "image": "assets/costochondritis_normal.png"
    },
    
    "Lung Abscess": {
        "clinical_notes": """Patient presents with:
• Fever (38.9°C) for 2 weeks
• Productive cough with foul-smelling sputum
• Weight loss (10 lbs in 3 weeks)
• Night sweats

Vital Signs:
• BP: 112/68 mmHg
• HR: 102 bpm
• RR: 22/min
• SpO2: 93% on room air

Physical Exam:
• Poor dental hygiene
• Crackles right upper lobe
• Dullness to percussion

Labs:
• WBC: 16,800/μL with left shift
• Sputum: Mixed anaerobes
• Albumin: 2.8 g/dL (low)""",
        "patient_history": """Age: 56 years
Sex: Male
PMH: Alcohol use disorder, GERD
Medications: None (non-compliant)
Social: Heavy alcohol use, homeless
Recent: Witnessed unconscious episode 3 weeks ago""",
        "image": "assets/sample_xray.jpg"
    },
    
    "Mediastinal Mass": {
        "clinical_notes": """Patient presents with:
• Dyspnea that worsens lying flat
• Facial swelling (worse in morning)
• Dilated veins on chest wall
• Cough

Vital Signs:
• BP: 135/82 mmHg
• HR: 88 bpm
• RR: 20/min
• SpO2: 96% on room air

Physical Exam:
• Facial plethora and edema
• Distended neck veins
• Dilated chest wall veins
• No JVP pulsations

Labs:
• WBC: 12,200/μL
• LDH: 580 U/L (elevated)
• β-hCG: Negative
• AFP: Negative""",
        "patient_history": """Age: 28 years
Sex: Male
PMH: None
Medications: None
Social: Non-smoker
Recent: Noticed difficulty breathing when lying down 2 weeks ago""",
        "image": "assets/sample_xray.jpg"
    },
    
    "Pneumocystis Pneumonia (PCP)": {
        "clinical_notes": """Patient presents with:
• Progressive dyspnea over 3 weeks
• Dry cough
• Fever (38.5°C) for 1 week
• Fatigue, weight loss

Vital Signs:
• BP: 108/68 mmHg
• HR: 108 bpm
• RR: 28/min
• SpO2: 86% on room air

Physical Exam:
• Tachypneic but lungs clear
• Oral thrush present
• No lymphadenopathy

Labs:
• CD4 count: 42 cells/μL
• HIV viral load: 450,000 copies/mL
• LDH: 524 U/L (markedly elevated)
• ABG: pH 7.46, pCO2 30, pO2 58, A-a gradient 52""",
        "patient_history": """Age: 38 years
Sex: Male
PMH: HIV (newly diagnosed 2 months ago, not on ART yet)
Medications: None
Social: MSM, recent diagnosis
Recent: Lost to follow-up after initial diagnosis""",
        "image": "assets/sample_xray.jpg"
    }
}
