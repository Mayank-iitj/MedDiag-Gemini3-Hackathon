# 🚀 Google Cloud Vertex AI Setup Guide for Gemini Fine-Tuning

## Overview

This guide walks you through setting up Google Cloud Vertex AI for fine-tuning Gemini models on MIMIC-CXR data. Fine-tuning on Vertex AI offers better accuracy but requires a paid Google Cloud account.

---

## Prerequisites

✅ MIMIC-CXR dataset access (see [physionet_credentialing.md](./physionet_credentialing.md))  
✅ Google Cloud account with billing enabled  
✅ Credit card for Google Cloud payment  
✅ Estimated budget: $1,000-$4,000 for full 377K image training

---

## Step 1: Create Google Cloud Project

1. Visit: https://console.cloud.google.com/
2. Sign in with Google account
3. Click "Select a project" → "New Project"
4. Enter project details:
   - **Project name**: `meddiag-gemini-training`
   - **Organization**: Your organization (if applicable)
   - **Location**: Leave as default

5. Click "Create"

**Time Required**: 2 minutes

---

## Step 2: Enable Billing

1. Go to: https://console.cloud.google.com/billing
2. Click "Link a billing account" or "Create billing account"
3. Enter credit card information
4. Set up billing alerts (recommended):
   - Navigate to **Billing → Budgets & alerts**
   - Create budget: $500, $1000, $2000 thresholds
   - Enable email alerts at 50%, 90%, 100%

**Cost Estimates**:
- **Training (one-time)**: $3-10 per 1000 examples
  - 10K images: ~$30-100
  - 100K images: ~$300-1000
  - 377K images: ~$1,000-4,000
- **Inference (per query)**: ~$0.001 per image analyzed

---

## Step 3: Enable Required APIs

Run these commands in **Cloud Shell** (click >_ icon in top-right):

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Storage (for dataset upload)
gcloud services enable storage.googleapis.com

# Enable Compute Engine (for training VMs)
gcloud services enable compute.googleapis.com

# Confirm enabled services
gcloud services list --enabled
```

**Time Required**: 3-5 minutes

---

## Step 4: Set Up Authentication

### Option A: Using gcloud CLI (Recommended for local development)

```bash
# Install Google Cloud SDK if not already installed
# Windows: Download from https://cloud.google.com/sdk/docs/install
# Mac: brew install --cask google-cloud-sdk
# Linux: curl https://sdk.cloud.google.com | bash

# Initialize and authenticate
gcloud init
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project meddiag-gemini-training
```

### Option B: Service Account Key (For automated pipelines)

```bash
# Create service account
gcloud iam service-accounts create meddiag-training-sa \
    --display-name="MedDiag Training Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding meddiag-gemini-training \
    --member="serviceAccount:meddiag-training-sa@meddiag-gemini-training.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding meddiag-gemini-training \
    --member="serviceAccount:meddiag-training-sa@meddiag-gemini-training.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Download key file
gcloud iam service-accounts keys create ~/meddiag-sa-key.json \
    --iam-account=meddiag-training-sa@meddiag-gemini-training.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/meddiag-sa-key.json
```

---

## Step 5: Create Cloud Storage Bucket

```bash
# Create bucket for training data
gsutil mb -l us-central1 gs://meddiag-mimic-cxr-training/

# Verify bucket creation
gsutil ls

# Set lifecycle policy (auto-delete old files after 90 days)
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://meddiag-mimic-cxr-training/
```

**Bucket Structure**:
```
gs://meddiag-mimic-cxr-training/
├── raw/                 # Original MIMIC-CXR files
├── processed/           # Preprocessed training data
├── models/              # Fine-tuned model artifacts
└── logs/                # Training logs
```

---

## Step 6: Install Python Dependencies

```bash
# Install Vertex AI SDK
pip install google-cloud-aiplatform
pip install google-cloud-storage

# Verify installation
python -c "from google.cloud import aiplatform; print(aiplatform.__version__)"
```

---

## Step 7: Initialize Vertex AI in Python

Create `training/scripts/vertex_init.py`:

```python
from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(
    project='meddiag-gemini-training',
    location='us-central1',
    staging_bucket='gs://meddiag-mimic-cxr-training'
)

