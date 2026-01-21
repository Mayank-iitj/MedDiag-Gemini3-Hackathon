"""
Vertex AI Fine-Tuning Script for Gemini on MIMIC-CXR Data

Prerequisites:
- Google Cloud project with Vertex AI enabled
- Preprocessed MIMIC-CXR data in Cloud Storage
- google-cloud-aiplatform installed
"""

from google.cloud import aiplatform
from google.cloud.aiplatform import gapic
import argparse
from datetime import datetime


def tune_gemini_model(
    project_id: str,
    location: str,
    training_data_uri: str,
    validation_data_uri: str,
    base_model: str = "gemini-2.0-flash-001",
    tuned_model_display_name: str = None,
    epochs: int = 3,
    learning_rate: float = 0.0001,
    batch_size: int = 8
):
    """
    Fine-tune Gemini model on MIMIC-CXR data using Vertex AI
    
    Args:
        project_id: Google Cloud project ID
        location: GCP region (e.g., 'us-central1')
        training_data_uri: GCS URI to training data (gs://bucket/train.jsonl)
        validation_data_uri: GCS URI to validation data
        base_model: Base Gemini model to fine-tune
        tuned_model_display_name: Name for tuned model
        epochs: Number of training epochs
        learning_rate: Learning rate
        batch_size: Training batch size
    
    Returns:
        Tuned model resource
    """
    
    # Initialize Vertex AI
    aiplatform.init(project=project_id, location=location)
    
    # Generate model name if not provided
    if tuned_model_display_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tuned_model_display_name = f"meddiag_gemini_mimic_cxr_{timestamp}"
    
    print(f"🚀 Starting fine-tuning job: {tuned_model_display_name}")
    print(f"Base model: {base_model}")
    print(f"Training data: {training_data_uri}")
    print(f"Validation data: {validation_data_uri}")
    print(f"Hyperparameters: epochs={epochs}, lr={learning_rate}, batch_size={batch_size}")
    
    # Configure tuning job
    tuning_job = aiplatform.PipelineJob(
        display_name=tuned_model_display_name,
        template_path="https://us-kfp.pkg.dev/ml-pipeline/large-language-model-pipelines/tune-large-model/v2.0.0",
        parameter_values={
            "model_display_name": tuned_model_display_name,
            "location": location,
            "large_model_reference": base_model,
            "train_steps": epochs * 1000,  # Approximate steps based on dataset size
            "learning_rate_multiplier": learning_rate,
            "batch_size": batch_size,
            "dataset_uri": training_data_uri,
            "validation_dataset_uri": validation_data_uri,
            "evaluation_interval": 100,
            "early_stopping": True,
            "tensorboard_log_dir": f"gs://{project_id}-tensorboard/logs/{tuned_model_display_name}"
        },
        enable_caching=False,
    )
    
    print("\n⏳ Submitting tuning job... This may take 4-48 hours depending on dataset size.")
    
    # Submit job
    tuning_job.submit()
    
    print(f"✅ Tuning job submitted: {tuning_job.resource_name}")
    print(f"Monitor progress: https://console.cloud.google.com/vertex-ai/locations/{location}/pipelines/runs/{tuning_job.job_id}")
    
    # Wait for completion (optional - comment out for async execution)
    print("\n⏳ Waiting for completion... (This will take hours. You can exit and check status later.)")
    tuning_job.wait()
    
    print(f"\n🎉 Tuning complete! Model: {tuned_model_display_name}")
    
    return tuning_job


