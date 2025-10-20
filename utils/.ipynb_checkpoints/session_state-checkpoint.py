import streamlit as st

def initialize_session_state():
    """Initialize all session state variables"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    if 'input_method' not in st.session_state:
        st.session_state.input_method = None

    # JSON dosya yolu (ihtiyaten)
    if 'json_path' not in st.session_state:
        st.session_state.json_path = ""

    if 'original_paragraphs' not in st.session_state:
        st.session_state.original_paragraphs = None
        
    if 'source_text' not in st.session_state:
        st.session_state.source_text = ""
        
    if 'edited_script' not in st.session_state:
        st.session_state.edited_script = ""
        
    if 'text_area_content' not in st.session_state:
        st.session_state.text_area_content = ""

    # ✅ Speaker seçimi (Edit Page – Bölüm 2 için gerekli)
    if 'selected_speakers' not in st.session_state:
        st.session_state.selected_speakers = []  # max 4 seçilecek

def navigate_to_step(step):
    """Navigate to a specific step"""
    st.session_state.current_step = step
    st.rerun()

def clear_session_for_new_podcast():
    """Clear session state for creating a new podcast"""
    keys_to_clear = [
        'original_paragraphs', 'source_text', 'edited_script', 
        'text_area_content', 'json_path', 'podcast_path', 'input_method',
        'selected_speakers'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
