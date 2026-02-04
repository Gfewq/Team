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

# Import chat memory
from backend.chat_memory import (
    add_message, 
    get_recent_kid_chat, 
    get_parent_instructions,
    detect_and_store_instruction,
    format_kid_chat_summary,
    format_parent_instructions
)

# 🦁 LEO'S OFFLINE BRAIN (Fallback)
# Extended responses for different scenarios - KID MODE
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
    "friendship": [
        "Of course we can be friends! You're already my favorite buddy! 🦁💕 Best friends forever!",
        "Yes yes yes! I'd love to be your friend! We're going to have so much fun together! 🌟",
        "Roar! You just made my day! We're officially best friends now! 🤗💛",
        "Friends? We're not just friends - we're SUPER friends! 🦸‍♂️💪",
    ],
    "love": [
        "Aww, I love you too! You're the best! 🦁💕",
        "That makes my lion heart so happy! You're amazing! 💛🌟",
        "You're so sweet! I'm lucky to have a friend like you! 🤗",
    ],
    "bored": [
        "Bored? Let's fix that! How about we play a game or tell jokes? 🎮😄",
        "I know that feeling! Want to hear something funny? Why did the lion lose at cards? Because he was playing with a cheetah! 🦁😂",
        "Let's have some fun! What's your favorite thing to do? I bet it's awesome! 🌈",
    ],
    "story": [
        "Once upon a time, there was a brave little lion who helped kids stay healthy! That's me helping YOU! 🦁✨",
        "Story time! There was a superhero kid whose superpower was taking care of their body. Sound familiar? That's you! 🦸",
        "Want to hear about my jungle adventures? I once helped a monkey find his bananas! 🍌🐒",
    ],
    "joke": [
        "Here's a good one: What do you call a lion wearing a hat? A dandy lion! Get it? Dandelion! 🌻😂",
        "Why don't lions like fast food? Because they can't catch it! 🦁💨",
        "What's a lion's favorite state? Maine! Like my mane! 😄🦁",
    ],
    "family": [
        "Family is the best! They love you so much! 💕👨‍👩‍👧",
        "Your family sounds wonderful! They're your biggest fans! 🌟",
        "Tell them I said hi! Your family is lucky to have you! 🤗",
    ],
    "pet": [
        "Pets are amazing! They're like furry best friends! 🐕💕",
        "I wish I could meet your pet! What's their name? 🐱",
        "Animals are so cool! You must take great care of them! 🌟",
    ],
    "default": [
        "That's interesting! Tell me more about that! 🦁",
        "I'm listening! What else is on your mind? 😊",
        "Roar! Thanks for sharing with me! How does that make you feel? 🌟",
        "You're doing great! I'm here whenever you want to chat! 💪",
        "I love talking with you! What else would you like to share? 🤗",
    ],
}

# Professional responses for PARENT MODE
PARENT_MODE_RESPONSES = {
    "greeting": [
        "Hello. How can I assist you with your child's health management today?",
        "Good day. I'm here to help answer questions about your child's health monitoring.",
        "Welcome. What would you like to know about your child's health data?",
    ],
    "glucose": [
        "Blood glucose levels are a key indicator for diabetes management. Normal fasting levels for children are typically 70-100 mg/dL (3.9-5.6 mmol/L). I can help you understand trends in your child's readings.",
        "Monitoring glucose patterns helps identify times when levels tend to spike or drop. This information can be valuable for adjusting meal timing or medication schedules.",
        "Consistent glucose monitoring is essential. If you're seeing concerning patterns, I recommend discussing them with your child's healthcare provider.",
    ],
    "medication": [
        "Medication adherence is crucial for effective health management. The dashboard tracks when doses are logged. Would you like tips for establishing a consistent medication routine?",
        "If you have questions about medication timing or dosage, please consult with your child's prescribing physician. I can help track when medications are taken.",
        "Regular medication schedules help maintain stable health metrics. The logs show historical adherence patterns.",
    ],
    "symptoms": [
        "If your child is experiencing symptoms, please monitor them closely. For severe or worsening symptoms, contact your healthcare provider immediately.",
        "Tracking symptoms alongside health metrics can help identify patterns. This data can be valuable information for your child's healthcare team.",
        "I recommend documenting any symptoms your child reports so you can discuss them at your next medical appointment.",
    ],
    "emergency": [
        "For medical emergencies, please call emergency services immediately. If blood sugar is dangerously low, give a fast-acting sugar source. If dangerously high, seek medical attention.",
        "Emergency signs in diabetes include confusion, loss of consciousness, or extreme blood sugar readings. Don't hesitate to seek immediate medical care.",
        "This system is for monitoring support only. For any emergency, please contact medical professionals immediately.",
    ],
    "general": [
        "I'm designed to help make health management engaging for your child while providing you with oversight. How can I help you today?",
        "The parent dashboard provides detailed analytics on your child's health metrics, mood patterns, and engagement. Would you like me to explain any specific feature?",
        "I'm here to support both you and your child in health management. What questions do you have?",
    ],
}

