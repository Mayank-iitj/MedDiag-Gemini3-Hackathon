"""
Visualization Helpers for Medical Analysis
Creates interactive Plotly charts and formatted displays
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any
import streamlit as st


def create_timeline_chart(timeline_data: Dict[str, Any]) -> go.Figure:
    """
    Create interactive timeline showing disease progression probabilities
    
    Args:
        timeline_data: Timeline dict from Gemini response
    
    Returns:
        Plotly figure object
    """
    
    days = timeline_data.get('days', [0, 7, 14])
    events = timeline_data.get('events', ['Start', 'Mid', 'End'])
    diagnosis_probs = timeline_data.get('diagnosis_probs', [])
    
    # Extract all unique diagnoses
    all_diagnoses = set()
    for prob_dict in diagnosis_probs:
        all_diagnoses.update(prob_dict.keys())
    
    all_diagnoses = sorted(list(all_diagnoses))
    
    # Clinical color palette
    colors = ['#0066CC', '#DC3545', '#28A745', '#FFC107', '#6610F2', '#17A2B8']
    
    fig = go.Figure()
    
    for idx, diagnosis in enumerate(all_diagnoses):
        probs = [prob_dict.get(diagnosis, 0) for prob_dict in diagnosis_probs]
        
        fig.add_trace(go.Scatter(
            x=days,
            y=probs,
            mode='lines+markers',
            name=diagnosis,
            line=dict(width=3, color=colors[idx % len(colors)]),
            marker=dict(size=10),
            hovertemplate=f'<b>{diagnosis}</b><br>Day %{{x}}<br>Probability: %{{y:.1%}}<extra></extra>'
        ))
    
    # Add event annotations
    for day, event in zip(days, events):
        fig.add_annotation(
            x=day,
            y=-0.15,
            text=event,
            showarrow=False,
            font=dict(size=10, color='#666'),
            xref='x',
            yref='paper'
        )
    
    fig.update_layout(
        title={
            'text': 'Disease Progression Timeline',
            'font': {'size': 20, 'color': '#1A1A1A'}
        },
        xaxis_title='Days from Onset',
        yaxis_title='Probability',
        yaxis=dict(
            tickformat='.0%',
            range=[0, 1.05],
            gridcolor='#E0E0E0'
        ),
        xaxis=dict(
            gridcolor='#E0E0E0'
        ),
        hovermode='x unified',
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#F8F9FA',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(b=80),
        height=400
    )
    
    return fig


def create_urgency_gauge(urgency: str) -> go.Figure:
    """
    Create urgency indicator gauge
    
    Args:
        urgency: Urgency level (Routine/Urgent/Critical)
    
    Returns:
        Plotly gauge figure
    """
    
    urgency_mapping = {
        'routine': {'value': 30, 'color': '#28A745', 'text': 'Routine'},
        'urgent': {'value': 65, 'color': '#FFC107', 'text': 'Urgent'},
        'critical': {'value': 95, 'color': '#DC3545', 'text': 'Critical'},
        'unknown': {'value': 50, 'color': '#6C757D', 'text': 'Unknown'}
    }
    
    urgency_key = urgency.lower() if urgency.lower() in urgency_mapping else 'unknown'
    config = urgency_mapping[urgency_key]
    
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=config['value'],
        title={'text': f"<b>Urgency Level</b><br><span style='font-size:0.8em;color:{config['color']}'>{config['text']}</span>"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': config['color'], 'thickness': 0.75},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#E0E0E0',
            'steps': [
                {'range': [0, 40], 'color': '#D4EDDA'},
                {'range': [40, 70], 'color': '#FFF3CD'},
                {'range': [70, 100], 'color': '#F8D7DA'}
            ],
            'threshold': {
                'line': {'color': 'black', 'width': 4},
                'thickness': 0.75,
                'value': config['value']
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor='#F8F9FA',
        font={'size': 14}
    )
    
    return fig


def create_differential_table(differentials: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create formatted differential diagnosis table
    
    Args:
        differentials: List of differential diagnosis dicts
    
    Returns:
        Pandas DataFrame for display
    """
    
    table_data = []
    
    for diff in differentials:
        table_data.append({
            'Rank': diff.get('rank', '?'),
            'Diagnosis': diff.get('diagnosis', 'Unknown'),
            'Probability': diff.get('probability', 'N/A'),
            'Key Evidence': ', '.join(diff.get('evidence_pro', [])[:2]) if diff.get('evidence_pro') else 'None listed',
            'Next Tests': ', '.join(diff.get('next_tests', [])[:2]) if diff.get('next_tests') else 'Clinical correlation'
        })
    
    df = pd.DataFrame(table_data)
    return df



