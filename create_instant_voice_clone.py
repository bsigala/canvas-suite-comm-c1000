#!/usr/bin/env python3
"""
Instant Voice Cloning & High-Fidelity Synthesis Pipeline for COMM C1000
Uses Authentic Multi-Sample Speech Recordings of Mr. Benjamin Sigala
"""

import os
import sys
import json
import requests

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_DIR = "/Users/benjaminsigala/Canvas_Suite/Studio_Clean_Samples"

SAMPLE_FILES = [
    os.path.join(VOICE_DIR, "benjamin_sigala_studio_clean_sample_1.mp3"),
    os.path.join(VOICE_DIR, "benjamin_sigala_studio_clean_sample_2.mp3")
]

def clone_voice():
    if not API_KEY:
        print("❌ Error: ELEVENLABS_API_KEY environment variable is required.")
        print("Run with: ELEVENLABS_API_KEY='your-key' python3 create_instant_voice_clone.py")
        sys.exit(1)

    print("🎙️ Initiating Instant Voice Cloning on ElevenLabs with 3 Master Speech Samples...")
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "xi-api-key": API_KEY
    }
    data = {
        "name": "Mr. Benjamin Sigala - Public Speaking Instructor",
        "description": "Authentic, warm, engaging voice of Mr. Benjamin Sigala (COMM C1000 Welcome & Lecture recordings).",
        "labels": json.dumps({"accent": "American", "gender": "male", "use_case": "education"})
    }

    files = []
    for idx, fpath in enumerate(SAMPLE_FILES):
        if os.path.exists(fpath):
            files.append(('files', (f'sample_{idx+1}.mp3', open(fpath, 'rb'), 'audio/mpeg')))
            print(f"   ✓ Attached Sample {idx+1}: {os.path.basename(fpath)}")

    response = requests.post(url, headers=headers, data=data, files=files)
    if response.status_code == 200:
        result = response.json()
        voice_id = result.get("voice_id")
        print(f"\n🎉 SUCCESS! Cloned Voice Created.")
        print(f"🔑 Voice ID: {voice_id}")
        
        # Save voice_id locally
        with open("/Users/benjaminsigala/Canvas_Suite/cloned_voice_id.txt", "w") as f:
            f.write(voice_id)
        return voice_id
    else:
        print(f"❌ ElevenLabs API Error ({response.status_code}): {response.text}")
        sys.exit(1)

def main():
    clone_voice()

if __name__ == "__main__":
    main()
