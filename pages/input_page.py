import streamlit as st
import tempfile
import os
from modules.JSONcreater import convert_text_to_json
from modules.url_text_extractor import convert_url_to_json
from utils.helpers import reset_script_state
from utils.session_state import navigate_to_step

def show():
    """Display the input selection page"""
    st.header("📥 Step 1: Choose Your Input Method")

    # Input method selection
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "📄 Upload File",
            help="Upload a .txt or .docx file",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.input_method = "upload"

    with col2:
        if st.button(
            "🌐 Website URL",
            help="Extract content from a website URL",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.input_method = "url"

    # Route by input method
    if st.session_state.get("input_method") == "upload":
        _handle_file_upload()
    elif st.session_state.get("input_method") == "url":
        _handle_url_input()

def _handle_file_upload():
    """Handle file upload functionality"""
    st.subheader("📄 Upload Your File")
    uploaded_file = st.file_uploader(
        "Upload a .txt or .docx file", type=["txt", "docx"]
    )

    if uploaded_file:
        # Save to a temp file so downstream functions can read from disk
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(uploaded_file.read())
            temp_path = temp.name

        with st.spinner("Processing file..."):
            try:
                json_path, paragraphs = convert_text_to_json(temp_path)
                st.session_state.json_path = json_path
                reset_script_state(paragraphs)
                st.success("📄 File uploaded and processed successfully!")
                # ✅ Automatically go to Step 2 (Edit Page)
                navigate_to_step(2)
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")

def _handle_url_input():
    """Handle URL input functionality"""
    st.subheader("🌐 Enter Website URL")
    url = st.text_input("Paste a valid website URL here:")

    if url and st.button("🌐 Fetch Content", type="primary"):
        with st.spinner("Extracting content from website..."):
            try:
                json_path, paragraphs = convert_url_to_json(url)
                st.session_state.json_path = json_path
                reset_script_state(paragraphs)
                st.success("✅ Successfully extracted content from website!")
                # ✅ Automatically go to Step 2 (Edit Page)
                navigate_to_step(2)
            except Exception as e:
                st.error(f"❌ Could not extract content from the URL: {e}")
