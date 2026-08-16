import os
import sys

# Pre-emptively clear conflicting or invalid legacy environment variables (but NOT GOOGLE_GENAI_API_KEY which is the valid one!)
for k in ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GEMINI_KEY_PRIMARY"]:
    if k in os.environ:
        del os.environ[k]

import json
import subprocess
import urllib.request
import urllib.parse
import urllib.error

BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"
AUDIO_DIR = os.path.join(BASE_DIR, "Audio_Assets")
os.makedirs(AUDIO_DIR, exist_ok=True)

# 16 Weekly Title 5 RSI Touchpoint Scripts (single source of truth: course_data.py)
import course_data

weekly_scripts = [
    {
        "week": w["week"],
        "filename": "week_%02d_rsi_touchpoint.mp3" % w["week"],
        "title": w["audio_title"],
        "script": w["audio_script"],
    }
    for w in course_data.WEEKS
]

def load_keys_from_env():
    # Prioritize active environment variables (correct verified keys starting with 'AQ.')
    gemini_key = os.environ.get("GOOGLE_GENAI_API_KEY")
    eleven_key = os.environ.get("ELEVENLABS_API_KEY")
    
    # Try reading from genkit-huggingface-project/.env as fallback only if missing
    if not gemini_key or not eleven_key:
        env_path = "/Users/benjaminsigala/genkit-huggingface-project/.env"
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line_stripped = line.strip()
                    if line_stripped.startswith("GOOGLE_GENAI_API_KEY=") and not gemini_key:
                        gemini_key = line_stripped.split("=", 1)[1].strip().strip('"').strip("'")
                    elif line_stripped.startswith("ELEVENLABS_API_KEY=") and not eleven_key:
                        eleven_key = line_stripped.split("=", 1)[1].strip().strip('"').strip("'")
                        
    return gemini_key, eleven_key

def get_elevenlabs_voice_id():
    # Try cloned_voice_id.json first
    json_path = os.path.join(BASE_DIR, "cloned_voice_id.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                return json.load(f).get("voice_id")
        except:
            pass
    # Try cloned_voice_id.txt
    txt_path = os.path.join(BASE_DIR, "cloned_voice_id.txt")
    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r") as f:
                return f.read().strip()
        except:
            pass
    return None

def synthesize_with_gemini(script, out_path, api_key, voice_name="Zubenelgenubi"):
    try:
        from google import genai
        from google.genai import types
        import base64
        import wave
        
        client = genai.Client(api_key=api_key)
        
        generation_config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=script,
            config=generation_config,
        )
        
        audio_data = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                audio_data = part.inline_data.data
                break
                
        if not audio_data:
            print("   ✗ Gemini API error: No audio data found in response.")
            return False
            
        if isinstance(audio_data, str):
            audio_bytes = base64.b64decode(audio_data)
        else:
            audio_bytes = audio_data
            
        # Write direct PCM data to a WAV container using built-in wave module
        wav_path = out_path.replace(".mp3", ".wav")
        with wave.open(wav_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(24000) # 24kHz
            wav_file.writeframes(audio_bytes)
            
        # Use ffmpeg to convert the generated WAV file to high quality MP3
        import subprocess
        cmd_ffmpeg = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", out_path]
        res = subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Remove intermediate WAV file
        if os.path.exists(wav_path):
            os.remove(wav_path)
            
        return res.returncode == 0 and os.path.exists(out_path)
    except Exception as e:
        print(f"   ✗ Gemini API error during synthesis: {e}")
        return False

def synthesize_with_elevenlabs(script, out_path, api_key, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": script,
        "model_id": "eleven_multilingual_v2", # Flagship lifelike expressive model
        "voice_settings": {
            "stability": 0.50,
            "similarity_boost": 0.92,
            "style": 0.35,
            "use_speaker_boost": True
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            audio_data = resp.read()
            with open(out_path, "wb") as f:
                f.write(audio_data)
            return True
    except Exception as e:
        print(f"   ✗ ElevenLabs API error: {e}")
        return False

def synthesize_with_mac_tts(script, out_path):
    # High quality macOS neural voice rendering via say + afconvert / ffmpeg
    aiff_path = out_path.replace('.mp3', '.aiff')
    voice = "Ava" # Premium macOS system neural voice
    cmd_say = ["say", "-v", voice, script, "-o", aiff_path]
    res = subprocess.run(cmd_say)
    if res.returncode != 0:
        # Fallback to default voice
        subprocess.run(["say", script, "-o", aiff_path])
    
    # Convert AIFF to MP3 or AAC MP4 audio container
    if os.path.exists(aiff_path):
        # Convert to mp3 or compressed m4a
        cmd_convert = ["afconvert", "-f", "m4af", "-d", "aac", aiff_path, out_path.replace('.mp3', '.m4a')]
        subprocess.run(cmd_convert)
        # Rename or keep mp3
        cmd_ffmpeg = ["ffmpeg", "-y", "-i", aiff_path, "-codec:a", "libmp3lame", "-qscale:a", "2", out_path]
        ff_res = subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if ff_res.returncode != 0:
            # If ffmpeg not installed, duplicate m4a to mp3 format
            os.rename(out_path.replace('.mp3', '.m4a'), out_path)
        if os.path.exists(aiff_path):
            os.remove(aiff_path)
        return True
    return False

def main():
    gemini_key, eleven_key = load_keys_from_env()
    voice_id = get_elevenlabs_voice_id()
    
    print(f"🎙️ Starting Batch Audio Synthesis for 16 COMM C1000 Modules...")
    
    for item in weekly_scripts:
        w = item["week"]
        out_file = os.path.join(AUDIO_DIR, item["filename"])
        print(f"--> Synthesizing Week {w:02d}: {item['title']}...")
        
        success = False
        
        # 1. Try ElevenLabs Cloned Voice first if key and voice ID are available
        if eleven_key and voice_id:
            success = synthesize_with_elevenlabs(item["script"], out_file, eleven_key, voice_id)
            
        # 2. Try Gemini Zubenelgenubi voice fallback
        if not success and gemini_key:
            success = synthesize_with_gemini(item["script"], out_file, gemini_key, "Zubenelgenubi")
            
        # 3. Fallback to macOS local say engine
        if not success:
            success = synthesize_with_mac_tts(item["script"], out_file)
            
        if success and os.path.exists(out_file):
            size_kb = os.path.getsize(out_file) / 1024
            print(f"   ✓ Generated: {item['filename']} ({size_kb:.1f} KB)")
        else:
            print(f"   ✗ Failed to generate audio for Week {w}")

    print("\n✅ All 16 Title 5 RSI Audio Assets Generated in:", AUDIO_DIR)

if __name__ == "__main__":
    main()