def deploy_tuned_model(
    project_id: str,
    location: str,
    model_display_name: str,
    endpoint_display_name: str = None,
    machine_type: str = "n1-standard-4",
    min_replicas: int = 1,
    max_replicas: int = 3
):
    """
    Deploy fine-tuned model to an endpoint
    
    Args:
        project_id: Google Cloud project ID
        location: GCP region
        model_display_name: Name of tuned model to deploy
        endpoint_display_name: Name for deployment endpoint
        machine_type: VM type for serving
        min_replicas: Minimum serving replicas
        max_replicas: Maximum serving replicas (for autoscaling)
    
    Returns:
        Endpoint resource
    """
    
    aiplatform.init(project=project_id, location=location)
    
    # Get model
    model =aiplatform.Model.list(filter=f'display_name="{model_display_name}"')[0]
    
    print(f"📦 Deploying model: {model.display_name}")
    
    # Create or get endpoint
    if endpoint_display_name is None:
        endpoint_display_name = f"{model_display_name}_endpoint"
    
    endpoints = aiplatform.Endpoint.list(filter=f'display_name="{endpoint_display_name}"')
    
    if endpoints:
        endpoint = endpoints[0]
        print(f"Using existing endpoint: {endpoint.display_name}")
    else:
        endpoint = aiplatform.Endpoint.create(display_name=endpoint_display_name)
        print(f"Created new endpoint: {endpoint.display_name}")
    
    # Deploy model to endpoint
    print(f"⏳ Deploying to endpoint... (5-10 minutes)")
    
    model.deploy(
        endpoint=endpoint,
        machine_type=machine_type,
        min_replica_count=min_replicas,
        max_replica_count=max_replicas,
        traffic_percentage=100,
        deploy_request_timeout=1200
    )
    
    print(f"✅ Model deployed!")
    print(f"Endpoint URI: {endpoint.resource_name}")
    
    return endpoint


def test_tuned_model(endpoint_uri: str, test_image_path: str):
    """
    Test fine-tuned model with a sample image
    
    Args:
        endpoint_uri: Endpoint resource name
        test_image_path: Path to test chest X-ray image
    """
    from PIL import Image
    import base64
    import io
    
    # Load endpoint
    endpoint = aiplatform.Endpoint(endpoint_uri)
    
    # Load and encode image
    img = Image.open(test_image_path)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Prepare request
    instance = {
        "content": [
            {
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}},
                    {"text": "Analyze this chest X-ray and provide differential diagnoses."}
                ]
            }
        ]
    }
    
    print("🔍 Testing model with sample image...")
    
    # Get prediction
    response = endpoint.predict(instances=[instance])
    
    print("\n📊 Model Response:")
    print(response.predictions[0])
    
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fine-tune Gemini on MIMIC-CXR using Vertex AI')
    
    # Required arguments
    parser.add_argument('--project-id', type=str, required=True, help='Google Cloud project ID')
    parser.add_argument('--location', type=str, default='us-central1', help='GCP region')
    parser.add_argument('--training-data', type=str, required=True, help='GCS URI to training data')
    parser.add_argument('--validation-data', type=str, required=True, help='GCS URI to validation data')
    
    # Optional tuning parameters
    parser.add_argument('--base-model', type=str, default='gemini-2.0-flash-001', help='Base Gemini model')
    parser.add_argument('--model-name', type=str, default=None, help='Tuned model name')
    parser.add_argument('--epochs', type=int, default=3, help='Number of epochs')
    parser.add_argument('--learning-rate', type=float, default=0.0001, help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=8, help='Batch size')
    
    # Deployment arguments
    parser.add_argument('--deploy', action='store_true', help='Deploy model after tuning')
    parser.add_argument('--endpoint-name', type=str, default=None, help='Endpoint name for deployment')
    
    args = parser.parse_args()
    
    # Run tuning
    tuning_job = tune_gemini_model(
        project_id=args.project_id,
        location=args.location,
        training_data_uri=args.training_data,
        validation_data_uri=args.validation_data,
        base_model=args.base_model,
        tuned_model_display_name=args.model_name,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size
    )
    
    # Deploy if requested
    if args.deploy:
        print("\n" + "="*60)
        print("DEPLOYING MODEL")
        print("="*60 + "\n")
        
        endpoint = deploy_tuned_model(
            project_id=args.project_id,
            location=args.location,
            model_display_name=args.model_name,
            endpoint_display_name=args.endpoint_name
        )
        
        print(f"\n✅ Training and deployment complete!")
        print(f"Endpoint: {endpoint.resource_name}")
        print(f"\nUpdate your app.py to use this endpoint:")
        print(f"  endpoint = aiplatform.Endpoint('{endpoint.resource_name}')")
    else:
        print(f"\n✅ Training complete! Model: {args.model_name}")
        print(f"\nTo deploy, run:")
        print(f"  python vertex_ai_training.py --deploy --model-name {args.model_name} --endpoint-name your_endpoint")
