
import sys
import streamlit as st

st.write("Python version:", sys.version)


from components.progress_bar import show_progress_bar
from pages import input_page, edit_page, voices_page, themes_page, generate_page, text_extraction
from utils.session_state import initialize_session_state
from utils.helpers import reset_script_state

st.set_page_config(
    page_title="🎙️ Text-to-Podcast App",
    page_icon="🎙️",
    layout="wide"
)

def main():
    initialize_session_state()

    st.title("🎙️ Text-to-Podcast App")
    show_progress_bar()
    st.divider()

    step = st.session_state.current_step

    if step == 1:
        input_page.show()
    elif step == 2:
        text_extraction.show_text_extraction_review()           # Preview/Edit
    elif step == 3:
        voices_page.show_speaker_selection()        # Pick Speakers
    elif step == 4:
        themes_page.show_themes_page()
    elif step == 5:
        edit_page.show()          # Final touches page?
    elif step == 6:
        generate_page.show()
    else:
        st.error(f"⚠️ Unknown step: {step}")

if __name__ == "__main__":
    main()