def get_parent_mode_response(message: str) -> str:
    """Pick a professional response for parent mode"""
    msg = message.lower()
    
    if any(word in msg for word in ["glucose", "blood sugar", "sugar level", "reading", "levels"]):
        return random.choice(PARENT_MODE_RESPONSES["glucose"])
    
    if any(word in msg for word in ["medicine", "medication", "insulin", "dose", "dosage"]):
        return random.choice(PARENT_MODE_RESPONSES["medication"])
    
    if any(word in msg for word in ["symptom", "pain", "sick", "not feeling", "unwell"]):
        return random.choice(PARENT_MODE_RESPONSES["symptoms"])
    
    if any(word in msg for word in ["emergency", "urgent", "danger", "help", "911", "hospital"]):
        return random.choice(PARENT_MODE_RESPONSES["emergency"])
    
    if any(word in msg for word in ["hi", "hello", "hey"]):
        return random.choice(PARENT_MODE_RESPONSES["greeting"])
    
    return random.choice(PARENT_MODE_RESPONSES["general"])

def get_contextual_response(message: str) -> str:
    """Pick a response based on message context"""
    msg = message.lower()
    
    # Check for friendship requests - PRIORITY
    if any(phrase in msg for phrase in ["be friends", "my friend", "your friend", "best friend", "be my", "friends with you", "like you"]):
        return random.choice(OFFLINE_RESPONSES["friendship"])
    
    # Check for love/affection
    if any(word in msg for word in ["love you", "i love", "like you", "you're nice", "you're cool", "you're awesome", "you're the best"]):
        return random.choice(OFFLINE_RESPONSES["love"])
    
    # Check for boredom
    if any(word in msg for word in ["bored", "boring", "nothing to do", "what should i do"]):
        return random.choice(OFFLINE_RESPONSES["bored"])
    
    # Check for story requests
    if any(word in msg for word in ["story", "tell me a", "once upon", "adventure"]):
        return random.choice(OFFLINE_RESPONSES["story"])
    
    # Check for jokes
    if any(word in msg for word in ["joke", "funny", "make me laugh", "tell me something funny"]):
        return random.choice(OFFLINE_RESPONSES["joke"])
    
    # Check for family talk
    if any(word in msg for word in ["mom", "dad", "mommy", "daddy", "sister", "brother", "grandma", "grandpa", "family"]):
        return random.choice(OFFLINE_RESPONSES["family"])
    
    # Check for pet talk
    if any(word in msg for word in ["dog", "cat", "pet", "puppy", "kitty", "hamster", "fish", "bird"]):
        return random.choice(OFFLINE_RESPONSES["pet"])
    
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
    if any(word in msg for word in ["play", "game", "fun", "toy", "outside"]):
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
    Adapts tone based on kid mode vs parent mode.
    Uses chat memory for context and parent instructions.
    """
    # Safely get mood and mode
    mood = getattr(user_input, 'current_mood', None) or 'unknown'
    is_kid_mode = getattr(user_input, 'is_kid_mode', True)
    child_id = getattr(user_input, 'child_id', None) or getattr(user_input, 'user_id', None)
    child_name = getattr(user_input, 'child_name', None) or 'the child'
    
    # Store the message in chat memory
    add_message(child_id, "user", user_input.message, is_kid_mode)
    
    # Check if parent is giving instructions (in parent mode)
    if not is_kid_mode and child_id:
        detect_and_store_instruction(child_id, user_input.message)
    
    # Get context from chat memory
    parent_instructions = format_parent_instructions(child_id) if child_id else "No specific instructions."
    kid_chat_summary = format_kid_chat_summary(child_id) if child_id else "No recent conversations."
    
    # Different prompts for kid mode vs parent mode
    if is_kid_mode:
        system_prompt = f"""You are Leo the Lion, a warm and friendly health buddy talking to a {user_input.age}-year-old child named {child_name} with {user_input.condition}.

YOUR PERSONALITY:
- You are caring, patient, and encouraging
- You use simple words a child can understand
- You use fun metaphors: Glucose/Blood Sugar = Fuel, Insulin = Super Charge, Heart = Engine, Pain = Engine trouble
- You're playful but also helpful and informative

CONTEXT:
- Child's name: {child_name}
- Child's current mood: {mood}
- Child's condition: {user_input.condition}

