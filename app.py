import streamlit as st
from backend import rag_engine   # Safety Logic
from backend import brain        # Leo Persona

st.set_page_config(page_title="Leo: AI Companion", page_icon="🦁")

# CSS (Keep your UI friend's work here if you have it)
st.markdown("""
    <style>
    .stApp { background-color: #E0F7FA; }
    .chat-bubble { 
        background-color: #FFFFFF; padding: 20px; border-radius: 20px; 
        border: 3px solid #FFB74D; font-size: 20px; color: #333;
    }
    .lion-avatar { font-size: 80px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦁 Leo: Universal Health Companion")

# --- GENERIC DATA INPUT ---
# Renamed to allow ANY health data (Asthma, Diabetes, Heart, etc.)
st.sidebar.header("🔧 Sensor Data Stream")
data_type = st.sidebar.selectbox("Sensor Type", ["Glucose Monitor", "Pulse Oximeter", "Smart Inhaler", "Heart Rate"])
sensor_value = st.sidebar.text_input("Raw Value", "5.5") 
simulated_msg = st.sidebar.text_input("System Message", f"Reading is {sensor_value}")

if st.sidebar.button("📡 Process Data"):
    
    # 1. SAFETY LAYER (RAG)
    # Checks your knowledge base for ANY match (Low Sugar, Low Oxygen, High Heart Rate)
    rag_input = f"{data_type}: {simulated_msg} (Value: {sensor_value})"
    safety_instruction = rag_engine.find_best_protocol(rag_input)
    
    st.sidebar.success(f"Protocol: {safety_instruction}")

    # 2. PERSONA LAYER (Brain)
    # Converts protocol into "Lion Speak"
    with st.spinner("Leo is reacting..."):
        leo_reply = brain.get_leo_response(rag_instruction=safety_instruction)

        st.markdown('<div class="lion-avatar">🦁</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble">{leo_reply}</div>', unsafe_allow_html=True)

else:
    st.info("Waiting for IoT stream...")