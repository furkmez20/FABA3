# modules/gemini_generator.py

from __future__ import annotations
from typing import Any, List
import os
import re
import google.genai as genai

# -----------------------------
# Güvenli API anahtarı okuma
# -----------------------------
def _read_gemini_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            import streamlit as st  # type: ignore
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            key = ""
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY bulunamadı (env veya .streamlit/secrets.toml)."
        )
    return key


client = genai.Client(api_key=_read_gemini_key())

# -----------------------------
# Yardımcılar: normalize/postprocess
# -----------------------------
def _as_text_list(items: Any) -> List[str]:
    """Her türlü girdiyi güvenli şekilde List[str]'e normalleştirir."""
    if not items:
        return []
    out: List[str] = []
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

def _postprocess_to_list(text_or_list: Any) -> List[str]:
    """
    Modelden geleni List[str]'e çevirir.
    - Liste dönerse normalize eder
    - String dönerse çift boş satıra göre böler
    - Satır başındaki 'Speaker X:' gibi etiketleri temizler
    """
    if isinstance(text_or_list, list):
        arr = _as_text_list(text_or_list)
    else:
        whole = str(text_or_list or "").strip()
        # paragrafları çift boş satıra göre böl
        arr = [p.strip() for p in re.split(r"\n\s*\n+", whole) if p.strip()]

    cleaned: List[str] = []
    for p in arr:
        # "Speaker 1: ..." öneklerini kaldır (sonraki adımda speaker'ı biz ekleyeceğiz)
        m = re.match(r"^\s*[^:\n]+:\s*(.+)$", p)
        cleaned.append(m.group(1).strip() if m else p)
    return cleaned

# -----------------------------
# Ana fonksiyon
# -----------------------------
# -----------------------------
# Ana fonksiyon
# -----------------------------
def generate_script_with_prompt(paragraphs: Any, prompt: str) -> List[str]:
    base_list = _as_text_list(paragraphs)
    input_text = "\n\n".join(base_list)

    system_msg = (
        "You are a podcast narration writer. "
        "Rewrite the original text based on the given theme or instructions. "
        "Write in a lively narration style with clear, punchy sentences. "
        "Return the result as paragraphs separated by a blank line. "
        "Do NOT add speaker names or dialogue tags."
    )
    full_prompt = (
        f"{system_msg}\n\n"
        f"Original Script:\n{input_text}\n\n"
        f"Rewrite Instruction:\n{prompt}\n\n"
        f"Format: one or two sentences per paragraph, separated by a blank line."
    )

    resp = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=full_prompt
    )
    raw = getattr(resp, "text", "") or ""

    return _postprocess_to_list(raw)
st(text_or_list: Any) -> List[str]:
    """
    Modelden geleni List[str]'e çevirir.
    - Liste dönerse normalize eder
    - String dönerse çift boş satıra göre böler
    - Satır başındaki 'Speaker X:' gibi etiketleri temizler
    """
    if isinstance(text_or_list, list):
        arr = _as_text_list(text_or_list)
    else:
        whole = str(text_or_list or "").strip()
        # paragrafları çift boş satıra göre böl
        arr = [p.strip() for p in re.split(r"\n\s*\n+", whole) if p.strip()]

    cleaned: List[str] = []
    for p in arr:
        # "Speaker 1: ..." öneklerini kaldır (sonraki adımda speaker'ı biz ekleyeceğiz)
        m = re.match(r"^\s*[^:\n]+:\s*(.+)$", p)
        cleaned.append(m.group(1).strip() if m else p)
    return cleaned

# -----------------------------
# Ana fonksiyon
# -----------------------------
def generate_script_with_prompt(paragraphs: Any, prompt: str) -> List[str]:
    """
    paragraphs: List[str] bekler ama dict/list karışık gelse de tolere eder.
    Her zaman List[str] döner (AI sonrası da).
    """
    # 1) Girişi String listesine çevir (dict -> text)
    base_list = _as_text_list(paragraphs)
    input_text = "\n\n".join(base_list)

    # 2) İstem (prompt)
    system_msg = (
        "You are a podcast narration writer. "
        "Rewrite the original text based on the given theme or instructions. "
        "Write in a lively narration style with clear, punchy sentences. "
        "Return the result as paragraphs separated by a blank line. "
        "Do NOT add speaker names or dialogue tags."
    )
    full_prompt = (
        f"{system_msg}\n\n"
        f"Original Script:\n{input_text}\n\n"
        f"Rewrite Instruction:\n{prompt}\n\n"
        f"Format: one or two sentences per paragraph, separated by a blank line."
    )

    # 3) Gemini çağrısı
    # 3) Gemini çağrısı (new google-genai)    
    client = genai.Client(api_key=_read_gemini_key())    
    resp = client.models.generate_content    (
        model="gemini-1.5-pro    ",
        contents=full_prompt
    )
    raw = resp.text


    return _postprocess_to_list(raw)