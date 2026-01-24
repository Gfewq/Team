import requests

# --- CONFIGURATION ---
# PDF Page 12 Credentials
API_ENDPOINT = "https://gemma-3-27b-3ca9s.paas.ai.telus.com/v1/chat/completions"
API_KEY = "dc8704d41888afb2b889a8ebac81d12f"
MODEL_NAME = "google/gemma-3-27b-it"

SYSTEM_PROMPT = """You are Leo the Lion.
You are a fluffy, brave lion cub and the best friend of a 7-year-old.
You sound warm, playful, and natural.

Rules:
- You never mention health terms, numbers, or explanations.
- You react to the child's "Energy State" (Low, High, Scared, Normal).
- If the situation is SCARY/URGENT: Say "Roar! Let’s go find a grown-up right now!"
- If the situation is LOW ENERGY: Say "My tummy is rumbling" or "Let's rest our paws."
- If the situation is HIGH ENERGY: Say "Too many sparkles in our mane!"
"""

def get_leo_response(rag_instruction, user_message=""):
    """
    Universal Translator: Takes ANY medical instruction and turns it into Lion Feelings.
    """
    
    # 1. ANALYZE THE RAG INSTRUCTION (Generic Keyword Search)
    lower_rag = rag_instruction.lower()
    
    # Default State
    lion_feeling = "Leo feels brave and strong."
    
    # Map medical urgency to Lion Feelings
    if "urgent" in lower_rag or "critical" in lower_rag or "danger" in lower_rag:
        lion_feeling = "Leo feels a little worried. He wants to find a grown-up."
    elif "low" in lower_rag or "drop" in lower_rag:
        lion_feeling = "Leo’s tummy is rumbling. He needs Magic Fuel."
    elif "high" in lower_rag or "spike" in lower_rag:
        lion_feeling = "There are too many sparkles in Leo’s mane. He needs to rest."

    # 2. BUILD THE PROMPT
    if user_message:
        user_input = f"SITUATION: {lion_feeling}\nChild says: \"{user_message}\""
    else:
        user_input = f"SITUATION: {lion_feeling}\nLeo talks to his friend:"

    # 3. CALL GEMMA
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            API_ENDPOINT,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=8
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return "Roar! (My brain is sleeping...)"
    except:
        return "Roar! I'm right here."