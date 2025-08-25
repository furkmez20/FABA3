import streamlit as st
from modules.gemini_generator import generate_script_with_prompt
from utils.helpers import reset_script_state, save_script_to_json
from utils.session_state import navigate_to_step

# Enhanced theme prompts with categories
THEME_CATEGORIES = {
    "🎯 Audience Targeting": {
        "👶 Children (Ages 8-12)": "Rewrite this content to be appropriate and engaging for children aged 8-12. Use simple language, fun examples, exciting analogies, and an enthusiastic tone. Remove complex concepts and make it educational yet entertaining with age-appropriate humor.",
        "🎓 Experts & Professionals": "Rewrite this content for an expert audience in the field. Use technical terminology, assume advanced knowledge, include nuanced details, cite methodologies, and adopt a professional, authoritative tone suitable for industry professionals.",
        "👥 General Public": "Make this content accessible to the general public. Use clear, everyday language while maintaining accuracy. Include helpful analogies and explanations for technical terms.",
        "🎓 Students & Learners": "Structure this content for students and active learners. Include learning objectives, key takeaways, and study-friendly formatting with clear explanations."
    },

    "📝 Content Structure": {
        "📖 Add Strong Introduction": "Add a compelling introductory section that hooks the listener, clearly explains what this episode will cover, why it matters, and what listeners will gain. Make it engaging and set proper expectations.",
        "📋 Add Summary & Key Points": "Add a comprehensive summary section with bullet points of key takeaways, main insights, and actionable items that listeners can reference later.",
        "❓ Add Q&A Section": "Transform this into a Q&A format by creating relevant questions that the content answers, making it more interactive and easier to follow.",
        "📚 Chapter Structure": "Organize this content into clear chapters or sections with descriptive headings, making it easy to navigate and reference specific topics."
    },

    "🎭 Tone & Style": {
        "💬 Conversational & Casual": "Make this content highly conversational and natural. Use casual language, contractions, rhetorical questions, personal anecdotes, and a friendly tone as if talking to a close friend.",
        "🎪 Entertaining & Engaging": "Add entertainment value with humor, interesting anecdotes, surprising facts, and engaging storytelling elements while maintaining the core message.",
        "📺 Documentary Style": "Write this in a compelling documentary narrative style with dramatic tension, investigative elements, and storytelling techniques that keep listeners engaged.",
        "🎯 Motivational & Inspiring": "Rewrite with an inspiring, motivational tone that empowers listeners. Include encouraging language, success stories, and calls to action.",
        "🔬 Scientific & Analytical": "Present this content with a scientific, analytical approach. Include data, evidence, logical reasoning, and objective analysis while remaining accessible."
    },

    "🌟 Special Formats": {
        "📻 Radio Show Style": "Format this as an engaging radio show with smooth transitions, catchy segments, and broadcast-friendly language that flows naturally.",
        "🎙️ Interview Format": "Present this as if it's an interview, with natural questions and detailed answers that explore the topic comprehensively.",
        "📖 Storytelling Narrative": "Transform this content into a compelling story with narrative elements, character development, plot progression, and storytelling techniques.",
        "🎬 Behind-the-Scenes": "Present this content as if revealing behind-the-scenes insights, with insider knowledge, exclusive details, and a revealing tone."
    }
}

def show_themes_page():
    st.header("🎨 Step 4: Apply Themes to Your Script")

    # Initialize initial_original_paragraphs if missing (for reset)
    if "initial_original_paragraphs" not in st.session_state and "original_paragraphs" in st.session_state:
        st.session_state.initial_original_paragraphs = list(st.session_state.original_paragraphs)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Speaker Selection"):
            navigate_to_step(3)
    with col2:
        if st.button("➡️ Proceed to Final Review", type="primary"):
            navigate_to_step(5)

    if "original_paragraphs" in st.session_state and st.session_state.original_paragraphs:
        show_theme_categories()
        st.divider()
        _inline_edit_script()
    else:
        show_no_data_warning()

def show_theme_categories():
    st.write("Choose from our curated themes to instantly transform your podcast script:")

    tab_names = list(THEME_CATEGORIES.keys())
    tabs = st.tabs(tab_names)

    for tab, category_name in zip(tabs, tab_names):
        with tab:
            st.write(f"Themes for **{category_name.strip('🎯📝🎭🌟').strip()}**")
            themes = THEME_CATEGORIES[category_name]
            cols = st.columns(2)
            theme_items = list(themes.items())

            for i, (theme_name, theme_prompt) in enumerate(theme_items):
                col = cols[i % 2]
                with col:
                    if st.button(theme_name, key=f"theme_{category_name}_{i}", use_container_width=True, help=f"Apply {theme_name} theme to your script"):
                        apply_theme(theme_prompt, theme_name)

def apply_theme(prompt, theme_name):
    with st.spinner(f"Applying {theme_name}..."):
        try:
            # new_paragraphs is list[str]
            new_paragraphs = generate_script_with_prompt(st.session_state.original_paragraphs, prompt)
            reset_script_state(new_paragraphs)
            save_script_to_json(new_paragraphs)

            # Format with speakers for editor display
            formatted = format_script_with_speakers(new_paragraphs)

            st.session_state.applied_theme = theme_name
            st.session_state.edited_script = formatted

            st.success(f"✅ {theme_name} applied successfully!")
            st.balloons()
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error applying {theme_name}: {e}")

def format_script_with_speakers(paragraphs):
    speaker_mapping = st.session_state.get("speaker_mapping", {})
    formatted = []
    num_speakers = len(speaker_mapping) or 2

    for i, p in enumerate(paragraphs):
        speaker_key = f"Speaker {(i % num_speakers) + 1}"
        speaker_name = speaker_mapping.get(speaker_key, speaker_key)
        formatted.append(f"{speaker_name}: {p}")

    return "\n\n".join(formatted)

def _inline_edit_script():
    st.subheader("✏️ Script Editor (Podcast Format)")

    if "edited_script" not in st.session_state:
        st.session_state.edited_script = format_script_with_speakers(st.session_state.original_paragraphs)

    edited_text = st.text_area(
        "Edit your script here (Speaker: Dialogue):",
        value=st.session_state.edited_script,
        height=350,
        key="inline_edit_area"
    )

    if "applied_theme" in st.session_state:
        st.info(f"🎨 Current theme: **{st.session_state.applied_theme}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Save Changes"):
            st.session_state.edited_script = edited_text

            # Parse speaker: text lines separated by double newlines
            paragraphs = []
            for chunk in edited_text.split("\n\n"):
                if ":" in chunk:
                    speaker, text = chunk.split(":", 1)
                    paragraphs.append({"speaker": speaker.strip(), "text": text.strip()})
                else:
                    paragraphs.append({"speaker": "Unknown", "text": chunk.strip()})

            reset_script_state(paragraphs)
            save_script_to_json(paragraphs)
            st.success("✅ Saved successfully!")
            st.rerun()

    with col2:
        if st.button("↩️ Discard Changes"):
            st.session_state.edited_script = format_script_with_speakers(st.session_state.original_paragraphs)
            st.success("ℹ️ Changes discarded.")
            st.rerun()

    with col3:
        if st.button("🔄 Reset to Original"):
            st.session_state.original_paragraphs = list(st.session_state.initial_original_paragraphs)
            st.session_state.edited_script = format_script_with_speakers(st.session_state.initial_original_paragraphs)
            save_script_to_json(st.session_state.initial_original_paragraphs)
            st.success("✅ Script reset to original!")
            st.rerun()

def show_no_data_warning():
    st.warning("⚠️ No script data found. Please go back and generate your script first.")
