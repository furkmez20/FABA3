# pages/edit_page.py

import streamlit as st
from modules.gemini_generator import generate_script_with_prompt
from utils.helpers import save_script_to_json, reset_script_state
from utils.session_state import navigate_to_step

# -------------------------------
# Helpers: speaker <-> text parse
# -------------------------------
def parse_speaker_script(script_text: str):
    """'Speaker: text' satırlarını [{'speaker':..,'text':..}, ...] listesine çevirir."""
    out = []
    for raw in (script_text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if ":" in line:
            speaker, text = line.split(":", 1)
            out.append({"speaker": speaker.strip(), "text": text.strip()})
        else:
            out.append({"speaker": "Unknown", "text": line})
    return out

def recompose_speaker_script(parsed):
    """[{'speaker':..,'text':..}] -> 'Speaker: text' birleşik string (textarea için)."""
    lines = [f"{p.get('speaker','Unknown')}: {p.get('text','')}" for p in parsed if p.get("text")]
    return "\n\n".join(lines)

def _as_text_list(items):
    """Her türlü girdiyi güvenle List[str]'e normalleştirir."""
    if not items:
        return []
    out = []
    for it in items:
        if isinstance(it, str):
            s = it.strip()
        elif isinstance(it, dict):
            s = (it.get("text") or "").strip()
        else:
            s = str(it).strip()
        if s:
            out.append(s)
    return out

# -------------------------------
# Page
# -------------------------------
def show():
    st.header("🔍 Step 5: Final Review & AI Enhancement (Optional)")

    if not st.session_state.get("original_paragraphs"):
        st.warning("⚠️ No script data found. Please go back to Step 1 and upload content first.")
        if st.button("⬅️ Back to Input Selection"):
            navigate_to_step(1)
        return

    # İlk açılışta textarea boşsa, mevcut paragrafları 'Speaker: text' formuna dök
    if not st.session_state.get("edited_script"):
        paragraphs = _as_text_list(st.session_state.original_paragraphs)
        # varsa tema sayfasından gelen eşleme; yoksa 2 konuşmacı arasında sırala
        speaker_mapping = st.session_state.get("speaker_mapping", {})
        num_speakers = max(len(speaker_mapping), 2)
        formatted = []
        for i, p in enumerate(paragraphs):
            key = f"Speaker {(i % num_speakers) + 1}"
            name = speaker_mapping.get(key, key)
            formatted.append(f"{name}: {p}")
        st.session_state.edited_script = "\n\n".join(formatted)

    # Serbest düzenleme alanı (Speaker: Metin)
    edited_script = st.text_area(
        "Final Script Review (Speaker: Dialogue):",
        value=st.session_state.edited_script,
        height=400,
        key="final_text_area",
    )
    st.session_state.edited_script = edited_script  # canlı güncelle

    # AI prompt
    prompt = st.text_area(
        "Optional: Enter a theme or style to enhance the script:",
        height=100,
        placeholder="e.g., 'Make it more conversational and add humor'",
        key="enhance_prompt",
    )

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("⬅️ Back to Theme Selection"):
            navigate_to_step(4)

    with col2:
        if st.button("✨ Regenerate Script with AI"):
            if not prompt.strip():
                st.warning("Please enter a prompt to enhance the script.")
            else:
                with st.spinner("Generating enhanced script with AI..."):
                    try:
                        # 1) Textarea’yı parse et → [{'speaker','text'}, ...]
                        parsed = parse_speaker_script(st.session_state.edited_script)

                        # 2) Sadece METİNLER → List[str] (AI girişinde dict olmayacak)
                        base_texts = [p["text"] for p in parsed]

                        # 3) AI’den yeni paragraflar → List[str]
                        new_texts = generate_script_with_prompt(base_texts, prompt)

                        # 4) Emniyet: normalize → List[str]
                        new_texts = _as_text_list(new_texts)

                        # 5) Speaker sırasını koruyarak textarea için tekrar birleştir
                        new_parsed = []
                        for i, t in enumerate(new_texts):
                            spk = parsed[i]["speaker"] if i < len(parsed) else "Speaker 1"
                            new_parsed.append({"speaker": spk, "text": t})

                        # 6) TEXTAREA'yı güncelle (gösterim)
                        st.session_state.edited_script = recompose_speaker_script(new_parsed)

                        # 7) Uygulama state’ini SADECE List[str] ile güncelle
                        reset_script_state(new_texts)

                        # 8) JSON'u da SADECE List[str] olarak kaydet (FABA okuyabiliyor)
                        save_script_to_json(new_texts)

                        st.success("✅ Script enhanced successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error enhancing script: {e}")

    with col3:
        if st.button("➡️ Generate Podcast", type="primary"):
            # Bir sonraki adım id'n buysa bırak; farklıysa projendeki step id’ye göre değiştir
            navigate_to_step(6)
