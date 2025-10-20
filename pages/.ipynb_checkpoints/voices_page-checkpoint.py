import streamlit as st
import os, requests
from utils.session_state import navigate_to_step

ELEVENLABS_VOICES = {
    "Female – Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Female – Bella": "EXAVITQu4vr4xnSDxMaL",
    "Female – Elli": "MF3mGyEYCl7XYWbV9V6O",
    "Female – Sarah": "pMsXgVXv3BLzUgSXRplE",
    "Male – Adam": "pNInz6obpgDQGcFmaJgB",
    "Male – Antony": "ErXwobaYiN019PkySvjV",
    "Male – Josh": "TxGEqnHWrfWFTfGW9XjX",
    "Male – Eric": "cjVigY5qzO86Huf0OWal",
}

@st.cache_data(show_spinner=False)
def _preview_tts_bytes(voice_id: str, text: str):
    # Your existing function here...
    pass

def show_speaker_selection():
    st.header("🎤 Step 3: Choose Speakers")
    st.caption("Preview voices and select up to 4 speakers.")
    
    if "original_paragraphs" not in st.session_state or not st.session_state.original_paragraphs:
        st.warning("⚠️ No script found. Please go back to Step 2.")
        if st.button("⬅️ Back to Script Review"):
            navigate_to_step(2)
        return

    default_preview = "This is a short sample for the podcast voice preview."
    sample = st.text_input("Preview text (short):", value=default_preview, help="Keep it short to save credits.")
    
    options = list(ELEVENLABS_VOICES.keys())
    current = set(st.session_state.get("selected_speakers", []))
    
    cols = st.columns(4)
    for idx, label in enumerate(options):
        with cols[idx % 4]:
            st.write(f"**{label}**")
            if st.button("▶︎ Preview", key=f"pv_{label}"):
                try:
                    audio_bytes = _preview_tts_bytes(ELEVENLABS_VOICES[label], (sample or default_preview).strip())
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.error(f"Preview failed: {e}")
            
            checked = label in current
            new_checked = st.checkbox("Select", value=checked, key=f"chk_{label}")
            if new_checked and not checked:
                if len(current) >= 4:
                    st.warning("You can select at most 4 voices.")
                else:
                    current.add(label)
            elif not new_checked and checked:
                current.remove(label)
    
    st.session_state.selected_speakers = list(current)
    
    if current:
        st.success(f"Selected ({len(current)}): " + ", ".join(sorted(current)))
    else:
        st.info("No speakers selected. Default voices will be used.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Script Review"):
            navigate_to_step(2)
    with col2:
        if st.button("➡️ Proceed to Apply Themes", type="primary"):
            navigate_to_step(4)