def create_reasoning_expander(differential: Dict, idx: int) -> None:
    """Display differential diagnosis reasoning directly (no expander)"""
    diagnosis = differential.get("diagnosis", "Unknown")
    probability = differential.get("probability", "Unknown")
    
    # Display as a card without expander
    st.markdown(f"""
    <div style="background-color: rgba(156, 39, 176, 0.05); padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #9c27b0;">
        <h4 style="color: #9c27b0; margin: 0 0 10px 0;">#{idx} - {diagnosis} ({probability})</h4>
        
        <div style="background-color: rgba(156, 39, 176, 0.1); padding: 8px; border-radius: 5px; margin-bottom: 10px;">
            <p style="color: #9c27b0; margin: 0; font-size: 12px;">&#128269; <strong>Observation</strong></p>
            <p style="color: #9c27b0; margin: 5px 0 0 0;"><strong>Diagnosis Considered:</strong> {diagnosis}</p>
            <p style="color: #9c27b0; margin: 5px 0 0 0;"><strong>Estimated Probability:</strong> {probability}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Clinical reasoning
    reasoning = differential.get("reasoning", "No reasoning provided")
    st.markdown(f"""
        <div style="margin: 10px 0;">
            <p style="color: #9c27b0; margin: 0; font-size: 14px;"><strong>&#128161; Clinical Reasoning</strong></p>
            <p style="color: #9c27b0; margin: 10px 0; line-height: 1.6;">{reasoning}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Supporting evidence
    evidence_pro = differential.get("evidence_pro", [])
    if evidence_pro:
        st.markdown("<p style=\"color: #9c27b0; margin: 10px 0 5px 0; font-size: 14px;\"><strong>&#9989; Supporting Evidence</strong></p>", unsafe_allow_html=True)
        for evidence in evidence_pro:
            st.markdown(f"<p style=\"color: #9c27b0; margin: 2px 0; padding-left: 10px;\">&#8226; {evidence}</p>", unsafe_allow_html=True)
    
    # Contradictory evidence
    evidence_con = differential.get("evidence_con", [])
    if evidence_con:
        st.markdown("<p style=\"color: #9c27b0; margin: 10px 0 5px 0; font-size: 14px;\"><strong>&#10060; Contradictory Evidence</strong></p>", unsafe_allow_html=True)
        for evidence in evidence_con:
            st.markdown(f"<p style=\"color: #9c27b0; margin: 2px 0; padding-left: 10px;\">&#8226; {evidence}</p>", unsafe_allow_html=True)
    
    # Recommended tests
    next_tests = differential.get("next_tests", [])
    if next_tests:
        st.markdown("<p style=\"color: #9c27b0; margin: 10px 0 5px 0; font-size: 14px;\"><strong>&#129514; Recommended Next Tests</strong></p>", unsafe_allow_html=True)
        for test in next_tests:
            st.markdown(f"<p style=\"color: #9c27b0; margin: 2px 0; padding-left: 10px;\">&#8226; {test}</p>", unsafe_allow_html=True)
    
    # Close the card div
    st.markdown("</div>", unsafe_allow_html=True)


def create_confidence_badge(confidence: str) -> str:
    """
    Create HTML confidence badge
    
    Args:
        confidence: Confidence string from Gemini
    
    Returns:
        HTML string for badge
    """
    
    if "high" in confidence.lower():
        color = "#28A745"
        icon = "✓"
    elif "moderate" in confidence.lower():
        color = "#FFC107"
        icon = "~"
    else:
        color = "#DC3545"
        icon = "!"
    
    return f"""
    <div style="display: inline-block; background-color: {color}; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 10px 0;">
        {icon} Confidence: {confidence}
    </div>
    """
