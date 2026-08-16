#!/usr/bin/env python3
"""
COMM C1000 — ElevenLabs Voice Cloning + Greeting Regeneration
==============================================================
1. Uploads the prepared clean samples to ElevenLabs Instant Voice Cloning
   (POST /v1/voices/add) and returns a custom voice_id.
2. Caches that voice_id in cloned_voice_id.json so re-runs skip re-cloning.
3. Regenerates the 2 instructor greetings AND all 16 weekly RSI touchpoints
   in the CLONED voice. A render manifest makes re-runs resume/skip safely.

Flags:  --force   re-render everything (ignore the completed manifest)

Requires:  export ELEVENLABS_API_KEY=sk_...
Run:       python3 clone_voice_and_regenerate.py
"""

import os
import json
import subprocess
import urllib.request
import urllib.error
import uuid

BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"
CLEAN_DIR = os.path.join(BASE_DIR, "Audio_Assets", "voice_samples", "clean")
AUDIO_DIR = os.path.join(BASE_DIR, "Audio_Assets")
VOICE_ID_FILE = os.path.join(BASE_DIR, "cloned_voice_id.json")

VOICE_NAME = "Benjamin Sigala — COMM C1000 Instructor"
MODEL_ID = "eleven_multilingual_v2"
MANIFEST_FILE = os.path.join(BASE_DIR, "voice_clone_manifest.json")

# Reuse the greeting + weekly scripts defined by the existing generators.
import sys
sys.path.insert(0, BASE_DIR)
from generate_elevenlabs_greeting import GREETINGS  # noqa: E402
from generate_course_audio import weekly_scripts   # noqa: E402


# ---------------------------------------------------------------------------
# Multipart builder (stdlib only — no `requests`, no SDK)
# ---------------------------------------------------------------------------
def build_multipart(fields, files):
    boundary = "----FreebuffBoundary" + uuid.uuid4().hex
    body = b""
    for name, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += f"{value}\r\n".encode()
    for field_name, path in files:
        fname = os.path.basename(path)
        with open(path, "rb") as f:
            data = f.read()
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{field_name}"; filename="{fname}"\r\n'.encode()
        body += b"Content-Type: audio/wav\r\n\r\n"
        body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return body, boundary


def http_json(url, headers, data=None):
    req = urllib.request.Request(url, data=data, headers=headers, method="GET" if data is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        return e.code, {"error": body}
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason)}


# ---------------------------------------------------------------------------
def clone_voice(api_key):
    samples = sorted(
        os.path.join(CLEAN_DIR, f)
        for f in os.listdir(CLEAN_DIR)
        if f.lower().endswith(".wav")
    )
    if not samples:
        print("✗ No prepared samples found. Run prepare_voice_samples.py first.")
        return None

    print(f"🧬 Cloning voice from {len(samples)} samples ({sum(os.path.getsize(s)/1024/1024 for s in samples):.1f} MB)...")
    fields = {
        "name": VOICE_NAME,
        "description": "Benjamin Sigala — instructor voice for COMM C1000: Public Speaking (Rio Hondo College).",
        "labels": json.dumps({"accent": "american", "use_case": "education", "gender": "male"}),
    }
    body, boundary = build_multipart(fields, [("files", s) for s in samples])
    headers = {
        "xi-api-key": api_key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    status, data = http_json("https://api.elevenlabs.io/v1/voices/add", headers, data=body)
    if status != 200 or "voice_id" not in data:
        print(f"   ✗ Voice cloning failed (HTTP {status}):")
        print(f"     {data.get('error', data)}")
        return None

    voice_id = data["voice_id"]
    with open(VOICE_ID_FILE, "w", encoding="utf-8") as f:
        json.dump({"voice_id": voice_id, "name": VOICE_NAME}, f, indent=2)
    print(f"   ✓ Cloned! voice_id = {voice_id}")
    print(f"   ✓ Cached to {os.path.basename(VOICE_ID_FILE)}")
    return voice_id


# ---------------------------------------------------------------------------
def synthesize(api_key, voice_id, script, mp3_path):
    payload = json.dumps({
        "text": script,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.85,
            "style": 0.2,
            "use_speaker_boost": True,
        },
    }).encode("utf-8")
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=payload, headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            audio = resp.read()
    except urllib.error.HTTPError as e:
        print(f"   ✗ TTS failed (HTTP {e.code}): {e.read().decode('utf-8', 'replace')[:300]}")
        return False
    with open(mp3_path, "wb") as f:
        f.write(audio)
    return True


