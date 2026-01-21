# 🏥 MIMIC-CXR Access: PhysioNet Credentialing Guide

## Overview

MIMIC-CXR is the gold-standard chest X-ray dataset containing **377,110 images** with structured radiology reports. Access requires credentialing through PhysioNet to ensure HIPAA compliance and ethical use of medical data.

---

## Step 1: Create PhysioNet Account

1. Visit: https://physionet.org/register/
2. Click "Register" and complete the form:
   - Full name (must match government ID)
   - Institutional email (required)
   - Professional title
   - Organization details

3. Verify your email address

**Time Required**: 5 minutes

---

## Step 2: Complete CITI Training

PhysioNet requires completion of "Data or Specimens Only Research" training:

### Option A: Through PhysioNet (Recommended)
1. Log into PhysioNet
2. Go to: https://physionet.org/about/citi-course/
3. Click "Complete training through CITI Program"
4. Select course: **"Data or Specimens Only Research"**
5. Complete all modules (~2-3 hours)
6. Download completion certificate

### Option B: Existing CITI Certificate
If you have recent CITI training (<3 years old):
1. Upload existing certificate to PhysioNet
2. Ensure it covers human subjects research

**Time Required**: 2-3 hours for new training

---

## Step 3: Request Dataset Access

1. Navigate to MIMIC-CXR page: https://physionet.org/content/mimic-cxr/2.0.0/
2. Click "Request Access" button
3. Complete the Data Use Agreement (DUA):
   - Agree to use data only for research
   - Commit to protecting patient privacy
   - Promise not to attempt re-identification
   - Agree to destroy data after research completion (or specify retention period)

4. Upload required documents:
   - CITI training certificate (PDF)
   - Institutional affiliation confirmation (if applicable)

5. Submit application

**Time Required**: 15-20 minutes

---

## Step 4: Approval Process

- **Review time**: Typically 1-7 days (sometimes up to 2 weeks)
- **Credentialing committee** reviews applications manually
- **Email notification** when approved

### What Gets Evaluated:
✅ Valid CITI training certificate  
✅ Legitimate research purpose  
✅ Institutional affiliation (academic/research org preferred)  
✅ Completeness of DUA

---

## Step 5: Download Dataset

Once approved, you'll get download access:

### Dataset Components

| File | Size | Description |
|------|------|-------------|
| `mimic-cxr-2.0.0-split.csv` | ~5 MB | Train/val/test split indices |
| `mimic-cxr-2.0.0-metadata.csv` | ~50 MB | Image metadata (patient ID, study, view) |
| `mimic-cxr-2.0.0-chexpert.csv` | ~20 MB | CheXpert labels (14 pathologies) |
| `mimic-cxr-reports.zip` | ~500 MB | Free-text radiology reports |
| `files/` (images) | ~440 GB | DICOM and JPG chest X-rays |

### Download Options

**Option A: Web Download** (Small subsets)
```bash
# Download via browser (slow for large files)
# Use for reports and metadata only
```

**Option B: wget/curl** (Recommended)
```bash
# Download with resume capability
wget -r -N -c -np https://physionet.org/files/mimic-cxr/2.0.0/
```

**Option C: AWS S3** (Fastest, requires AWS account)
```bash
# MIMIC-CXR is mirrored on AWS S3
# Free egress within same AWS region
aws s3 sync s3://physionet-open/mimic-cxr/ ./mimic-cxr/
```

**Recommended**: Download metadata and reports first (~500 MB), then selectively download images based on your use case (~440 GB full dataset).

---

## Step 6: Data Structure Understanding

### Directory Layout
```
mimic-cxr-2.0.0/
├── files/
│   ├── p10/
│   │   ├── p10000032/
│   │   │   ├── s50414267/
│   │   │   │   ├── 02aa804e-bde0afdd-112c0b34-7bc16630-4e384014.dcm
│   │   │   │   ├── 02aa804e-bde0afdd-112c0b34-7bc16630-4e384014.jpg
│   │   │   │   └── ...
│   ├── p11/
│   └── ...
├── mimic-cxr-2.0.0-metadata.csv
├── mimic-cxr-2.0.0-chexpert.csv
├── mimic-cxr-2.0.0-split.csv
└── mimic-cxr-reports.zip
```

