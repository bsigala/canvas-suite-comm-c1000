#!/usr/bin/env python3
"""
COMM C1000 — ElevenLabs-Inspired Voice Greeting Generator
==========================================================
Synthesizes the instructor welcome greetings using ElevenLabs' "George" voice
(the same voice_id wired into the COMM C1000 AI Speech Coach agent).

Engine priority (first available wins):
  1. ElevenLabs   -> voice "George" (JBFqnCBsd6RMkjVDRZzb), eleven_multilingual_v2
  2. Gemini 2.5   -> "Puck" prebuilt voice (gemini-2.5-flash-preview-tts)
  3. macOS `say`  -> neural "Ava" voice

Outputs, per greeting:
  - Audio_Assets/<slug>.mp3   (Canvas upload)
  - Audio_Assets/<slug>.m4a   (Apple-friendly AAC)
  - Audio_Assets/<slug>.player.html (Canvas HTML-editor audio embed snippet)
"""

import os
import json
import base64
import subprocess
import urllib.request

BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"
AUDIO_DIR = os.path.join(BASE_DIR, "Audio_Assets")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Voice configuration (matches speech_coach_agent_config.json)
# ---------------------------------------------------------------------------
ELEVEN_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"   # "George" — male, narrative
ELEVEN_MODEL_ID = "eleven_multilingual_v2"
GEMINI_VOICE_NAME = "Puck"
GEMINI_MODEL = "gemini-2.5-flash-preview-tts"
MAC_VOICE = "Ava"

# ---------------------------------------------------------------------------
# Greeting scripts
# ---------------------------------------------------------------------------
GREETINGS = [
    {
        "slug": "course_welcome_greeting",
        "label": "Full Course Welcome (Hero)",
        "script": (
            "Hello, and welcome to COMM C1000: Public Speaking. "
            "I'm your instructor, Mr. Benjamin Sigala, and I am genuinely thrilled to have you in our digital public speaking studio. "
            "If you arrived here with butterflies in your stomach, or even a deep dread of presenting, take a breath: you are in exactly the right place. "
            "Over the next sixteen weeks we're going to transform that apprehension into a calm, grounded, and confident voice. "
            "This is a Zero Textbook Cost course, which means every reading lives online and is completely free — no textbook purchases, ever. "
            "We'll begin by measuring your public speaking anxiety with the PRPSA, then build somatic control through diaphragmatic breathing, "
            "and move step by step through four major speeches: an introductory speech, a research-backed informative speech, "
            "a persuasive policy speech built on Monroe's Motivated Sequence, and a ceremonial speech to close the semester. "
            "Along the way you'll learn to cite sources out loud, design visual aids that don't overload the brain, and give peer feedback that actually helps. "
            "My promise to you is regular video touchpoints every single week, fast responses to your messages, and a classroom built on respect, curiosity, and courage. "
            "Welcome to our classroom journey. Let's make this an extraordinary and transformative semester."
        ),
    },
    {
        "slug": "opening_announcement_greeting",
        "label": "Opening Announcement (Short Teaser)",
        "script": (
            "Hey there, COMM C1000 scholars — Mr. Sigala here with a quick hello. "
            "The course is officially open, and your very first move is simple: read the syllabus, take the PRPSA anxiety baseline, "
            "and complete the orientation scavenger hunt. Everything is free, everything is in Canvas, and I'll be right here with you every step of the way. "
            "Let's get started!"
        ),
    },
]


# ---------------------------------------------------------------------------
# API key loaders (keys are never printed)
# ---------------------------------------------------------------------------
def load_eleven_key():
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if api_key:
        return api_key
    env_path = "/Users/benjaminsigala/genkit-huggingface-project/.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.strip().startswith("ELEVENLABS_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def load_gemini_key():
    api_key = os.environ.get("GOOGLE_GENAI_API_KEY")
    if api_key:
        return api_key
    env_path = "/Users/benjaminsigala/genkit-huggingface-project/.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.strip().startswith("GOOGLE_GENAI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