def to_m4a(mp3_path):
    m4a_path = mp3_path.replace(".mp3", ".m4a")
    res = subprocess.run(
        ["ffmpeg", "-y", "-i", mp3_path, "-c:a", "aac", "-b:a", "192k", m4a_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return m4a_path if res.returncode == 0 and os.path.exists(m4a_path) else None


def write_player_html(slug, label, mp3_filename, m4a_filename):
    html = f"""<!-- {label} — CLONED instructor voice. Paste into Canvas RCE HTML editor -->
<div style="max-width:720px; margin:0 auto; padding:18px 20px; background:#080C14; border:1px solid rgba(217,119,6,.3); border-radius:12px; font-family:Inter,-apple-system,sans-serif;">
  <p style="margin:0 0 10px 0; color:#FBBF24; font-weight:600; font-size:0.9rem; letter-spacing:.04em;">🎙️ {label} — Mr. Benjamin Sigala (cloned voice)</p>
  <audio controls preload="metadata" style="width:100%;" aria-label="{label}">
    <source src="{m4a_filename}" type="audio/mp4">
    <source src="{mp3_filename}" type="audio/mpeg">
  </audio>
  <p style="margin:10px 0 0 0; color:#94A3B8; font-size:0.75rem;">Upload the MP3/M4A to Canvas Files, then point the <code>src</code> at the file URL.</p>
</div>
"""
    with open(os.path.join(AUDIO_DIR, f"{slug}_cloned.player.html"), "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------------------------
def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"voice_id": None, "rendered": []}


def save_manifest(manifest):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def render_one(api_key, voice_id, script, mp3_path, make_m4a, force, manifest):
    """Render one script; skip if already rendered for this voice (unless --force)."""
    key = os.path.basename(mp3_path)
    if not force and key in manifest.get("rendered", []) and os.path.exists(mp3_path):
        return "skip"

    if not synthesize(api_key, voice_id, script, mp3_path):
        return "fail"

    if make_m4a:
        to_m4a(mp3_path)

    manifest.setdefault("rendered", []).append(key)
    save_manifest(manifest)
    return "ok"


# ---------------------------------------------------------------------------
def load_api_key():
    """Read ELEVENLABS_API_KEY from env, then from the project .env file."""
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


def main():
    api_key = load_api_key()
    if not api_key:
        print("✗ ELEVENLABS_API_KEY is not set.")
        print("  Add this line to ~/genkit-huggingface-project/.env (next to GOOGLE_GENAI_API_KEY):")
        print("    ELEVENLABS_API_KEY=sk_...")
        print("  Then re-run:")
        print("    python3 /Users/benjaminsigala/Canvas_Suite/clone_voice_and_regenerate.py")
        return 1

    # Reuse cached voice_id if we've already cloned once.
    voice_id = None
    if os.path.exists(VOICE_ID_FILE):
        with open(VOICE_ID_FILE, "r", encoding="utf-8") as f:
            voice_id = json.load(f).get("voice_id")
        print(f"♻️  Reusing cached cloned voice_id: {voice_id}")

    if not voice_id:
        voice_id = clone_voice(api_key)
        if not voice_id:
            return 1

    force = "--force" in sys.argv
    manifest = load_manifest()
    manifest["voice_id"] = voice_id
    save_manifest(manifest)

    ok = skip = fail = 0

    print("\n🎙️ Regenerating greetings in your cloned voice...")
    for g in GREETINGS:
        slug = g["slug"]
        mp3_path = os.path.join(AUDIO_DIR, f"{slug}_cloned.mp3")
        status = render_one(api_key, voice_id, g["script"], mp3_path, True, force, manifest)
        if status == "skip":
            print(f"   ⏭  {g['label']} (already rendered — skipping)"); skip += 1
        elif status == "ok":
            m4a_path = mp3_path.replace(".mp3", ".m4a")
            write_player_html(slug, g["label"], f"{slug}_cloned.mp3", f"{slug}_cloned.m4a" if os.path.exists(m4a_path) else f"{slug}_cloned.mp3")
            print(f"   ✓ {slug}_cloned.mp3 ({os.path.getsize(mp3_path)/1024:.1f} KB)" + (" + .m4a" if os.path.exists(m4a_path) else "")); ok += 1
        else:
            print(f"   ✗ failed: {g['label']}"); fail += 1

    print("\n🎙️ Regenerating 16 weekly RSI touchpoints in your cloned voice...")
    for w in weekly_scripts:
        mp3_path = os.path.join(AUDIO_DIR, w["filename"])
        status = render_one(api_key, voice_id, w["script"], mp3_path, True, force, manifest)
        label = f"Week {w['week']:02d}: {w['title']}"
        if status == "skip":
            print(f"   ⏭  {label} (already rendered — skipping)"); skip += 1
        elif status == "ok":
            m4a_path = mp3_path.replace(".mp3", ".m4a")
            print(f"   ✓ {w['filename']} ({os.path.getsize(mp3_path)/1024:.1f} KB)" + (" + .m4a" if os.path.exists(m4a_path) else "")); ok += 1
        else:
            print(f"   ✗ failed: {label}"); fail += 1

    print(f"\n✅ Done: {ok} rendered, {skip} skipped, {fail} failed → {AUDIO_DIR}")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
