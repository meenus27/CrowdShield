"""
Text-to-speech generator with multilingual support.
"""

import os
from pathlib import Path
from gtts import gTTS

def generate_tts(text, lang="en"):
    """
    Generate MP3 advisory in selected language.
    """
    alerts_dir = Path("data/alerts")
    alerts_dir.mkdir(parents=True, exist_ok=True)
    fname = alerts_dir / f"tts_{lang}.mp3"
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(fname)
        return str(fname)
    except Exception as e:
        # Fallback: save plain text file
        fname = alerts_dir / f"tts_{lang}.txt"
        with open(fname,"w",encoding="utf-8") as f:
            f.write(text + f"\n(TTS unavailable: {e})")
        return str(fname)