print("Vertex AI initialized successfully!")
print(f"Project: {aiplatform.metadata.get_client().project}")
print(f"Location: {aiplatform.metadata.get_location()}")
```

Test:
```bash
python training/scripts/vertex_init.py
```

---

## Step 8: Upload MIMIC-CXR Data to Cloud Storage

```bash
# Upload preprocessed training data (after running preprocess_mimic_cxr.py)
gsutil -m cp -r ./mimic-cxr-processed/* gs://meddiag-mimic-cxr-training/processed/

# Verify upload
gsutil du -sh gs://meddiag-mimic-cxr-training/processed/
```

**Upload time**: 2-24 hours depending on dataset size and connection speed

---

## Step 9: Fine-Tune Gemini Model

Use the prepared training script:

```bash
# Run fine-tuning (see vertex_ai_training.py for full implementation)
python training/scripts/vertex_ai_training.py \
    --training-data gs://meddiag-mimic-cxr-training/processed/train.jsonl \
    --validation-data gs://meddiag-mimic-cxr-training/processed/val.jsonl \
    --model gemini-2.0-flash-001 \
    --epochs 3 \
    --batch-size 8 \
    --learning-rate 0.0001
```

**Training time**: 4-48 hours depending on dataset size

---

## Step 10: Monitor Training

### Option A: Cloud Console UI
1. Go to: https://console.cloud.google.com/vertex-ai/training/training-pipelines
2. Select your training job
3. View metrics: loss curves, accuracy, validation performance

### Option B: Python SDK
```python
from google.cloud import aiplatform

# List training jobs
jobs = aiplatform.Model.list()
for job in jobs:
    print(f"Job: {job.display_name}, State: {job.state}")

# Get specific job
job = aiplatform.TrainingJob.get(resource_name='projects/meddiag-gemini-training/locations/us-central1/trainingJobs/12345')
print(job.state)
```

---

## Step 11: Deploy Fine-Tuned Model

```bash
# Deploy model to endpoint
python training/scripts/deploy_model.py \
    --model-id your-fine-tuned-model-id \
    --endpoint-name meddiag-gemini-endpoint \
    --machine-type n1-standard-4 \
    --min-replicas 1 \
    --max-replicas 3
```

**Deployment time**: 5-10 minutes

---

## Step 12: Update Application to Use Fine-Tuned Model

Update `app.py`:

```python
# Replace this:
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# With this:
from google.cloud import aiplatform

endpoint = aiplatform.Endpoint(
    endpoint_name='meddiag-gemini-endpoint',
    project='meddiag-gemini-training',
    location='us-central1'
)

# Use endpoint for predictions
response = endpoint.predict(instances=[{'content': multimodal_input}])
```

---

## Cost Optimization Tips

### 1. Start Small
- Train on 10K subset first (~$30-100)
- Evaluate accuracy improvement
- Scale to full dataset only if justified

### 2. Use Preemptible VMs
```python
# In training script
training_job = aiplatform.CustomTrainingJob(
    ...
    scheduling={
        'restart_job_on_worker_restart': True,
        'enable_web_access': False
    },
    # Use preemptible VMs (70% cost reduction)
    machine_type='n1-standard-8-preemptible'
)
```

### 3. Auto-Shutdown Endpoints
```bash
# Scale endpoint to 0 replicas when not in use
gcloud ai endpoints update ENDPOINT_ID \
    --region=us-central1 \
    --min-replica-count=0
```

### 4. Set Budget Alerts
- $100 warning
- $500 alert
- $1000 hard stop (disable billing)

---

## Troubleshooting

### Error: Quota Exceeded
**Solution**: Request quota increase
```bash
gcloud alpha quotas update \
    --service=aiplatform.googleapis.com \
    --consumer=projects/meddiag-gemini-training \
    --metric=aiplatform.googleapis.com/custom_model_training_vcpus \
    --unit=1/d/{region} \
    --value=100
```

### Error: Permission Denied
**Solution**: Verify IAM roles
```bash
gcloud projects get-iam-policy meddiag-gemini-training
```

### Training Job Fails
**Solution**: Check logs
```bash
gcloud ai training-jobs describe JOB_ID --region=us-central1
gcloud logging read "resource.type=aiplatform.googleapis.com/TrainingJob AND resource.labels.job_id=JOB_ID"
```

---

## Security Best Practices

✅ Enable VPC Service Controls for data isolation  
✅ Use Customer-Managed Encryption Keys (CMEK) for sensitive data  
✅ Rotate service account keys every 90 days  
✅ Enable audit logging  
✅ Restrict IAM permissions to minimum required  

---

## Next Steps

1. Review [`preprocess_mimic_cxr.py`](file:///C:/Users/MS/.gemini/antigravity/scratch/MedDiag-Gemini3-Hackathon/training/scripts/preprocess_mimic_cxr.py)
2. Run preprocessing on MIMIC-CXR data
3. Execute [`vertex_ai_training.py`](file:///C:/Users/MS/.gemini/antigravity/scratch/MedDiag-Gemini3-Hackathon/training/scripts/vertex_ai_training.py)
4. Evaluate model with [`evaluate_model.py`](file:///C:/Users/MS/.gemini/antigravity/scratch/MedDiag-Gemini3-Hackathon/training/scripts/evaluate_model.py)

---

## Resources

- **Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
- **Gemini Tuning Guide**: https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Support**: https://cloud.google.com/support

**Your training infrastructure is ready!** 🚀