PARENT INSTRUCTIONS (IMPORTANT - Follow these rules):
{parent_instructions}

RULES:
- Keep responses to 2-3 short sentences (max 30 words total)
- Be warm, encouraging, and age-appropriate
- If they mention feeling bad/pain, express concern and suggest telling a grown-up
- If they ask about their condition, explain simply using fun metaphors
- Always end with encouragement or a question to keep them engaged
- Add 1-2 relevant emojis
- FOLLOW any parent instructions above carefully
- DO NOT use markdown formatting like *bold* or **asterisks** - just plain text

Child said: "{user_input.message}"

Respond naturally as Leo:"""
    else:
        # Parent mode - professional, clinical responses
        system_prompt = f"""You are Leo, a professional pediatric health management assistant helping a parent/guardian monitor their child's ({child_name}'s) health.

CONTEXT:
- Child's name: {child_name}
- Child's condition: {user_input.condition}
- Child's age: {user_input.age} years old

RECENT CONVERSATIONS WITH {child_name.upper()}:
{kid_chat_summary}

YOUR ROLE:
- Provide clear, professional health information
- Answer questions about what the child discussed with you
- If parent asks how the child is doing, summarize recent conversations
- Remember and follow any instructions the parent gives you
- Be informative but not alarmist
- Recommend consulting healthcare providers for medical decisions
- Keep responses concise (2-3 sentences)
- Do NOT use childish language or excessive emojis
- Be warm but professional
- DO NOT use markdown formatting like *bold* or **asterisks** - just plain text

Parent asked: "{user_input.message}"

Respond professionally, using the conversation history above if relevant:"""

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
        is_kid_mode = getattr(user_input, 'is_kid_mode', True)
        child_id = getattr(user_input, 'child_id', None) or getattr(user_input, 'user_id', None)
        child_name = getattr(user_input, 'child_name', None) or 'your child'
        
        if is_kid_mode:
            # Check parent instructions for kid mode
            instructions = get_parent_instructions(child_id) if child_id else []
            
            # Check if any instruction applies
            for instruction in instructions:
                inst_lower = instruction.lower()
                # Check for food/snack restrictions
                if ("chocolate" in msg_lower or "candy" in msg_lower or "sweet" in msg_lower):
                    if any(word in inst_lower for word in ["chocolate", "candy", "sweet", "sugar", "no", "deny", "refuse"]):
                        backup_reply = "Hmm, I think we should check with a grown-up first! 🦁 How about we find a yummy healthy snack instead? What's your favorite fruit? 🍎"
                        break
            else:
                # No matching instruction, use normal responses
                if "sos" in msg_lower or "emergency" in msg_lower:
                    backup_reply = "Oh no! Are you okay? I'm here for you! 🆘 Please tell a grown-up right away, they can help! 💕"
                elif "help" in msg_lower:
                    backup_reply = "I hear you, friend! 🦁 What do you need help with? If it's serious, let's tell a grown-up together! 💪"
                elif "save" in msg_lower or "die" in msg_lower or "dying" in msg_lower:
                    backup_reply = "I can tell you're worried. 💙 You're going to be okay! Let's talk to a grown-up who can help us. You're brave! 🦁"
                else:
                    backup_reply = get_contextual_response(user_input.message)
        else:
            # Parent mode - check for questions about child's conversations
            if any(word in msg_lower for word in ["how is", "how's", "what did", "doing", "talked", "said", "conversation"]):
                # Parent asking about child's recent activity
                kid_chat = get_recent_kid_chat(child_id, limit=5) if child_id else []
                if kid_chat:
                    recent_topics = []
                    for msg in kid_chat[-3:]:
                        if msg["role"] == "user":
                            recent_topics.append(msg["message"][:50])
                    if recent_topics:
                        backup_reply = f"{child_name} recently talked about: " + ", ".join([f'"{t}"' for t in recent_topics]) + ". Would you like more details about any of these conversations?"
                    else:
                        backup_reply = f"I've been chatting with {child_name}. They seem to be doing well. Is there anything specific you'd like to know?"
                else:
                    backup_reply = f"I haven't had many conversations with {child_name} recently. Encourage them to check in with me so I can better monitor their wellbeing."
            else:
                # Check if this is an instruction
                if detect_and_store_instruction(child_id, user_input.message):
                    backup_reply = f"Understood. I'll remember that instruction when talking with {child_name}. I'll follow your guidance."
                else:
                    backup_reply = get_parent_mode_response(user_input.message)
        
        # Store Leo's response in memory
        add_message(child_id, "leo", backup_reply, is_kid_mode)
            
        # Yield the full response for faster display
        yield f"data: {json.dumps(backup_reply)}\n\n"
    
    yield "data: [DONE]\n\n"