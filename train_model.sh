#!/bin/bash
# ============================================================================
# MedDiag Gemini Model Training Script
# ============================================================================
# This script provides a quick reference for training the Gemini model
# on MIMIC-CXR data using Google Cloud Vertex AI
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# CONFIGURATION
# ============================================================================

# Update these with your actual values
GCP_PROJECT_ID="your-gcp-project-id"
GCP_LOCATION="us-central1"
GCS_BUCKET="your-gcs-bucket"
MIMIC_CXR_ROOT="/path/to/mimic-cxr-2.0.0"
OUTPUT_DIR="./mimic-cxr-processed"

# Training parameters
BASE_MODEL="gemini-2.0-flash-001"
MODEL_NAME="meddiag_gemini_v1"
EPOCHS=3
LEARNING_RATE=0.0001
BATCH_SIZE=8
MAX_EXAMPLES=10000  # Start small for testing; remove for full dataset

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo -e "${BLUE}============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================================================
# CHECK PREREQUISITES
# ============================================================================

check_prerequisites() {
    print_header "CHECKING PREREQUISITES"
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 is installed"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_warning "Google Cloud SDK (gcloud) is not installed"
        print_info "Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "Google Cloud SDK is installed"
    
    # Check if gsutil is installed
    if ! command -v gsutil &> /dev/null; then
        print_error "gsutil is not installed (part of Google Cloud SDK)"
        exit 1
    fi
    print_success "gsutil is installed"
    
    # Check if required Python packages are installed
    if ! python3 -c "import google.cloud.aiplatform" &> /dev/null; then
        print_warning "google-cloud-aiplatform is not installed"
        print_info "Installing required packages..."
        pip install google-cloud-aiplatform pandas pillow
    fi
    print_success "Required Python packages are installed"
    
    echo ""
}

# ============================================================================
# STEP 1: PREPROCESS DATA
# ============================================================================

preprocess_data() {
    print_header "STEP 1: PREPROCESSING MIMIC-CXR DATA"
    
    if [ ! -d "$MIMIC_CXR_ROOT" ]; then
        print_error "MIMIC-CXR root directory not found: $MIMIC_CXR_ROOT"
        print_info "Update MIMIC_CXR_ROOT variable in this script"
        print_info "Apply for access at: https://physionet.org/content/mimic-cxr/2.0.0/"
        exit 1
    fi
    
    print_info "MIMIC-CXR root: $MIMIC_CXR_ROOT"
    print_info "Output directory: $OUTPUT_DIR"
    print_info "Max examples: $MAX_EXAMPLES"
    
    echo ""
    read -p "Start preprocessing? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Preprocessing cancelled"
        exit 0
    fi
    
    python3 training/scripts/preprocess_mimic_cxr.py \
        --mimic-root "$MIMIC_CXR_ROOT" \
        --output-dir "$OUTPUT_DIR" \
        --max-examples "$MAX_EXAMPLES"
    
    print_success "Preprocessing complete!"
    echo ""
}

# ============================================================================
# STEP 2: UPLOAD TO CLOUD STORAGE
# ============================================================================

