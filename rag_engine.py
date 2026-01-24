import re
import numpy as np
from sentence_transformers import SentenceTransformer
from knowledge_base import SAFETY_PROTOCOLS

# --- SETUP (Runs once) ---
print("⬇️  Loading Local AI Model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2') 

def get_embedding(text):
    return model.encode(text)

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- INITIALIZATION ---
print("🧠 Initializing Knowledge Base...")
for protocol in SAFETY_PROTOCOLS:
    protocol["vector"] = get_embedding(protocol["situation"])
print("✅ Knowledge Base Ready! (Running Locally)")

def find_best_protocol(user_query):
    # --- 1. THE SAFETY CHECK (Regex) ---
    # We look for the number in the text (e.g. "3.2" or "15.0")
    # This guarantees the right protocol triggers, even if the AI gets confused.
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", user_query)
    
    if numbers:
        val = float(numbers[0])
        
        # ZONE A: Hypoglycemia (Dangerous Low)
        if val < 4.0:
            return "URGENT: Glucose is critically LOW. STOP everything. Ask for 'Magic Fuel' (Juice) immediately."
            
        # ZONE B: Hyperglycemia (High)
        elif val > 10.0:
            return "Glucose is HIGH. Suggest drinking water ('Hydration Potion') and checking insulin ('Shield')."
            
        # ZONE C: Normal Range (4.0 - 10.0)
        else:
            return "Glucose is Stable/Normal. Be playful. Suggest playing a game or ask about their day."

    # --- 2. STANDARD AI SEARCH (Fallback) ---
    # If there is no number, we use the vector search to match emotions/questions
    query_vector = get_embedding(user_query)
    best_score = -1
    best_protocol = None
    
    for protocol in SAFETY_PROTOCOLS:
        score = cosine_similarity(query_vector, protocol["vector"])
        if score > best_score:
            best_score = score
            best_protocol = protocol
            
    if best_score < 0.25: 
        return "Standard Protocol: Be friendly, keep the tone light."
        
    return best_protocol["instruction"]

# --- TEST IT ---
if __name__ == "__main__":
    print("------------------------------------------------")
    # TEST 1: Dangerous Low
    print(f"Test 3.2: {find_best_protocol('Reading is 3.2')}")
    # TEST 2: High
    print(f"Test 15.0: {find_best_protocol('Reading is 15.0')}")
    # TEST 3: Normal
    print(f"Test 5.5: {find_best_protocol('Reading is 5.5')}")
    print("------------------------------------------------")