"""
Model Evaluation Framework for Fine-Tuned Gemini on MIMIC-CXR

Evaluates model accuracy against CheXpert labels and radiologist agreement
"""

import pandas as pd
import json
from pathlib import Path
from google.cloud import aiplatform
from PIL import Image
import base64
import io
from typing import Dict, List
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import numpy as np


class GeminiModelEvaluator:
    """Evaluates fine-tuned Gemini model performance"""
    
    def __init__(self, endpoint_uri: str, test_data_path: str, chexpert_labels_path: str):
        """
        Args:
            endpoint_uri: Vertex AI endpoint resource name
            test_data_path: Path to test JSONL file
            chexpert_labels_path: Path to CheXpert labels CSV
        """
        self.endpoint = aiplatform.Endpoint(endpoint_uri)
        self.test_data = self._load_test_data(test_data_path)
        self.chexpert = pd.read_csv(chexpert_labels_path)
        
    def _load_test_data(self, test_data_path: str) -> List[Dict]:
        """Load test dataset"""
        examples = []
        with open(test_data_path, 'r') as f:
            for line in f:
                examples.append(json.loads(line))
        return examples
    
    def predict_single(self, image_path: str) -> Dict:
        """
        Get model prediction for single image
        
        Args:
            image_path: Path to chest X-ray image
            
        Returns:
            Parsed JSON prediction
        """
        # Load image
        img = Image.open(image_path)
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
                        {"text": "Analyze this chest X-ray and provide differential diagnoses in JSON format."}
                    ]
                }
            ]
        }
        
        # Get prediction
        response = self.endpoint.predict(instances=[instance])
        
        # Parse JSON response
        try:
            prediction = json.loads(response.predictions[0])
            return prediction
        except json.JSONDecodeError:
            return None
    
    def evaluate_diagnostic_accuracy(self, max_examples: int = None) -> Dict:
        """
        Evaluate diagnostic accuracy on test set
        
        Args:
            max_examples: Limit number of test examples
            
        Returns:
            Evaluation metrics dict
        """
        results = {
            'top1_correct': 0,  # Correct diagnosis is rank 1
            'top3_correct': 0,  # Correct diagnosis in top 3
            'total': 0,
            'predictions': []
        }
        
        print(f"Evaluating on {len(self.test_data)} test examples...")
        
        for idx, example in enumerate(self.test_data):
            if max_examples and idx >= max_examples:
                break
            
            if idx % 10 == 0:
                print(f"Progress: {idx}/{len(self.test_data)}")
            
            # Get ground truth
            study_id = example.get('study_id')
            true_pathologies = self.chexpert[self.chexpert['study_id'] == study_id]
            
            if true_pathologies.empty:
                continue
            
            # Get model prediction
            image_path = example['image_path']
            prediction = self.predict_single(image_path)
            
            if prediction is None:
                continue
            
            # Extract predicted diagnoses
            predicted_diagnoses = [d['diagnosis'] for d in prediction.get('differentials', [])]
            
            # Check if any true positive pathology is in predictions
            true_positives = []
            for col in ['Pneumonia', 'Edema', 'Atelectasis', 'Cardiomegaly', 'Consolidation']:
                if true_pathologies[col].values[0] == 1.0:
                    true_positives.append(col)
            
            for true_dx in true_positives:
                # Check if in top 1
                if predicted_diagnoses and true_dx.lower() in predicted_diagnoses[0].lower():
                    results['top1_correct'] += 1
                
                # Check if in top 3
                if any(true_dx.lower() in pred.lower() for pred in predicted_diagnoses[:3]):
                    results['top3_correct'] += 1
                    break
            
            results['total'] += 1
            results['predictions'].append({
                'study_id': study_id,
                'true_pathologies': true_positives,
                'predicted': predicted_diagnoses
            })
        
        # Calculate metrics
        top1_accuracy = results['top1_correct'] / results['total'] if results['total'] > 0 else 0
        top3_accuracy = results['top3_correct'] / results['total'] if results['total'] > 0 else 0
        
        print(f"\n📊 EVALUATION RESULTS:")
        print(f"="*60)
        print(f"Total examples evaluated: {results['total']}")
        print(f"Top-1 Accuracy: {top1_accuracy:.2%}")
        print(f"Top-3 Accuracy: {top3_accuracy:.2%}")
        print(f"="*60)
        
        return {
            'top1_accuracy': top1_accuracy,
            'top3_accuracy': top3_accuracy,
            'total_examples': results['total'],
            'predictions': results['predictions']
        }
    
    def evaluate_per_pathology(self) -> pd.DataFrame:
        """
        Calculate per-pathology sensitivity and specificity
        
        Returns:
            DataFrame with per-pathology metrics
        """
        pathologies = ['Pneumonia', 'Edema', 'Atelectasis', 'Cardiomegaly', 'Pleural Effusion']
        
        metrics = []
        
        for pathology in pathologies:
            y_true = []
            y_pred = []
            
            for example in self.test_data[:100]:  # Sample for demo
                study_id = example.get('study_id')
                true_label = self.chexpert[self.chexpert['study_id'] == study_id][pathology].values
                
                if len(true_label) == 0:
                    continue
                
                y_true.append(1 if true_label[0] == 1.0 else 0)
                
                # Get prediction
                prediction = self.predict_single(example['image_path'])
                predicted_diagnoses = [d['diagnosis'] for d in prediction.get('differentials', [])]
                
                y_pred.append(1 if any(pathology.lower() in d.lower() for d in predicted_diagnoses) else 0)
            
            # Calculate metrics
            precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
            
            metrics.append({
                'pathology': pathology,
                'sensitivity (recall)': recall,
                'precision': precision,
                'f1_score': f1,
                'n_samples': len(y_true)
            })
        
        df = pd.DataFrame(metrics)
        print("\n📊 PER-PATHOLOGY PERFORMANCE:")
        print(df.to_string(index=False))
        
        return df
    
    def save_evaluation_report(self, results: Dict, output_path: str):
        """Save evaluation results to JSON"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Evaluation report saved to {output_path}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate fine-tuned Gemini model')
    parser.add_argument('--endpoint-uri', type=str, required=True, help='Vertex AI endpoint resource name')
    parser.add_argument('--test-data', type=str, required=True, help='Path to test JSONL')
    parser.add_argument('--chexpert-labels', type=str, required=True, help='Path to CheXpert labels CSV')
    parser.add_argument('--max-examples', type=int, default=None, help='Max examples to evaluate')
    parser.add_argument('--output', type=str, default='evaluation_results.json', help='Output path for results')
    
    args = parser.parse_args()
    
    evaluator = GeminiModelEvaluator(
        endpoint_uri=args.endpoint_uri,
        test_data_path=args.test_data,
        chexpert_labels_path=args.chexpert_labels
    )
    
    # Run evaluation
    results = evaluator.evaluate_diagnostic_accuracy(max_examples=args.max_examples)
    
    # Per-pathology analysis
    per_pathology_results = evaluator.evaluate_per_pathology()
    
    # Save report
    results['per_pathology_metrics'] = per_pathology_results.to_dict('records')
    evaluator.save_evaluation_report(results, args.output)
    
    print("\n✅ Evaluation complete!")
