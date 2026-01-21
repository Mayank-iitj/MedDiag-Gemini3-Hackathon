"""
Robust JSON Parser with Fallback Recovery
Handles Gemini 3 responses with markdown code blocks and malformed JSON
"""

import json
import re
from typing import Dict, Any, Optional


def safe_parse_json(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON from Gemini response, handling markdown code blocks
    
    Args:
        response_text: Raw text response from Gemini 3
    
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    
    # Try direct JSON parse first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Extract JSON from markdown code blocks
    code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(code_block_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Try to find JSON object in raw text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, dict) and 'differentials' in parsed:
                return parsed
        except json.JSONDecodeError:
            continue
    
    return None


def validate_schema(data: Dict[str, Any]) -> bool:
    """
    Validate that JSON response contains all required fields
    
    Args:
        data: Parsed JSON dict
    
    Returns:
        True if valid, False otherwise
    """
    
    required_fields = ['findings', 'differentials', 'timeline', 'recommendations', 'confidence']
    
    if not all(field in data for field in required_fields):
        return False
    
    # Validate differentials structure
    if not isinstance(data['differentials'], list) or len(data['differentials']) == 0:
        return False
    
    for diff in data['differentials']:
        required_diff_fields = ['rank', 'diagnosis', 'probability', 'reasoning', 'evidence_pro', 'evidence_con', 'next_tests']
        if not all(field in diff for field in required_diff_fields):
            return False
    
    # Validate timeline structure
    timeline = data['timeline']
    if not all(key in timeline for key in ['days', 'events', 'diagnosis_probs']):
        return False
    
    return True


def fill_missing_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fill in missing fields with sensible defaults
    
    Args:
        data: Potentially incomplete JSON dict
    
    Returns:
        Complete JSON dict with defaults for missing fields
    """
    
    # Default structure
    defaults = {
        'findings': ["Analysis completed with available data"],
        'differentials': [
            {
                'rank': 1,
                'diagnosis': 'Insufficient data for specific diagnosis',
                'probability': 'Unable to estimate',
                'reasoning': 'Additional clinical information or higher quality images needed for differential diagnosis.',
                'evidence_pro': ['Available imaging data reviewed'],
                'evidence_con': ['Limited clinical context'],
                'next_tests': ['Complete medical history', 'Additional imaging as clinically indicated']
            }
        ],
        'timeline': {
            'days': [0, 7, 14],
            'events': ['Presentation', 'Expected follow-up', 'Reassessment'],
            'diagnosis_probs': [
                {'unknown': 1.0},
                {'unknown': 1.0},
                {'unknown': 1.0}
            ]
        },
        'recommendations': ['Clinical correlation recommended', 'Follow-up with treating physician'],
        'urgency': 'Unknown',
        'confidence': 'Low - insufficient data for confident analysis'
    }
    
    # Merge with defaults
    for key, default_value in defaults.items():
        if key not in data:
            data[key] = default_value
    
    # Ensure urgency field exists (may be named differently)
    if 'urgency' not in data:
        data['urgency'] = defaults['urgency']
    
    return data


def parse_gemini_response(response_text: str) -> Dict[str, Any]:
    """
    Complete pipeline: parse, validate, and fill missing fields
    
    Args:
        response_text: Raw Gemini 3 response
    
    Returns:
        Valid, complete JSON dict
    """
    
    parsed = safe_parse_json(response_text)
    
    if parsed is None:
        # Return error structure
        return {
            'error': True,
            'message': 'Failed to parse Gemini response as JSON',
            'findings': ['Response parsing error'],
            'differentials': [
                {
                    'rank': 1,
                    'diagnosis': 'Analysis Error',
                    'probability': 'N/A',
                    'reasoning': 'The AI response could not be properly parsed. Please try again.',
                    'evidence_pro': [],
                    'evidence_con': [],
                    'next_tests': []
                }
            ],
            'timeline': {
                'days': [0],
                'events': ['Error'],
                'diagnosis_probs': [{}]
            },
            'recommendations': ['Retry analysis', 'Contact support if issue persists'],
            'urgency': 'Unknown',
            'confidence': 'N/A'
        }
    
    # Fill missing fields
    parsed = fill_missing_fields(parsed)
    
    return parsed
