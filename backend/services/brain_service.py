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
# Extended responses for different scenarios
OFFLINE_RESPONSES = {
    "greeting": [
        "Hi there, friend! How are you feeling today? 🦁",
        "Hey buddy! I'm so happy to see you! 😊",
        "Roar! Hello! What's on your mind? 🌟",
    ],
    "health_question": [
        "That's a great question! Your body is like a super car - it needs the right fuel to run well! 🚗",
        "Let me explain! Think of your blood sugar like a gas tank - we want it just right! ⛽",
        "Good thinking! Your body is amazing and works hard to keep you healthy! 💪",
    ],
    "feeling_bad": [
        "Oh no, I'm sorry you're not feeling great! Let's figure this out together. Can you tell a grown-up? 🤗",
        "I hear you, buddy. When we don't feel good, it's important to rest and tell someone who can help! 🏥",
        "That's tough! Remember, it's okay to not feel okay sometimes. Let's get you some help! 💕",
    ],
    "scared": [
        "It's okay to feel scared sometimes! I'm right here with you. You're braver than you know! 🦁💪",
        "Being scared is normal! Even lions get scared sometimes. But we face it together! 🌟",
        "I understand, friend. Take a deep breath with me - in through your nose, out through your mouth! 😊",
    ],
    "medication": [
        "Medicine time! Think of it like a power-up in a video game - it helps your body fight! 💊⚡",
        "Time for your super charge! Your medicine helps keep your engine running smooth! 🚀",
        "Great job remembering your medicine! That's being a real health hero! 🦸",
    ],
    "food": [
        "Yummy! Food is fuel for your amazing body! What did you eat? 🍎",
        "Eating good food gives your body superpowers! Did you have something healthy? 🥗",
        "Food time is important! Your body needs good fuel to play and learn! 🌟",
    ],
    "school": [
        "School is awesome! What did you learn today? I bet you're super smart! 📚⭐",
        "I hope you had a great day at school! Learning new things is so cool! 🎒",
        "School sounds fun! Remember to drink water and take breaks! 💧",
    ],
    "play": [
        "Playing is so much fun! Just remember to check how you're feeling! 🎮🦁",
        "That sounds awesome! Having fun is good for your heart and your smile! 😄",
        "Woohoo! Playtime is the best! Stay safe and have fun! 🌈",
    ],
    "sleep": [
        "Sleep is super important! Your body does magical healing while you rest! 😴✨",
        "Getting good sleep makes you stronger and happier! Time for bed soon? 🌙",
        "Rest up, buddy! Tomorrow is going to be another great adventure! 💫",
    ],
    "default": [
        "That's interesting! Tell me more about that! 🦁",
        "I'm listening! What else is on your mind? 😊",
        "Roar! Thanks for sharing with me! How does that make you feel? 🌟",
        "You're doing great! I'm here whenever you want to chat! 💪",
        "I love talking with you! What else would you like to share? 🤗",
    ]
}

