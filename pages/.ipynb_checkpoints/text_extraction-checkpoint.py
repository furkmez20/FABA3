import streamlit as st
from utils.session_state import navigate_to_step
from utils.helpers import reset_script_state, save_script_to_json

def show_text_extraction_review():
    st.header("📄 Step 2: Review & Edit Extracted Script")
    
    if "original_paragraphs" in st.session_state and st.session_state.original_paragraphs:
        # Get current edited script or fallback to original paragraphs joined
        current_script = st.session_state.get("edited_script", "\n\n".join(st.session_state.original_paragraphs))
        
        # Editable text area
        edited_script = st.text_area(
            "Please review and edit your extracted script below:",
            value=current_script,
            height=400,
            key="edited_text_area"
        )
        
        # Save edits if changed
        if edited_script != current_script:
            paragraphs = [p.strip() for p in edited_script.split("\n\n") if p.strip()]
            reset_script_state(paragraphs)
            save_script_to_json(paragraphs)
            st.session_state.edited_script = edited_script
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Input Selection"):
                navigate_to_step(1)
        with col2:
            if st.button("➡️ Proceed to Speaker Selection", type="primary"):
                navigate_to_step(3)  # Speaker selection page index
                
    else:
        st.warning("⚠️ No extracted script found. Please upload your content first.")
        if st.button("⬅️ Back to Input Selection"):
            navigate_to_step(1)

