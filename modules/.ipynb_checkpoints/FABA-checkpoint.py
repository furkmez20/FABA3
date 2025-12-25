# modules/FABA.py
# --- Podcast üreten çekirdek modül ---

from __future__ import annotations
import os, io, json, hashlib
from typing import List, Dict, Any, Optional

import requests
from pydub import AudioSegment

# Configure pydub to use FFmpeg
AudioSegment.converter = "ffmpeg"
AudioSegment.ffprobe = "ffprobe"

# ------------------------------------------------------------
# 0) API KEY - Güvenli okuma (env ya da .streamlit/secrets.toml)
# ------------------------------------------------------------
def _read_api_key() -> str:
    # Streamlit ile çalışıyorsak secrets'tan da deneyelim
    api = os.getenv("ELEVEN_API_KEY")
    if not api:
        try:
            import streamlit as st  # type: ignore
            api = st.secrets.get("ELEVEN_API_KEY", "")
        except Exception:
            api = ""
    if not api:
        raise RuntimeError("ELEVEN_API_KEY bulunamadı (env veya .streamlit/secrets.toml).")
    return api

ELEVEN_API_KEY = _read_api_key()

# ------------------------------------------------------------
# 1) Public (herkeste çalışan) voice ID'leri
#    Etiketler edit_page.py'dekiyle birebir aynı olmalı
# ------------------------------------------------------------
VOICE_MAP: Dict[str, str] = {
    "Female – Rachel": "21m00Tcm4TlvDq8ikWAM",
    "Female – Bella":  "EXAVITQu4vr4xnSDxMaL",
    "Female – Elli":   "MF3mGyEYCl7XYWbV9V6O",
    "Female – Sarah":  "pMsXgVXv3BLzUgSXRplE",
    "Male – Adam":     "pNInz6obpgDQGcFmaJgB",
    "Male – Antony":   "ErXwobaYiN019PkySvjV",
    "Male – Josh":     "TxGEqnHWrfWFTfGW9XjX",
    "Male – Eric":     "cjVigY5qzO86Huf0OWal",
}

# ------------------------------------------------------------
# 2) Basit disk cache (aynı paragraf + aynı ses = tekrar istek atma)
# ------------------------------------------------------------
CACHE_DIR = "audio_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_name(text: str, voice_id: str) -> str:
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{voice_id}_{h}.mp3")

# ------------------------------------------------------------
# 3) ElevenLabs TTS – Sağlamlaştırılmış istek + doğrulama
# ------------------------------------------------------------
def _tts(text: str, voice_id: str, model_id: Optional[str] = "eleven_turbo_v2") -> AudioSegment:
    """
    Tek bir paragrafı ElevenLabs TTS ile MP3'e çevirir.
    - Audio dönmezse (400/401/limit vb.) exception fırlatır.
    - Başarılı sonuçları cache'ler.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("Boş metin TTS'e gönderilemez.")

    cache_file = _cache_name(text, voice_id)
    if os.path.exists(cache_file):
        try:
            return AudioSegment.from_file(cache_file, format="mp3")
        except Exception as e:
            # Cache bozuksa, yeniden üret
            os.remove(cache_file)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_API_KEY
    }
    payload: Dict[str, Any] = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    if model_id:
        payload["model_id"] = model_id  # public seslerle uyumlu

    r = requests.post(url, json=payload, headers=headers, timeout=60)

    ctype = r.headers.get("content-type", "")
    if r.status_code != 200 or not ctype.startswith("audio/mpeg"):
        # API'nin döndürdüğü gerçek mesajı yüzeye çıkar
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"ElevenLabs TTS failed ({r.status_code}): {detail}")

    try:
        audio = AudioSegment.from_file(io.BytesIO(r.content), format="mp3")
        audio.export(cache_file, format="mp3")
        return audio
    except Exception as e:
        raise RuntimeError(f"FFmpeg error processing audio: {e}. Make sure FFmpeg is installed.")

# ------------------------------------------------------------
# 4) JSON okuma – farklı formatlara tolerans
#    - ["para1", "para2", ...]
#    - [{"text": "...", "speaker": "..."} , ...]
# ------------------------------------------------------------
def _load_segments(json_path: str) -> List[Dict[str, str]]:
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments: List[Dict[str, str]] = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                txt = item.strip()
                if txt:
                    segments.append({"text": txt})
            elif isinstance(item, dict):
                txt = (item.get("text") or "").strip()
                spk = (item.get("speaker") or "").strip()
                if txt:
                    seg = {"text": txt}
                    if spk:
                        seg["speaker"] = spk
                    segments.append(seg)
    if not segments:
        raise ValueError("No segments found in JSON. Script may be empty.")
    return segments

# ------------------------------------------------------------
# 5) Yardımcı – seçilen etiketlerden voice_id listesi üret
# ------------------------------------------------------------
def _resolve_voice_ids(selected_labels: Optional[List[str]]) -> List[str]:
    ids: List[str] = []
    if selected_labels:
        for label in selected_labels:
            vid = VOICE_MAP.get(label)
            if vid:
                ids.append(vid)

    if not ids:
        # Fallback: iki public ses
        ids = [VOICE_MAP["Female – Rachel"], VOICE_MAP["Male – Adam"]]
    return ids

# ------------------------------------------------------------
# 6) ANA FONKSİYON – Podcast üret
# ------------------------------------------------------------
def generate_podcast(
    json_path: str,
    selected_speakers: Optional[List[str]] = None,
    gap_ms: int = 400,
    out_name: str = "podcast_final.mp3",
) -> str:
    """
    json_path: save_script_to_json tarafından üretilen dosya yolu
    selected_speakers: edit_page'de seçilen etiketler (max 4). None ise fallback kullanılır.
    gap_ms: paragraflar arası sessizlik
    out_name: çıktı dosyası adı
    """
    segments = _load_segments(json_path)
    voice_ids = _resolve_voice_ids(selected_speakers)

    final_audio = AudioSegment.silent(duration=1000)  # 1 sn intro
    added = 0

    for i, seg in enumerate(segments):
        text = (seg.get("text") or "").strip()
        if not text:
            continue

        # Eğer JSON'da speaker ismi varsa ve VOICE_MAP'te karşılığı bulunuyorsa onu kullan,
        # yoksa round-robin ile selected_speakers'tan dağıt.
        spk_label = (seg.get("speaker") or "").strip()
        if spk_label and spk_label in VOICE_MAP:
            vid = VOICE_MAP[spk_label]
        else:
            vid = voice_ids[i % len(voice_ids)]

        # ❗ Hata olursa exception fırlasın; 1 sn'lik boş dosya üretmeyelim
        clip = _tts(text, vid, model_id="eleven_turbo_v2")
        final_audio += clip + AudioSegment.silent(duration=gap_ms)
        added += 1

    if added == 0:
        raise RuntimeError("Hiçbir ses segmenti üretilmedi. (Boş script, eşleşmeyen speaker ya da TTS hatası).")

    out_path = os.path.join(os.getcwd(), out_name)
    
    try:
        final_audio.export(out_path, format="mp3")
    except Exception as e:
        raise RuntimeError(f"FFmpeg error exporting final podcast: {e}. Make sure FFmpeg is installed.")
    
    return out_path