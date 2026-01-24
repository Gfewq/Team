import streamlit as st
import requests
from backend import rag_engine

# --- CONFIGURATION (From TELUS PDF Page 12) ---
# We use the standard /v1/chat/completions endpoint for Gemma
API_URL = "https://gemma-3-27b-3ca9s.paas.ai.telus.com/v1/chat/completions"
API_KEY = "dc8704d41888afb2b889a8ebac81d12f"
MODEL_NAME = "google/gemma-3-27b-it"

# --- PAGE SETUP ---
st.set_page_config(page_title="Leo the Lion", page_icon="🦁")

# Custom CSS to make it look like a game
st.markdown("""
    <style>
    .stApp { background-color: #E0F7FA; }
    .lion-avatar { font-size: 80px; text-align: center; }
    .chat-bubble { 
        background-color: #FFFFFF; 
        padding: 20px; 
        border-radius: 20px; 
        border: 3px solid #FFB74D;
        font-size: 20px;
        color: #333;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .stButton button {
        background-color: #FF9800;
        color: white;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🦁 Leo: Your Diabetes Buddy")

# --- SIDEBAR (Doctor Control Panel) ---
st.sidebar.header("🔧 Doctor Control Panel")
st.sidebar.write("Simulate sensor data here:")
glucose_input = st.sidebar.number_input("Glucose Level", value=5.5, step=0.1)
simulated_msg = st.sidebar.text_input("Device Message", f"Sensor reading is {glucose_input}")

# --- THE LOGIC ---
if st.sidebar.button("📡 Send Signal"):
    
    # 1. RAG ENGINE (Safety Check)
    # We add the value explicitly so your Regex in rag_engine.py can find it
    rag_input = f"{simulated_msg} (Value: {glucose_input})"
    safety_instruction = rag_engine.find_best_protocol(rag_input)
    
    # Show the Doctor what protocol triggered (Debugging)
    st.sidebar.success(f"Protocol Found: {safety_instruction}")

    # 2. THE TELUS BRAIN (Leo Persona)
    # We prepare the prompt for the AI
    system_prompt = f"""
    You are Leo the Lion, a magical companion for a 7-year-old child.
    Current Health Status: {safety_instruction}
    
    Instructions:
    1. If status is LOW, ask for 'Magic Fuel' (Juice).
    2. If status is HIGH, ask for 'Shield Recharge' (Insulin).
    3. If status is NORMAL, suggest a fun game.
    4. Keep response under 2 sentences.
    5. NEVER use medical words like glucose or insulin.
    """

    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # We try the standard Chat format first
    data = {
        "model": MODEL_NAME, 
        "messages": [ 
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Hello Leo!"}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }

    with st.spinner("Leo is thinking..."):
        try:
            # Attempt 1: Chat Endpoint
            response = requests.post(API_URL, headers=headers, json=data)
            
            if response.status_code == 200:
                # Chat Success: Parse 'message.content'
                leo_reply = response.json()['choices'][0]['message']['content']
                st.markdown('<div class="lion-avatar">🦁</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-bubble">{leo_reply}</div>', unsafe_allow_html=True)
            
            # Attempt 2: Fallback to Completion Endpoint (If Chat fails with 404)
            elif response.status_code == 404:
                # Switch URL
                fallback_url = API_URL.replace("/chat/completions", "/completions")
                # Switch Data Format (Prompt string instead of Messages list)
                data["prompt"] = f"{system_prompt}\n\nUser: Hello Leo!\nLeo:"
                del data["messages"]
                
                res2 = requests.post(fallback_url, headers=headers, json=data)
                
                if res2.status_code == 200:
                    # Completion Success: Parse 'text'
                    leo_reply = res2.json()['choices'][0]['text'].strip()
                    st.markdown('<div class="lion-avatar">🦁</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="chat-bubble">{leo_reply}</div>', unsafe_allow_html=True)
                else:
                    st.error(f"Fallback Error ({res2.status_code}): {res2.text}")
            
            else:
                st.error(f"Brain Error ({response.status_code}): {response.text}")
                
        except Exception as e:
            st.error(f"Connection Failed: {e}")

else:
    st.info("Waiting for sensor data...")