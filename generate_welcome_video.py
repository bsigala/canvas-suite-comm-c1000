import os
import sys

# Pre-emptively clear conflicting or invalid legacy environment variables (but NOT GOOGLE_GENAI_API_KEY which is the valid one!)
for k in ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GEMINI_KEY_PRIMARY"]:
    if k in os.environ:
        del os.environ[k]

import wave
import json
import base64
import subprocess
import urllib.request
import urllib.error

BASE_DIR = "/Users/benjaminsigala/Canvas_Suite"

def load_keys_from_env():
    # Prioritize the active environment variable first (verified to contain your valid working API key starting with 'AQ.')
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

def synthesize_with_elevenlabs(text, out_path, api_key, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
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

def synthesize_with_gemini(text, out_path, api_key, voice_name="Zubenelgenubi"):
    try:
        from google import genai
        from google.genai import types
        
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
            contents=text,
            config=generation_config,
        )
        
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        audio_bytes = base64.b64decode(audio_data) if isinstance(audio_data, str) else audio_data
        
        # Save to temporary WAV file
        wav_path = out_path.replace(".mp3", ".wav")
        with wave.open(wav_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(24000) # 24kHz
            wav_file.writeframes(audio_bytes)
            
        # Convert WAV to high-quality MP3 via FFmpeg
        cmd_ffmpeg = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", out_path]
        res = subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(wav_path):
            os.remove(wav_path)
            
        return res.returncode == 0 and os.path.exists(out_path)
    except Exception as e:
        print(f"   ✗ Gemini API error: {e}")
        return False

def main():
    gemini_key, eleven_key = load_keys_from_env()
    
    welcome_speech = (
        "Hello and welcome, everyone, to COMM C1000: Public Speaking. "
        "I am your instructor, Mr. Benjamin Sigala, and I am absolutely thrilled to welcome you to our digital public speaking studio. "
        "Whether you are entering our online classroom environment with butterflies in your stomach or an absolute dread of presenting, "
        "I want to assure you: you are in the exact right place. "
        "This course is a journey of self-discovery, and public speaking is a humbling, grounding, and deeply connecting common thread "
        "that binds us all together. "
        "Over the next 16 weeks, you will have a wide array of opportunities to not only deliver your thoughts but, very critically, "
        "to get to know your classmates, share in their perspectives, and build an authentic, supportive community. "
        "Together, we will explore the power of mindfulness—offering our focus, our diaphragmatic breathing, and our presence to the moment, "
        "learning how to seamlessly transform communication anxiety into compelling, resonant public speaking. "
        "We have an exciting run-down of the syllabus ahead, including hands-on, low-stakes introductory assignments, informative speeches, "
        "persuasive policy briefs using Monroe's Motivated Sequence, and a final capstone speech of ceremonial elegance. "
        "I am honored to walk this path of rhetorical growth and mindfulness with you. "
        "Welcome to our classroom journey, and let's make this an extraordinary and transformative semester!"
    )

    audio_out_path = "/Users/benjaminsigala/Canvas_Suite/welcome_greeting.mp3"
    voice_id = get_elevenlabs_voice_id()
    
    success = False
    
    # Attempt ElevenLabs Cloned Voice first if key and voice ID are available
    if eleven_key and voice_id:
        print(f"🎙️ Synthesizing welcome speech using your ElevenLabs custom cloned voice (ID: {voice_id})...")
        success = synthesize_with_elevenlabs(welcome_speech, audio_out_path, eleven_key, voice_id)
        
    # Fallback to rich, resonant male Gemini voice "Zubenelgenubi"
    if not success:
        if not gemini_key:
            print("Error: Neither GOOGLE_GENAI_API_KEY nor valid ElevenLabs configuration found!")
            exit(1)
        print("🎙️ Synthesizing welcome speech using Gemini 2.5 Flash TTS (Resonant Male Zubenelgenubi voice)...")
        success = synthesize_with_gemini(welcome_speech, audio_out_path, gemini_key, "Zubenelgenubi")

    if not success or not os.path.exists(audio_out_path):
        print("Error: Voiceover synthesis failed.")
        exit(1)

    # Compile into synced MP4 video greeting using profile picture
    image_path = "/Users/benjaminsigala/Downloads/Profile Picture Gemini Generated.jpeg"
    output_video_path = "/Users/benjaminsigala/Canvas_Suite/Individual_Pages/welcome_greeting.mp4"

    if not os.path.exists(image_path):
        print(f"Error: Profile picture not found at {image_path}")
        exit(1)

    print("🎬 Compiling Profile Picture and Voiceover into a synced MP4 video via FFmpeg...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_out_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_video_path
    ]

    res = subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(audio_out_path):
        os.remove(audio_out_path)

    if res.returncode == 0 and os.path.exists(output_video_path):
        size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
        print(f"\n✨ SUCCESS! Synced MP4 Video Greeting beautifully compiled!")
        print(f"   Video Path: {output_video_path}")
        print(f"   Video Size: {size_mb:.2f} MB")
    else:
        print("Error: FFmpeg compilation failed.")
        exit(1)

if __name__ == "__main__":
    main()
