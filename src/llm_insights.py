"""
LLM advisory generator with OpenAI integration and cached fallback.
"""
import os
import json
from pathlib import Path

try:
    # New OpenAI client (>=1.x)
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore

try:
    # Legacy OpenAI client (<1.0)
    import openai  # type: ignore
except Exception:
    openai = None  # type: ignore

CACHE_PATH = Path("data/cached_advisories.json")
LOCAL_CACHE = {}
OPENAI_DISABLED = False  # set to True if we detect quota or other hard failure
if CACHE_PATH.exists():
    with open(CACHE_PATH) as f:
        LOCAL_CACHE = json.load(f)

def generate_advisory(severity, top_drivers, role="Local Authority"):
    """
    If OPENAI_API_KEY present, use OpenAI; otherwise return cached advisory.
    """
    global OPENAI_DISABLED

    key = os.getenv("OPENAI_API_KEY")
    prompt = f"Provide a concise advisory for severity={severity}. Top drivers: {', '.join(top_drivers)}. Role: {role}."

    # If we've previously detected a hard error (e.g. insufficient_quota),
    # skip calling the API again and immediately return cached/fallback text.
    if OPENAI_DISABLED:
        return LOCAL_CACHE.get(severity, f"{severity} advisory: follow local instructions.")

    if key and (OpenAI or openai):
        try:
            text = None

            # Prefer the new client if available
            if OpenAI is not None:
                client = OpenAI(api_key=key)
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                )
                text = resp.choices[0].message.content.strip()

            # Fallback to legacy client, if installed
            elif openai is not None:
                openai.api_key = key
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                )
                text = resp["choices"][0]["message"]["content"].strip()

            if text:
                # cache it
                LOCAL_CACHE[severity] = text
                with open(CACHE_PATH, "w") as f:
                    json.dump(LOCAL_CACHE, f, indent=2)
                return text
        except Exception as e:
            # If quota is exceeded or another hard error occurs, disable
            # further OpenAI usage for this process to avoid log spam.
            msg = str(e)
            if "insufficient_quota" in msg or "quota" in msg:
                OPENAI_DISABLED = True
            print("OpenAI call failed:", e)
    # fallback
    return LOCAL_CACHE.get(severity, f"{severity} advisory: follow local instructions.")