def get_contextual_response(message: str) -> str:
    """Pick a response based on message context"""
    msg = message.lower()
    
    # Check for greetings
    if any(word in msg for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
        return random.choice(OFFLINE_RESPONSES["greeting"])
    
    # Check for questions about health/diabetes/body
    if any(word in msg for word in ["what is", "how does", "why do", "explain", "tell me about", "what happens"]):
        return random.choice(OFFLINE_RESPONSES["health_question"])
    
    # Check for feeling bad
    if any(word in msg for word in ["hurt", "pain", "bad", "sick", "dizzy", "weak", "shaky", "uncomfortable"]):
        return random.choice(OFFLINE_RESPONSES["feeling_bad"])
    
    # Check for scared/worried
    if any(word in msg for word in ["scared", "afraid", "worried", "nervous", "anxious", "fear"]):
        return random.choice(OFFLINE_RESPONSES["scared"])
    
    # Check for medication
    if any(word in msg for word in ["medicine", "medication", "insulin", "pill", "injection", "shot"]):
        return random.choice(OFFLINE_RESPONSES["medication"])
    
    # Check for food
    if any(word in msg for word in ["eat", "food", "hungry", "snack", "lunch", "dinner", "breakfast", "ate"]):
        return random.choice(OFFLINE_RESPONSES["food"])
    
    # Check for school
    if any(word in msg for word in ["school", "class", "teacher", "homework", "learn", "study"]):
        return random.choice(OFFLINE_RESPONSES["school"])
    
    # Check for play/fun
    if any(word in msg for word in ["play", "game", "fun", "friend", "toy", "outside"]):
        return random.choice(OFFLINE_RESPONSES["play"])
    
    # Check for sleep/tired
    if any(word in msg for word in ["sleep", "tired", "bed", "rest", "nap", "sleepy"]):
        return random.choice(OFFLINE_RESPONSES["sleep"])
    
    # Check for positive feelings
    if any(word in msg for word in ["happy", "good", "great", "awesome", "fine", "okay", "better"]):
        return f"That's wonderful to hear! 🌟 {random.choice(['Keep being amazing!', 'You make me happy too!', 'Roar! That is great news!'])} 😊"
    
    # Check for sad feelings
    if any(word in msg for word in ["sad", "cry", "upset", "lonely", "miss"]):
        return "I'm sorry you're feeling that way. 💙 Remember, it's okay to feel sad sometimes. I'm here for you! 🤗"
    
    # Default response
    return random.choice(OFFLINE_RESPONSES["default"])

async def analyze_intent(message: str, user_age: int):
    # Quick keyword check instead of slow AI
    msg = message.lower()
    if "hurt" in msg or "pain" in msg or "bad" in msg:
        return {"intent": "SYMPTOM", "risk_level": "HIGH"}
    if "help" in msg or "sos" in msg or "emergency" in msg:
        return {"intent": "EMERGENCY", "risk_level": "HIGH"}
    return {"intent": "CHAT", "risk_level": "LOW"}

async def generate_leo_response(user_input, intent_data):
    """
    Generates response using Gemma, but falls back to offline mode if it fails.
    """
    # Safely get mood
    mood = getattr(user_input, 'current_mood', None) or 'unknown'
    
    system_prompt = f"""You are Leo the Lion, a warm and friendly health buddy talking to a {user_input.age}-year-old child with {user_input.condition}.

YOUR PERSONALITY:
- You are caring, patient, and encouraging
- You use simple words a child can understand
- You use fun metaphors: Glucose/Blood Sugar = Fuel, Insulin = Super Charge, Heart = Engine, Pain = Engine trouble
- You're playful but also helpful and informative

CONTEXT:
- Child's current mood: {mood}
- Child's condition: {user_input.condition}

RULES:
- Keep responses to 2-3 short sentences (max 30 words total)
- Be warm, encouraging, and age-appropriate
- If they mention feeling bad/pain, express concern and suggest telling a grown-up
- If they ask about their condition, explain simply using fun metaphors
- Always end with encouragement or a question to keep them engaged
- Add 1-2 relevant emojis

Child said: "{user_input.message}"

Respond naturally as Leo:"""

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

    got_response = False
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, headers=headers, json=payload, timeout=5.0) as response:
                if response.status_code != 200:
                    raise Exception(f"AI Error: {response.status_code}")
                    
                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        data_str = chunk.replace("data: ", "")
                        if data_str == "[DONE]": 
                            break
                        try:
                            data = json.loads(data_str)
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                got_response = True
                                yield f"data: {json.dumps(content)}\n\n"
                        except:
                            pass
    except Exception as e:
        print(f"⚠️ AI Failed ({e}). Using Offline Brain.")
        got_response = False
    
    # 🚨 FALLBACK MODE: If AI fails or returns nothing, use offline brain
    if not got_response:
        print("🦁 Using Offline Brain for response")
        msg_lower = user_input.message.lower()
        
        # Special cases first
        if "sos" in msg_lower or "emergency" in msg_lower:
            backup_reply = "Oh no! Are you okay? I'm here for you! 🆘 Please tell a grown-up right away, they can help! 💕"
        elif "help" in msg_lower:
            backup_reply = "I hear you, friend! 🦁 What do you need help with? If it's serious, let's tell a grown-up together! 💪"
        elif "save" in msg_lower or "die" in msg_lower or "dying" in msg_lower:
            backup_reply = "I can tell you're worried. 💙 You're going to be okay! Let's talk to a grown-up who can help us. You're brave! 🦁"
        else:
            # Use contextual response system
            backup_reply = get_contextual_response(user_input.message)
            
        # Yield the full response for faster display
        yield f"data: {json.dumps(backup_reply)}\n\n"
    
    yield "data: [DONE]\n\n"