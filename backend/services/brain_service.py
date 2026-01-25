import os
import json
import httpx
import asyncio
import random

# Load Env
from dotenv import load_dotenv
load_dotenv()

# API KEYS
GEMMA_KEY = os.getenv("GEMMA_API_KEY")

# 🦁 LEO'S OFFLINE BRAIN (Fallback)
# If the AI fails, he will say one of these!
OFFLINE_RESPONSES = [
    "Oh no! My tummy feels a bit wobbly too. Let's check your numbers! 🦁",
    "You are so brave! Even superheroes need a break sometimes.",
    "I'm listening! Tell me more about how you feel.",
    "Roar! That sounds tough. But we can handle it together!",
    "Let's take a deep breath together. In... and out..."
]

async def analyze_intent(message: str, user_age: int):
    # Quick keyword check instead of slow AI
    msg = message.lower()
    if "hurt" in msg or "pain" in msg or "bad" in msg:
        return {"intent": "SYMPTOM", "risk_level": "HIGH"}
    return {"intent": "CHAT", "risk_level": "LOW"}

async def generate_leo_response(user_input, intent_data):
    """
    Generates response using Gemma, but falls back to offline mode if it fails.
    """
    system_prompt = f"""
    You are Leo the Lion. You are talking to a 7-year-old.
    Tone: Warm, protective, brave.
    Metaphors: 
    - Glucose -> Fuel
    - Insulin -> Super Charge
    - Stomach Pain -> Engine trouble
    
    User said: "{user_input.message}"
    keep it short (max 2 sentences).
    """

    url = "https://gemma-3-27b-3ca9s.paas.ai.telus.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GEMMA_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "google/gemma-3-27b-it",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input.message}
        ],
        "stream": True,
        "max_tokens": 100
    }

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, headers=headers, json=payload, timeout=5.0) as response:
                if response.status_code != 200:
                    raise Exception("AI Error")
                    
                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        data_str = chunk.replace("data: ", "")
                        if data_str == "[DONE]": break
                        try:
                            data = json.loads(data_str)
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                # Send as JSON string for safety
                                yield f"data: {json.dumps(content)}\n\n"
                        except:
                            pass
    except Exception as e:
        # 🚨 FALLBACK MODE: If AI fails, simulate typing a pre-set response
        print(f"⚠️ AI Failed ({e}). Using Offline Brain.")
        
        # Pick a relevant fallback based on keywords
        backup_reply = random.choice(OFFLINE_RESPONSES)
        if "bad" in user_input.message.lower():
            backup_reply = "Oh no, feeling bad is no fun! Is your engine running low on fuel? 🦁"
            
        # Simulate typing effect
        for word in backup_reply.split(" "):
            yield f"data: {json.dumps(word + ' ')}\n\n"
            await asyncio.sleep(0.1)