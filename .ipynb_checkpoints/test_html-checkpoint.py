import streamlit as st

html_content = """
<div style='color: red; font-weight: bold;'>This is red bold text!</div>
"""

st.markdown(html_content, unsafe_allow_html=True)
