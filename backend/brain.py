import requests
import time
import random

# --- CONFIGURATION ---
API_ENDPOINT = "https://gemma-3-27b-3ca9s.paas.ai.telus.com/v1/chat/completions"
API_KEY = "dc8704d41888afb2b889a8ebac81d12f"
MODEL_NAME = "google/gemma-3-27b-it"

SYSTEM_PROMPT = """You are Leo the Lion.
1. MAX 15 WORDS.
2. NO medical words.
3. Be cute and brave.
"""

# BACKUP PHRASES (If Internet Fails)
BACKUP_RESPONSES = {
    "danger": [
        "Roar! My tummy rumbles... I need Magic Fuel fast!",
        "Oh no! My mane is drooping. Let's find a grown-up!",
        "Roar! I feel wobbly. Juice time right now!"
    ],
    "safe": [
        "I feel super strong! Let's build a fort!",
        "My mane is sparkling today! Roar!",
        "You are the bravest friend ever!"
    ]
}

def get_leo_response(rag_instruction, user_message=""):
    lower_rag = rag_instruction.lower()
    
    # Determine mood for prompt
    if "urgent" in lower_rag or "danger" in lower_rag:
        mood = "scared/urgent"
        backup_key = "danger"
    else:
        mood = "happy/playful"
        backup_key = "safe"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"MOOD: {mood}\nINSTRUCTION: {rag_instruction}"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }

    # RETRY LOGIC WITH FALLBACK
    for attempt in range(2): # Try twice
        try:
            response = requests.post(
                API_ENDPOINT,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=payload,
                timeout=4 
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
        except:
            time.sleep(1)
            
    # If API fails, use Backup Brain (Safety Net)
    return random.choice(BACKUP_RESPONSES[backup_key])