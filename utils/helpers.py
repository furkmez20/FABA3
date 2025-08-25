# utils/helpers.py
from typing import Any, List
import streamlit as st
import json
import os

def _as_text_list(items: Any) -> List[str]:
    """
    Her türlü girdiyi güvenle List[str]'e normalleştirir.
    Kabul edilen girdiler:
      - str  -> çift boş satıra göre paragraflara böler
      - List[str]
      - List[dict] ({"text": "...", ...}) -> text alanlarını alır
      - karışık tipler -> str(...) ile dönüştürür
    """
    if items is None:
        return []

    # Tek parça string geldiyse paragraflara böl
    if isinstance(items, str):
        parts = [p.strip() for p in items.split("\n\n") if p.strip()]
        return parts

    out: List[str] = []
    for it in items if isinstance(items, (list, tuple)) else [items]:
        if isinstance(it, str):
            s = it.strip()
        elif isinstance(it, dict):
            s = (it.get("text") or "").strip()
        else:
            s = str(it).strip()
        if s:
            out.append(s)
    return out

def reset_script_state(paragraphs: Any) -> None:
    """
    UI state'ini güvenli şekilde günceller (daima List[str] kullanır).
    """
    paras = _as_text_list(paragraphs)
    full_script = "\n\n".join(paras)

    st.session_state.original_paragraphs = paras      # List[str]
    st.session_state.source_text = full_script        # textarea gösterimi
    st.session_state.edited_script = full_script
    st.session_state.text_area_content = full_script

def save_script_to_json(paragraphs: Any, path: str = "edited_script.json") -> str:
    """
    Script'i JSON'a kaydeder. Format: List[str]
    (FABA bu formatı okuyabiliyor. Giriş dict/list/str olabilir; normalize edilir.)
    """
    paras = _as_text_list(paragraphs)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(paras, f, ensure_ascii=False, indent=2)

    abs_path = os.path.abspath(path)
    st.session_state.json_path = abs_path
    return abs_path
