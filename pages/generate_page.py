import streamlit as st
import os
from modules.FABA import generate_podcast
from utils.helpers import save_script_to_json
from utils.session_state import navigate_to_step, clear_session_for_new_podcast

def show():
    """Display the podcast generation page"""
    st.header("🎙️ Step 6: Generate Your Podcast")
    
    # Back button - back to Final Touches (Step 5)
    if st.button("⬅️ Back to Final Touches"):
        navigate_to_step(5)
    
    if "original_paragraphs" in st.session_state and st.session_state.original_paragraphs:
        _show_script_preview()
        st.divider()
        _show_generation_section()
        _show_generated_podcast()
    else:
        _show_no_data_warning()

def _show_script_preview():
    """Show script preview section"""
    with st.expander("📄 Script Preview", expanded=False):
        st.text_area(
            "Current script:", 
            value=st.session_state.get('edited_script', ''),
            height=200,
            disabled=True
        )

def _show_generation_section():
    """Show podcast generation section"""
    st.subheader("🎙️ Generate Audio")
    st.write("Ready to convert your script into a podcast? Click the button below to start the audio generation process.")

    picked = st.session_state.get("selected_speakers", [])
    if picked:
        st.success(f"Selected speakers ({len(picked)}): " + ", ".join(picked))
    else:
        st.info("No speakers selected in Step 3. Default 2 voices will be used.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🎙️ Generate Podcast Audio", 
            type="primary", 
            use_container_width=True
        ):
            _generate_podcast()

def _generate_podcast():
    """Generate the podcast audio"""
    # Use the string from text area or edited_script directly
    edited_script_text = st.session_state.get('text_area_content', st.session_state.edited_script)
    
    # Pass the entire string to save_script_to_json (which expects a string)
    json_path = save_script_to_json(edited_script_text)
    
    picked = st.session_state.get("selected_speakers", [])

    with st.spinner("🎙️ Generating your podcast... This may take a few minutes."):
        try:
            mp3_path = generate_podcast(json_path, selected_speakers=picked)
            st.session_state.podcast_path = mp3_path
            st.success("✅ Podcast generated successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error generating podcast: {e}")


def _show_generated_podcast():
    """Show the generated podcast if available"""
    if 'podcast_path' in st.session_state and os.path.exists(st.session_state.podcast_path):
        st.divider()
        st.subheader("🎧 Your Podcast is Ready!")
        
        with open(st.session_state.podcast_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download Podcast",
                data=audio_bytes,
                file_name="my_podcast.mp3",
                mime="audio/mp3",
                use_container_width=True,
                type="primary"
            )
        
        _show_restart_option()

def _show_restart_option():
    """Show option to start over"""
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🔄 Create Another Podcast", 
            use_container_width=True,
            type="secondary"
        ):
            clear_session_for_new_podcast()
            navigate_to_step(1)

def _show_no_data_warning():
    """Show warning when no script data is available"""
    st.warning("⚠️ No script data found. Please go back to Step 1 and upload content first.")
    if st.button("⬅️ Back to Input Selection", type="primary"):
        navigate_to_step(1)
