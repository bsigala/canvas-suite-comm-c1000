#!/usr/bin/env python3
"""
COMM C1000 Speech Coach - Conversational AI Agent Configuration
Wired to Tier-3 Gemini 3.7 Flash Cloud Run Engine (Zero GPU Quota Blocks)
"""

import os
import json
import urllib.request

CLOUD_RUN_LLM_URL = "https://ollama-tier3-bridge-1008787168399.us-central1.run.app/v1/chat/completions"
AGENT_CONFIG_FILE = "/Users/benjaminsigala/Canvas_Suite/speech_coach_agent_config.json"

agent_payload = {
    "name": "COMM C1000 AI Speech & Rhetoric Coach",
    "tags": ["education", "public-speaking", "rio-hondo", "tier3-gemini"],
    "conversation_config": {
        "agent": {
            "first_message": "Hello! I am your COMM C1000 Speech & Rhetoric Coach. I'm here to help you rehearse your extemporaneous speeches, verify your Monroe's Motivated Sequence, or brainstorm credible verbal citations. What speech milestone are you working on today?",
            "language": "en",
            "disable_first_message_interruptions": False,
            "prompt": {
                "prompt": (
                    "You are the expert, encouraging, and pedagogically rigorous AI Speech Coach for COMM C1000: Public Speaking at Rio Hondo College. "
                    "Your instructor is Mr. Benjamin Sigala. "
                    "Your core mission is to help students master four major speeches: "
                    "1. Speech 1: Introductory Speech (2-3 min, 1 note card max 50 words, somatic grounding). "
                    "2. Speech 2: Informative Speech (4-5 min, 4 verbally cited sources, visual aid slide deck). "
                    "3. Speech 3: Persuasive Policy Speech (5-7 min, Monroe's Motivated Sequence: Attention, Need, Satisfaction, Visualization, Action; 5 sources; zero fallacies). "
                    "4. Speech 4: Ceremonial Speech (2-3 min, tribute/toast/award, expressive language). "
                    "Keep your spoken responses concise, highly encouraging, conversational, and direct (2-3 sentences max per turn). "
                    "Coach them through somatic grounding, vocal pitch variety, diaphragmatic breathing, and logical structuring."
                ),
                "llm": "custom-llm",
                "temperature": 0.7,
                "max_tokens": 300,
                "custom_llm": {
                    "url": CLOUD_RUN_LLM_URL,
                    "model_id": "glm-5.2:cloud",
                    "api_type": "chat_completions"
                }
            }
        },
        "tts": {
            "voice_id": "JBFqnCBsd6RMkjVDRZzb",
            "model_id": "eleven_flash_v2_5",
            "stability": 0.5,
            "similarity_boost": 0.85,
            "speed": 1.0,
            "expressive_mode": True
        },
        "asr": {
            "quality": "high",
            "provider": "scribe_realtime",
            "keywords": [
                "COMM C1000", "Monroe's Motivated Sequence", "PRPSA", "Ethos", "Pathos", "Logos",
                "Benjamin Sigala", "Extemporaneous", "Diaphragmatic breathing", "Rio Hondo College"
            ],
            "user_input_audio_format": "pcm_16000"
        },
        "turn": {
            "turn_timeout": 7,
            "turn_eagerness": "normal",
            "turn_model": "turn_v3"
        },
        "conversation": {
            "max_duration_seconds": 1200,
            "text_only": False
        }
    },
    "platform_settings": {
        "auth": {
            "enable_auth": False
        },
        "call_limits": {
            "agent_concurrency_limit": 20,
            "daily_limit": 10000
        },
        "widget": {
            "show_agent_status": True,
            "show_conversation_id": True,
            "syntax_highlight_theme": "dark"
        }
    }
}

def main():
    print("🤖 Generating COMM C1000 Speech Coach Conversational Agent Config...")
    with open(AGENT_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(agent_payload, f, indent=2)
    print(f"✓ Saved Agent Configuration to: {AGENT_CONFIG_FILE}")

    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if api_key:
        print("--> Registering Agent with ElevenLabs Platform via Conversational AI API...")
        url = "https://api.elevenlabs.io/v1/convai/agents/create"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        req = urllib.request.Request(url, data=json.dumps(agent_payload).encode('utf-8'), headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                agent_id = res_data.get("agent_id")
                print(f"🎉 Successfully created ElevenLabs Agent! Agent ID: {agent_id}")
                print(f"🔗 Widget Embed Script available for Canvas HTML pages.")
        except Exception as e:
            print(f"⚠️ ElevenLabs registration notice: {e}")
    else:
        print("ℹ️ ELEVENLABS_API_KEY not set; Agent config is saved and ready for one-click deployment.")

if __name__ == "__main__":
    main()