### Key Files Explained

**metadata.csv**
```csv
dicom_id,subject_id,study_id,ViewPosition,Rows,Columns
02aa804e-bde0afdd-112c0b34-7bc16630-4e384014,10000032,50414267,AP,2320,2828
```

**chexpert.csv** (Pathology Labels)
```csv
subject_id,study_id,Atelectasis,Cardiomegaly,Consolidation,Edema,Enlarged Cardiomediastinum,Fracture,Lung Lesion,Lung Opacity,No Finding,Pleural Effusion,Pleural Other,Pneumonia,Pneumothorax,Support Devices
10000032,50414267,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0
```
- `1.0` = Positive
- `0.0` = Negative  
- `-1.0` = Uncertain
- `NaN` = Not mentioned

**split.csv**
```csv
dicom_id,split
02aa804e-bde0afdd-112c0b34-7bc16630-4e384014,train
```

---

## Ethical Considerations

### Data Use Restrictions
❌ **NOT ALLOWED**:
- Commercial use without separate agreement
- Attempting to re-identify patients
- Sharing data with non-credentialed users
- Publishing images that could identify individuals

✅ **ALLOWED**:
- Academic research
- Model training for medical AI
- Algorithm development
- Publication of aggregate statistics
- De-identified image examples in papers (with watermarks)

### Citation Requirement
Always cite when using MIMIC-CXR:

```
Johnson, A., Pollard, T., Greenbaum, N. et al. MIMIC-CXR-JPG, a large publicly 
available database of labeled chest radiographs. Sci Data 6, 317 (2019). 
https://doi.org/10.1038/s41597-019-0322-0
```

---

## Timeline Summary

| Step | Time Required | Waiting Period |
|------|---------------|----------------|
| Account creation | 5 min | Email verification (instant) |
| CITI training | 2-3 hours | Certificate issued immediately |
| Access request | 15 min | 1-14 days (typically 3-5 days) |
| Metadata download | 10 min | - |
| Full image download | 2-48 hours | Depends on connection speed |

**Total Time**: ~1 week (including approval wait)

---

## Troubleshooting

### Application Rejected
**Reasons**:
- Incomplete CITI training
- No institutional affiliation (individual researchers may be scrutinized more)
- Vague research purpose

**Solution**: Resubmit with detailed research plan

### Download Timeout
**Solution**: Use `wget -c` for resume capability or AWS S3 mirror

### Storage Constraints
**Solution**: Download subset of images
- Filter by pathology (e.g., only pneumonia cases)
- Use low-resolution JPGs instead of DICOMs
- Sample 10-20% of dataset for prototyping

---

## Next Steps After Access

1. Review [`preprocess_mimic_cxr.py`](file:///C:/Users/MS/.gemini/antigravity/scratch/MedDiag-Gemini3-Hackathon/training/scripts/preprocess_mimic_cxr.py) - Data preprocessing script
2. Read [`vertex_ai_training.py`](file:///C:/Users/MS/.gemini/antigravity/scratch/MedDiag-Gemini3-Hackathon/training/scripts/vertex_ai_training.py) - Fine-tuning pipeline
3. Set up Google Cloud Vertex AI (see [`vertex_ai_setup.md`](file:///C:/Users/MS/.gemini/antigravity/scratch/MedDiag-Gemini3-Hackathon/training/guides/vertex_ai_setup.md))

---

## Support

- **PhysioNet Help**: https://physionet.org/contact/
- **MIMIC-CXR Forum**: https://groups.google.com/forum/#!forum/mimic-users
- **Email**: physionet-support@mit.edu

**Good luck with your credentialing!** 🏥
