import streamlit as st

def show_progress_bar():
    """Display step-by-step progress bar using Streamlit columns"""
    steps = [
        "📥 Input", 
        "🔍 Preview/Edit", 
        "🎤 Pick Speakers", 
        "🎨 Apply Themes", 
        "✍️ Final Touches", 
        "🎙️ Generate Podcast"
    ]
    current = st.session_state.current_step
    
    cols = st.columns(len(steps))
    
    for i, (step, col) in enumerate(zip(steps, cols), start=1):
        with col:
            if i < current:
                st.success(f"✅ Step {i}: {step}")
            elif i == current:
                st.info(f"⭐ Step {i}: {step}")
            else:
                st.write(f"⏳ Step {i}: {step}")