upload_to_gcs() {
    print_header "STEP 2: UPLOADING DATA TO GOOGLE CLOUD STORAGE"
    
    if [ ! -d "$OUTPUT_DIR" ]; then
        print_error "Processed data directory not found: $OUTPUT_DIR"
        print_info "Run preprocessing step first"
        exit 1
    fi
    
    print_info "Uploading to: gs://$GCS_BUCKET/processed/"
    
    echo ""
    read -p "Start upload? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Upload cancelled"
        exit 0
    fi
    
    gsutil -m cp -r "$OUTPUT_DIR"/* "gs://$GCS_BUCKET/processed/"
    
    print_success "Upload complete!"
    echo ""
}

# ============================================================================
# STEP 3: FINE-TUNE MODEL
# ============================================================================

train_model() {
    print_header "STEP 3: FINE-TUNING GEMINI MODEL"
    
    print_info "Project ID: $GCP_PROJECT_ID"
    print_info "Location: $GCP_LOCATION"
    print_info "Base model: $BASE_MODEL"
    print_info "Model name: $MODEL_NAME"
    print_info "Training data: gs://$GCS_BUCKET/processed/train.jsonl"
    print_info "Validation data: gs://$GCS_BUCKET/processed/val.jsonl"
    print_info "Epochs: $EPOCHS"
    print_info "Learning rate: $LEARNING_RATE"
    print_info "Batch size: $BATCH_SIZE"
    
    print_warning "This will take 4-48 hours and cost \$30-\$4,000 depending on dataset size"
    
    echo ""
    read -p "Start training? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Training cancelled"
        exit 0
    fi
    
    python3 training/scripts/vertex_ai_training.py \
        --project-id "$GCP_PROJECT_ID" \
        --location "$GCP_LOCATION" \
        --training-data "gs://$GCS_BUCKET/processed/train.jsonl" \
        --validation-data "gs://$GCS_BUCKET/processed/val.jsonl" \
        --base-model "$BASE_MODEL" \
        --model-name "$MODEL_NAME" \
        --epochs "$EPOCHS" \
        --learning-rate "$LEARNING_RATE" \
        --batch-size "$BATCH_SIZE"
    
    print_success "Training job submitted!"
    print_info "Monitor progress in Vertex AI console: https://console.cloud.google.com/vertex-ai"
    echo ""
}

# ============================================================================
# STEP 4: DEPLOY MODEL
# ============================================================================

deploy_model() {
    print_header "STEP 4: DEPLOYING TRAINED MODEL"
    
    print_info "This will deploy the trained model to a Vertex AI endpoint"
    print_info "Model name: $MODEL_NAME"
    
    echo ""
    read -p "Deploy model? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    python3 training/scripts/vertex_ai_training.py \
        --project-id "$GCP_PROJECT_ID" \
        --location "$GCP_LOCATION" \
        --training-data "gs://$GCS_BUCKET/processed/train.jsonl" \
        --validation-data "gs://$GCS_BUCKET/processed/val.jsonl" \
        --model-name "$MODEL_NAME" \
        --deploy
    
    print_success "Model deployed!"
    echo ""
}

# ============================================================================
# STEP 5: EVALUATE MODEL
# ============================================================================

evaluate_model() {
    print_header "STEP 5: EVALUATING MODEL PERFORMANCE"
    
    print_warning "You need to update ENDPOINT_URI in this script first"
    print_info "Get endpoint URI from Vertex AI console or previous deployment step"
    
    # Update this with your actual endpoint URI after deployment
    ENDPOINT_URI="projects/$GCP_PROJECT_ID/locations/$GCP_LOCATION/endpoints/YOUR_ENDPOINT_ID"
    
    echo ""
    read -p "Start evaluation? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Evaluation cancelled"
        exit 0
    fi
    
    python3 training/scripts/evaluate_model.py \
        --endpoint-uri "$ENDPOINT_URI" \
        --test-data "$OUTPUT_DIR/test.jsonl" \
        --chexpert-labels "$MIMIC_CXR_ROOT/mimic-cxr-2.0.0-chexpert.csv" \
        --output "evaluation_results.json"
    
    print_success "Evaluation complete! Results saved to evaluation_results.json"
    echo ""
}

# ============================================================================
# MAIN MENU
# ============================================================================

show_menu() {
    print_header "MEDDIAG GEMINI MODEL TRAINING"
    echo ""
    echo "MODEL TO TRAIN: $BASE_MODEL (Gemini 2.0 Flash)"
    echo "DATASET: MIMIC-CXR (377K chest X-rays)"
    echo ""
    echo "Select an option:"
    echo ""
    echo "  1) Check prerequisites"
    echo "  2) Preprocess MIMIC-CXR data"
    echo "  3) Upload data to Google Cloud Storage"
    echo "  4) Fine-tune Gemini model"
    echo "  5) Deploy trained model"
    echo "  6) Evaluate model performance"
    echo "  7) Run full pipeline (steps 2-4)"
    echo "  8) Show training documentation"
    echo "  9) Exit"
    echo ""
}

show_documentation() {
    print_header "TRAINING DOCUMENTATION"
    echo ""
    echo "📄 MODEL_TRAINING.md - Complete training guide"
    echo "📄 training/README.md - Training infrastructure overview"
    echo "📄 FINE_TUNING_GUIDE.md - Fine-tuning strategy and datasets"
    echo "📄 training/guides/physionet_credentialing.md - Get MIMIC-CXR access"
    echo "📄 training/guides/vertex_ai_setup.md - Set up Google Cloud"
    echo ""
    echo "Key Scripts:"
    echo "  • training/scripts/preprocess_mimic_cxr.py - Data preprocessing"
    echo "  • training/scripts/vertex_ai_training.py - Model training"
    echo "  • training/scripts/evaluate_model.py - Model evaluation"
    echo ""
    echo "External Resources:"
    echo "  • MIMIC-CXR: https://physionet.org/content/mimic-cxr/2.0.0/"
    echo "  • Vertex AI Docs: https://cloud.google.com/vertex-ai/docs"
    echo ""
}

run_full_pipeline() {
    print_header "RUNNING FULL TRAINING PIPELINE"
    print_warning "This will run steps 2-4: Preprocess, Upload, Train"
    print_warning "This may take hours and cost \$30-\$4,000"
    
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Pipeline cancelled"
        return
    fi
    
    preprocess_data
    upload_to_gcs
    train_model
    
    print_success "Pipeline complete!"
    print_info "Next steps: Deploy model (option 5) and evaluate (option 6)"
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

main() {
    while true; do
        show_menu
        read -p "Enter option (1-9): " choice
        echo ""
        
        case $choice in
            1)
                check_prerequisites
                ;;
            2)
                preprocess_data
                ;;
            3)
                upload_to_gcs
                ;;
            4)
                train_model
                ;;
            5)
                deploy_model
                ;;
            6)
                evaluate_model
                ;;
            7)
                run_full_pipeline
                ;;
            8)
                show_documentation
                ;;
            9)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 1-9"
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
        clear
    done
}

# Run main menu
main
