# Script to completely fix viz_helpers.py
with open('utils/viz_helpers_backup.py', 'w', encoding='utf-8') as backup:
    with open('utils/viz_helpers.py', 'r', encoding='utf-8', errors='replace') as f:
        backup.write(f.read())

# Read the original file up to line 176 (before the corruption)
with open('utils/viz_helpers.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Write clean version
with open('utils/viz_helpers.py', 'w', encoding='utf-8') as f:
    # Write first 176 lines (before corruption)
    for i in range(min(176, len(lines))):
        line = lines[i]
        # Fix any corrupted emojis in the timeline chart title
        if i == 66:  # Line 67 (0-indexed)
            line = "            'text': 'Disease Progression Timeline',\r\n"
        f.write(line)
    
    # Add the properly formatted create_reasoning_expander function
    f.write('''
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
        st.markdown("<p style=\\"color: #9c27b0; margin: 10px 0 5px 0; font-size: 14px;\\"><strong>&#9989; Supporting Evidence</strong></p>", unsafe_allow_html=True)
        for evidence in evidence_pro:
            st.markdown(f"<p style=\\"color: #9c27b0; margin: 2px 0; padding-left: 10px;\\">&#8226; {evidence}</p>", unsafe_allow_html=True)
    
    # Contradictory evidence
    evidence_con = differential.get("evidence_con", [])
    if evidence_con:
        st.markdown("<p style=\\"color: #9c27b0; margin: 10px 0 5px 0; font-size: 14px;\\"><strong>&#10060; Contradictory Evidence</strong></p>", unsafe_allow_html=True)
        for evidence in evidence_con:
            st.markdown(f"<p style=\\"color: #9c27b0; margin: 2px 0; padding-left: 10px;\\">&#8226; {evidence}</p>", unsafe_allow_html=True)
    
    # Recommended tests
    next_tests = differential.get("next_tests", [])
    if next_tests:
        st.markdown("<p style=\\"color: #9c27b0; margin: 10px 0 5px 0; font-size: 14px;\\"><strong>&#129514; Recommended Next Tests</strong></p>", unsafe_allow_html=True)
        for test in next_tests:
            st.markdown(f"<p style=\\"color: #9c27b0; margin: 2px 0; padding-left: 10px;\\">&#8226; {test}</p>", unsafe_allow_html=True)
    
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
''')

print("File rewritten successfully")
