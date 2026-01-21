"""
MIMIC-CXR Data Preprocessing Script
Converts MIMIC-CXR radiology reports and images into training format for Gemini fine-tuning

Prerequisites:
- MIMIC-CXR dataset downloaded from PhysioNet
- pandas, PIL, json libraries installed
"""

import pandas as pd
import json
import os
from pathlib import Path
from PIL import Image
import re
from typing import Dict, List, Any


class MIMICCXRPreprocessor:
    """Preprocesses MIMIC-CXR data for Gemini fine-tuning"""
    
    def __init__(self, mimic_root: str, output_dir: str):
        """
        Args:
            mimic_root: Path to MIMIC-CXR root directory
            output_dir: Path to save processed training data
        """
        self.mimic_root = Path(mimic_root)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load metadata
        self.metadata = pd.read_csv(self.mimic_root / 'mimic-cxr-2.0.0-metadata.csv')
        self.chexpert = pd.read_csv(self.mimic_root / 'mimic-cxr-2.0.0-chexpert.csv')
        self.split = pd.read_csv(self.mimic_root / 'mimic-cxr-2.0.0-split.csv')
        
        print(f"Loaded {len(self.metadata)} total images")
        
    def parse_radiology_report(self, report_path: str) -> Dict[str, str]:
        """
        Parse free-text radiology report into structured sections
        
        Args:
            report_path: Path to report text file
            
        Returns:
            Dict with 'findings' and 'impression' sections
        """
        try:
            with open(report_path, 'r') as f:
                report_text = f.read()
            
            # Extract sections using regex
            findings_match = re.search(r'FINDINGS:(.*?)(?:IMPRESSION:|$)', report_text, re.DOTALL)
            impression_match = re.search(r'IMPRESSION:(.*?)$', report_text, re.DOTALL)
            
            findings = findings_match.group(1).strip() if findings_match else ""
            impression = impression_match.group(1).strip() if impression_match else ""
            
            return {
                'findings': findings,
                'impression': impression
            }
        except Exception as e:
            print(f"Error parsing {report_path}: {e}")
            return {'findings': '', 'impression': ''}
    
    def get_pathology_labels(self, study_id: int) -> Dict[str, float]:
        """
        Get CheXpert pathology labels for a study
        
        Args:
            study_id: Study ID from metadata
            
        Returns:
            Dict of pathology: label pairs
        """
        row = self.chexpert[self.chexpert['study_id'] == study_id]
        if row.empty:
            return {}
        
        pathologies = {
            'Atelectasis': row['Atelectasis'].values[0],
            'Cardiomegaly': row['Cardiomegaly'].values[0],
            'Consolidation': row['Consolidation'].values[0],
            'Edema': row['Edema'].values[0],
            'Pleural Effusion': row['Pleural Effusion'].values[0],
            'Pneumonia': row['Pneumonia'].values[0],
            'Pneumothorax': row['Pneumothorax'].values[0]
        }
        
        # Filter out NaN values
        return {k: v for k, v in pathologies.items() if pd.notna(v)}
    
    def create_training_example(self, row: pd.Series) -> Dict[str, Any]:
        """
        Create a single training example from metadata row
        
        Args:
            row: Pandas series with image metadata
            
        Returns:
            Training example dict
        """
        # Get image path
        subject_id = f"p{str(row['subject_id'])[:2]}"
        patient_id = f"p{row['subject_id']}"
        study_id = f"s{row['study_id']}"
        image_filename = f"{row['dicom_id']}.jpg"
        
        image_path = self.mimic_root / 'files' / subject_id / patient_id / study_id / image_filename
        
        if not image_path.exists():
            return None
        
        # Get report
        report_path = self.mimic_root / 'files' / subject_id / patient_id / study_id / f"{row['study_id']}.txt"
        report = self.parse_radiology_report(str(report_path))
        
        # Get pathology labels
        pathologies = self.get_pathology_labels(row['study_id'])
        
        # Determine primary diagnosis from positive labels
        positive_findings = [k for k, v in pathologies.items() if v == 1.0]
        
        if not positive_findings or not report['findings']:
            return None  # Skip cases without clear findings
        
        # Create structured training example
        example = {
            'image_path': str(image_path),
            'findings': report['findings'],
            'impression': report['impression'],
            'pathologies': pathologies,
            'primary_diagnosis': positive_findings[0] if positive_findings else None,
            'view_position': row['ViewPosition'],
            'study_id': row['study_id']
        }
        
        return example
    
    def convert_to_gemini_format(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert training example to Gemini fine-tuning format
        
        Args:
            example: Training example from create_training_example
            
        Returns:
            Gemini-formatted training example
        """
        # Create structured differential diagnosis output
        positive_pathologies = [k for k, v in example['pathologies'].items() if v == 1.0]
        uncertain_pathologies = [k for k, v in example['pathologies'].items() if v == -1.0]
        
        # Build differential list
        differentials = []
        for rank, diagnosis in enumerate(positive_pathologies[:3], 1):
            differentials.append({
                'rank': rank,
                'diagnosis': diagnosis,
                'probability': '70-90%' if rank == 1 else '30-50%',
                'reasoning': f"Imaging findings consistent with {diagnosis}. {example['impression']}",
                'evidence_pro': [example['findings'][:200]],  # Truncate long findings
                'evidence_con': [],
                'next_tests': ['Clinical correlation recommended']
            })
        
        # Gemini training format
        gemini_example = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [
                        {
                            'file_data': {
                                'file_uri': example['image_path'],
                                'mime_type': 'image/jpeg'
                            }
                        },
                        {
                            'text': f"Analyze this chest X-ray ({example['view_position']} view) and provide differential diagnoses."
                        }
                    ]
                },
                {
                    'role': 'model',
                    'parts': [
                        {
                            'text': json.dumps({
                                'findings': [example['findings']],
                                'differentials': differentials,
                                'recommendations': [example['impression']],
                                'confidence': 'High' if len(positive_pathologies) > 0 else 'Moderate'
                            })
                        }
                    ]
                }
            ]
        }
        
        return gemini_example
    
    def preprocess_dataset(self, max_examples: int = None):
        """
        Process entire MIMIC-CXR dataset
        
        Args:
            max_examples: Optional limit on number of examples (for testing)
        """
        # Merge metadata with split information
        data = self.metadata.merge(self.split, on='dicom_id')
        
        train_examples = []
        val_examples = []
        test_examples = []
        
        print(f"Processing {len(data)} images...")
        
        for idx, row in data.iterrows():
            if max_examples and idx >= max_examples:
                break
            
            if idx % 1000 == 0:
                print(f"Processed {idx}/{len(data)} images")
            
            example = self.create_training_example(row)
            if example is None:
                continue
            
            gemini_example = self.convert_to_gemini_format(example)
            
            # Split into train/val/test
            if row['split'] == 'train':
                train_examples.append(gemini_example)
            elif row['split'] == 'validate':
                val_examples.append(gemini_example)
            else:
                test_examples.append(gemini_example)
        
        # Save to JSONL format (required by Vertex AI)
        self._save_jsonl(train_examples, self.output_dir / 'train.jsonl')
        self._save_jsonl(val_examples, self.output_dir / 'val.jsonl')
        self._save_jsonl(test_examples, self.output_dir / 'test.jsonl')
        
        print(f"\nProcessing complete!")
        print(f"Train examples: {len(train_examples)}")
        print(f"Val examples: {len(val_examples)}")
        print(f"Test examples: {len(test_examples)}")
    
    def _save_jsonl(self, examples: List[Dict], output_path: Path):
        """Save examples to JSONL file"""
        with open(output_path, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')
        print(f"Saved {len(examples)} examples to {output_path}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Preprocess MIMIC-CXR for Gemini fine-tuning')
    parser.add_argument('--mimic-root', type=str, required=True, help='Path to MIMIC-CXR root directory')
    parser.add_argument('--output-dir', type=str, required=True, help='Output directory for processed data')
    parser.add_argument('--max-examples', type=int, default=None, help='Max examples to process (for testing)')
    
    args = parser.parse_args()
    
    preprocessor = MIMICCXRPreprocessor(
        mimic_root=args.mimic_root,
        output_dir=args.output_dir
    )
    
    preprocessor.preprocess_dataset(max_examples=args.max_examples)
    
    print("\n✅ Preprocessing complete! Next steps:")
    print("1. Upload processed data to Google Cloud Storage:")
    print(f"   gsutil -m cp -r {args.output_dir}/* gs://your-bucket/processed/")
    print("2. Run vertex_ai_training.py to fine-tune Gemini")
