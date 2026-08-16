#!/usr/bin/env python3
"""
COMM C1000 — Voice Sample Preparation for ElevenLabs Cloning
=============================================================
Turns the four downloaded instructor recordings into clean, clone-grade
samples: mono, 44.1 kHz, 16-bit WAV, loudness-normalized to -16 LUFS,
with rumble/hiss filtered and leading/trailing silence trimmed.

Each long lecture recording contributes one 60-second window chosen where
the instructor's voice is strong (verified via silencedetect/volumedetect).
"""

import os
import subprocess

BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"
RAW_DIR = os.path.join(BASE_DIR, "Audio_Assets", "voice_samples", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "Audio_Assets", "voice_samples", "clean")
os.makedirs(CLEAN_DIR, exist_ok=True)

# (source_id, start_sec, end_sec, label)
SEGMENTS = [
    ("RPI4gNQnft8", 0.3, 45.5, "welcome_speech"),      # 46s "Welcome to Communication Studies!"
    ("WYFwnffAggM", 5.0, 65.0, "lecture_weekA"),        # strong levels (max -5 dB)
    ("0-D-hy_uIC8", 5.0, 65.0, "lecture_weekB"),        # strong levels (max -5 dB)
    ("thZN20nKSg0", 23.0, 83.0, "lecture_week4"),       # quiet mic; gains normalized below
]


def prepare(src_id, start, end, label):
    src = os.path.join(RAW_DIR, f"{src_id}.mp3")
    dst = os.path.join(CLEAN_DIR, f"{label}.wav")
    if not os.path.exists(src):
        print(f"   ✗ missing source {src}")
        return False

    # mono -> 44.1kHz -> de-rumble/de-hiss -> loudness normalize -> trim edges
    af = (
        "highpass=f=60,"
        "lowpass=f=14000,"
        "loudnorm=I=-16:TP=-1.5:LRA=11,"
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.3,"
        "aresample=44100"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(start), "-to", str(end),
        "-i", src,
        "-af", af,
        "-ac", "1",
        "-c:a", "pcm_s16le",
        dst,
    ]
    res = subprocess.run(cmd)
    if res.returncode == 0 and os.path.exists(dst):
        dur = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", dst], capture_output=True, text=True
        ).stdout.strip()
        kb = os.path.getsize(dst) / 1024
        print(f"   ✓ {label}.wav  ({float(dur):.1f}s, {kb:.0f} KB)")
        return True
    print(f"   ✗ ffmpeg failed for {label}")
    return False


def main():
    print("🎚️ Preparing clone-grade voice samples...")
    ok = 0
    for src_id, start, end, label in SEGMENTS:
        if prepare(src_id, start, end, label):
            ok += 1
    print(f"\n✅ Prepared {ok}/{len(SEGMENTS)} samples in: {CLEAN_DIR}")


if __name__ == "__main__":
    main()