# ---------------------------------------------------------------------------
# Synthesis engines
# ---------------------------------------------------------------------------
def synthesize_elevenlabs(script, mp3_path):
    """POST /v1/text-to-speech/{voice_id} via stdlib urllib (no SDK dependency)."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    payload = json.dumps({
        "text": script,
        "model_id": ELEVEN_MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.85,
            "style": 0.35,
            "use_speaker_boost": True,
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "xi-api-key": load_eleven_key(),
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        audio = resp.read()
    with open(mp3_path, "wb") as f:
        f.write(audio)
    return True


def synthesize_gemini(script, mp3_path):
    from google import genai
    from google.genai import types
    import wave

    client = genai.Client(api_key=load_gemini_key())
    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=GEMINI_VOICE_NAME
                )
            )
        ),
    )
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=script,
        config=config,
    )

    audio_data = None
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            audio_data = part.inline_data.data
            break
    if not audio_data:
        return False

    audio_bytes = base64.b64decode(audio_data) if isinstance(audio_data, str) else audio_data

    wav_path = mp3_path.replace(".mp3", ".wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)      # 16-bit
        wf.setframerate(24000)  # 24 kHz
        wf.writeframes(audio_bytes)

    res = subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if os.path.exists(wav_path):
        os.remove(wav_path)
    if res.returncode == 0 and os.path.exists(mp3_path):
        return True
    return False


def synthesize_mac(script, mp3_path):
    aiff_path = mp3_path.replace(".mp3", ".aiff")
    res = subprocess.run(["say", "-v", MAC_VOICE, script, "-o", aiff_path])
    if res.returncode != 0:
        subprocess.run(["say", script, "-o", aiff_path])
    if not os.path.exists(aiff_path):
        return False
    ff = subprocess.run(
        ["ffmpeg", "-y", "-i", aiff_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if os.path.exists(aiff_path):
        os.remove(aiff_path)
    return ff.returncode == 0 and os.path.exists(mp3_path)


def to_m4a(mp3_path):
    m4a_path = mp3_path.replace(".mp3", ".m4a")
    res = subprocess.run(
        ["ffmpeg", "-y", "-i", mp3_path, "-c:a", "aac", "-b:a", "192k", m4a_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return m4a_path if res.returncode == 0 and os.path.exists(m4a_path) else None


def write_player_html(slug, label, mp3_filename, m4a_filename):
    """Canvas-compatible HTML5 audio player embed (paste into RCE HTML editor)."""
    html = f"""<!-- {label} — paste this into the Canvas Rich Content Editor's HTML view -->
<div style="max-width:720px; margin:0 auto; padding:18px 20px; background:#080C14; border:1px solid rgba(217,119,6,.3); border-radius:12px; font-family:Inter,-apple-system,sans-serif;">
  <p style="margin:0 0 10px 0; color:#FBBF24; font-weight:600; font-size:0.9rem; letter-spacing:.04em;">🎙️ {label} — Mr. Benjamin Sigala</p>
  <audio controls preload="metadata" style="width:100%;" aria-label="{label}">
    <source src="{m4a_filename}" type="audio/mp4">
    <source src="{mp3_filename}" type="audio/mpeg">
    Your browser does not support the audio element.
  </audio>
  <p style="margin:10px 0 0 0; color:#94A3B8; font-size:0.75rem;">Upload the matching MP3/M4A file to Canvas Files, then update the <code>src</code> above to the file's URL.</p>
</div>
"""
    path = os.path.join(AUDIO_DIR, f"{slug}.player.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


# ---------------------------------------------------------------------------
def main():
    eleven_key = load_eleven_key()
    gemini_key = load_gemini_key()
    engine = "ElevenLabs (George)" if eleven_key else ("Gemini 2.5 TTS (Puck)" if gemini_key else "macOS say (Ava)")

    print("🎙️ COMM C1000 — Voice Greeting Generator")
    print(f"   Engine selected: {engine}")
    if not eleven_key:
        print("   ℹ️  ELEVENLABS_API_KEY not set → using fallback. Add the key and re-run for the true ElevenLabs 'George' voice.")

    results = []
    for g in GREETINGS:
        slug = g["slug"]
        mp3_path = os.path.join(AUDIO_DIR, f"{slug}.mp3")
        print(f"\n--> Synthesizing: {g['label']}")

        success = False
        if eleven_key:
            try:
                success = synthesize_elevenlabs(g["script"], mp3_path)
            except Exception as e:
                print(f"   ✗ ElevenLabs failed ({e}); falling back.")
        if not success and gemini_key:
            try:
                success = synthesize_gemini(g["script"], mp3_path)
            except Exception as e:
                print(f"   ✗ Gemini failed ({e}); falling back.")
        if not success:
            success = synthesize_mac(g["script"], mp3_path)

        if not success or not os.path.exists(mp3_path):
            print(f"   ✗ All engines failed for {slug}")
            continue

        m4a_path = to_m4a(mp3_path)
        player_path = write_player_html(
            slug, g["label"],
            f"{slug}.mp3",
            f"{slug}.m4a" if m4a_path else f"{slug}.mp3",
        )

        size_kb = os.path.getsize(mp3_path) / 1024
        print(f"   ✓ {slug}.mp3 ({size_kb:.1f} KB)")
        if m4a_path:
            print(f"   ✓ {slug}.m4a ({os.path.getsize(m4a_path)/1024:.1f} KB)")
        print(f"   ✓ {os.path.basename(player_path)}")
        results.append(slug)

    print("\n" + "=" * 60)
    print(f"✅ Generated {len(results)}/{len(GREETINGS)} greetings in: {AUDIO_DIR}")
    if not eleven_key:
        print("\nTo re-render with ElevenLabs' George voice:")
        print("  export ELEVENLABS_API_KEY=your_key_here")
        print("  python3 /Users/benjaminsigala/Canvas_Suite/generate_elevenlabs_greeting.py")


if __name__ == "__main__":
    main()
