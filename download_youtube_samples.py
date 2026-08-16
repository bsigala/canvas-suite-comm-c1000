#!/usr/bin/env python3
"""
COMM C1000 — Download and Extract Presentation Audio for Voice Cloning
=====================================================================
This script programmatically downloads the user's YouTube presentation links
using yt-dlp, extracts the high-quality vocal audio tracks as WAV files, and
places them in both the Voice_Samples and clean voice_samples directories
for instant voice cloning with ElevenLabs.
"""

import os
import subprocess

BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"
VOICE_DIR = os.path.join(BASE_DIR, "Voice_Samples")
CLEAN_DIR = os.path.join(BASE_DIR, "Audio_Assets", "voice_samples", "clean")

os.makedirs(VOICE_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)

YOUTUBE_LINKS = {
    "presentation_sample_1": "https://youtu.be/thZN20nKSg0",
    "presentation_sample_2": "https://youtu.be/WYFwnffAggM",
    "presentation_sample_3": "https://youtu.be/0-D-hy_uIC8",
    "presentation_sample_4": "https://youtu.be/RPI4gNQnft8"
}

def download_and_extract():
    print("🎙️ Starting Presentation Voice Sample Extraction Pipeline...")
    print(f"   Destination 1: {VOICE_DIR}")
    print(f"   Destination 2: {CLEAN_DIR}\n")

    for name, url in YOUTUBE_LINKS.items():
        print(f"--> Processing {name} ({url})...")
        
        # Output paths for both mp3 and wav formats
        mp3_out = os.path.join(VOICE_DIR, f"{name}.mp3")
        wav_out = os.path.join(CLEAN_DIR, f"{name}.wav")
        
        # Download and extract to MP3 (for Voice_Samples directory)
        print(f"   Downloading and converting to MP3...")
        cmd_mp3 = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", os.path.join(VOICE_DIR, f"{name}.%(ext)s"),
            url
        ]
        
        # Run yt-dlp to extract MP3
        res_mp3 = subprocess.run(cmd_mp3, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if res_mp3.returncode == 0 and os.path.exists(mp3_out):
            print(f"   ✓ MP3 generated: {os.path.basename(mp3_out)}")
        else:
            print(f"   ✗ Failed to generate MP3. Error: {res_mp3.stderr.decode('utf-8', 'replace').strip()}")
            continue

        # Download and extract to WAV (for the clean training directory)
        print(f"   Downloading and converting to WAV...")
        cmd_wav = [
            "yt-dlp",
            "-x",
            "--audio-format", "wav",
            "-o", os.path.join(CLEAN_DIR, f"{name}.%(ext)s"),
            url
        ]
        
        res_wav = subprocess.run(cmd_wav, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if res_wav.returncode == 0 and os.path.exists(wav_out):
            print(f"   ✓ WAV generated: {os.path.basename(wav_out)}")
        else:
            print(f"   ✗ Failed to generate WAV. Error: {res_wav.stderr.decode('utf-8', 'replace').strip()}")

    print("\n🎉 Extraction complete! Clean speech samples populated successfully.")

if __name__ == "__main__":
    download_and_extract()
