import streamlit as st
import json
import time
import os
from backend import rag_engine
from backend import brain

st.set_page_config(page_title="Leo Health", page_icon="🦁", layout="wide")

# --- 1. ROBUST APPLE DESIGN SYSTEM (Fixed Fonts) ---
st.markdown("""
    <style>
    /* Force System Font Everywhere */
    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"], .stMarkdown {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #1D1D1F;
    }
    
    /* Background */
    .stApp { background-color: #F5F5F7; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E5EA;
    }
    
    /* Apple Cards (The White Boxes) */
    .ios-card {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border: 1px solid #E5E5EA;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* CRITICAL ALERT CARD ("Blast Red") */
    .critical-card {
        background-color: #FFEBEE !important;
        border: 2px solid #FF3B30 !important;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(255, 59, 48, 0.25);
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }

    /* Typography Fixes */
    h1, h2, h3, h4 { color: #1D1D1F !important; font-weight: 700 !important; }
    p, div, span { color: #1D1D1F; }
    
    .metric-label {
        font-size: 13px !important; 
        font-weight: 600 !important; 
        text-transform: uppercase;
        color: #86868B !important; 
        margin-bottom: 8px; 
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 32px !important; 
        font-weight: 700 !important; 
        color: #1D1D1F !important;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    
    .metric-sub { font-size: 14px; color: #86868B; font-weight: 500; }
    
    /* Status Colors */
    .status-safe { color: #34C759 !important; }
    .status-danger { color: #FF3B30 !important; }
    .status-monitor { color: #FF9500 !important; }

    /* Leo Chat Bubble */
    .leo-bubble {
        background: #FFFFFF; 
        border-radius: 28px; 
        padding: 30px;
        font-size: 24px; 
        line-height: 1.4; 
        font-weight: 500; 
        color: #1D1D1F;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06); 
        border: 1px solid #F2F2F7;
    }
    
    /* Blue Progress Bars */
    .stProgress > div > div > div > div { background-color: #007AFF; }
    
    /* Clean up Streamlit UI */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ROBUST HELPERS ---
def safe_float(val, default=0.0):
    try:
        if val is None: return default
        return float(val)
    except (ValueError, TypeError):
        return default

def get_trend_str(val):
    if not val: return "Stable"
    return str(val).title()

# --- 3. STATE MANAGEMENT ---
if 'last_processed_time' not in st.session_state:
    st.session_state['last_processed_time'] = 0
if 'current_event' not in st.session_state:
    st.session_state['current_event'] = None
if 'leo_response' not in st.session_state:
    st.session_state['leo_response'] = "I'm ready to help! 🦁"

# --- 4. APP LAYOUT ---
st.title("Leo Health")

with st.sidebar:
    st.header("Control Center")
    mode = st.radio("Source", ["🔴 Live Stream", "🛠️ Manual Input"])
    st.markdown("---")
    if st.session_state['current_event']:
        ts = st.session_state['current_event'].get('timestamp', 'N/A')
        # Clean timestamp display
        display_ts = str(ts).split('T')[-1][:8] if 'T' in str(ts) else ts
        st.caption(f"Last Update: {display_ts}")

# Ingestion Logic
new_data_found = False

if mode == "🔴 Live Stream":
    event_file = "events.jsonl"
    if os.path.exists(event_file):
        try:
            with open(event_file, "r") as f:
                lines = f.readlines()
                if lines:
                    raw_event = json.loads(lines[-1])
                    event_ts = raw_event.get('timestamp', str(time.time()))
                    
                    if event_ts != st.session_state['last_processed_time']:
                        st.session_state['current_event'] = raw_event
                        st.session_state['last_processed_time'] = event_ts
                        new_data_found = True
        except Exception:
            pass
    else:
        st.warning("Waiting for Simulator...")

elif mode == "🛠️ Manual Input":
    with st.form("manual"):
        st.write("Inject Event")
        e_type = st.selectbox("Type", ["glucose_drop", "glucose_spike", "heart_rate_elevated", "asthma_risk"])
        val = st.number_input("Value", 4.5)
        if st.form_submit_button("Simulate"):
            # Auto-calculate risk
            status = "SAFE"
            anom = 0.1
            if "glucose" in e_type and (val < 4.0 or val > 10.0): 
                status = "DANGER"; anom = 0.95
            elif "heart" in e_type and val > 120: 
                status = "MONITOR"; anom = 0.65
                
            st.session_state['current_event'] = {
                "event_type": e_type, "value": val, "unit": "manual",
                "safety_status": status, "trend": "falling" if val < 4 else "rising",
                "health_score": 45.5 if status == "DANGER" else 98.2,
                "anomaly_score": anom, "llm_reasoning": "Manual Injection Test Event",
                "timestamp": str(time.time())
            }
            new_data_found = True

# --- 5. BRAIN (Only runs on new data) ---
if new_data_found and st.session_state['current_event']:
    ev = st.session_state['current_event']
    query = f"{ev['event_type']} {ev['safety_status']} {ev['value']}"
    proto = rag_engine.find_best_protocol(query)
    st.session_state['leo_response'] = brain.get_leo_response(proto)
    st.rerun()

# --- 6. DISPLAY ---
event = st.session_state['current_event']

if event:
    # Safe Extraction
    status = event.get('safety_status', 'SAFE')
    anomaly = safe_float(event.get('anomaly_score', 0))
    h_score = safe_float(event.get('health_score', 0))
    trend = get_trend_str(event.get('trend'))
    e_name = event['event_type'].replace('_', ' ').title()
    
    # Colors
    s_class = "status-safe"
    if status == "DANGER": s_class = "status-danger"
    elif status == "MONITOR": s_class = "status-monitor"

    # TABS
    t1, t2 = st.tabs(["🦁 Patient View", "👨‍⚕️ Clinical Data"])

    # === TAB 1: PATIENT ===
    with t1:
        if status == "DANGER":
            st.markdown(f"<div style='background:#FF3B30; color:white; padding:16px; border-radius:14px; font-weight:700; margin-bottom:24px; text-align:center; font-size:18px; box-shadow: 0 4px 15px rgba(255,59,48,0.4);'>🚨 PARENT ALERT: INTERVENTION REQUIRED</div>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"<div class='ios-card'><div class='metric-label'>Event</div><div class='metric-value' style='font-size:22px'>{e_name}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='ios-card'><div class='metric-label'>Value</div><div class='metric-value'>{event['value']}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='ios-card'><div class='metric-label'>Trend</div><div class='metric-value'>{trend}</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='ios-card'><div class='metric-label'>Status</div><div class='metric-value {s_class}'>{status}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_av, col_bub = st.columns([1, 5])
        with col_av: st.markdown("<div style='font-size:100px; text-align:center;'>🦁</div>", unsafe_allow_html=True)
        with col_bub: st.markdown(f"<div class='leo-bubble'>{st.session_state['leo_response']}</div>", unsafe_allow_html=True)

    # === TAB 2: DOCTOR (Restored Detail) ===
    with t2:
        st.subheader("Real-Time Telemetry")
        
        # Health Score
        st.write(f"**Overall Health Index: {h_score:.1f}/100**")
        st.progress(min(h_score / 100.0, 1.0))
        st.markdown("---")
        
        # Vitals Row
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            g_val = safe_float(event['value']) if 'glucose' in event['event_type'] else 5.5
            st.markdown(f"""<div class='ios-card'><div class='metric-label'>Glucose</div><div class='metric-value'>{g_val} <span style='font-size:16px;color:#86868B'>mmol/L</span></div></div>""", unsafe_allow_html=True)
            st.progress(min(g_val/15.0, 1.0))

        with r1_c2:
            hr = 85
            if 'heart' in event['event_type']: hr = safe_float(event['value'])
            st.markdown(f"""<div class='ios-card'><div class='metric-label'>Heart Rate</div><div class='metric-value'>{int(hr)} <span style='font-size:16px;color:#86868B'>BPM</span></div></div>""", unsafe_allow_html=True)
            st.progress(min(hr/180.0, 1.0))

        with r1_c3:
            spo2 = 98
            if 'oxygen' in event['event_type']: spo2 = safe_float(event['value'])
            st.markdown(f"""<div class='ios-card'><div class='metric-label'>SpO2</div><div class='metric-value'>{int(spo2)} <span style='font-size:16px;color:#86868B'>%</span></div></div>""", unsafe_allow_html=True)
            st.progress(min(spo2/100.0, 1.0))

        st.markdown("<br>", unsafe_allow_html=True)

        # Risk Analysis (BLAST RED Logic)
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        
        # Anomaly Card (Dynamic)
        with r2_c2:
            is_high_risk = anomaly > 0.6
            card_class = "critical-card" if is_high_risk else "ios-card"
            val_color = "#D32F2F" if is_high_risk else "#1D1D1F"
            
            st.markdown(f"""
            <div class='{card_class}'>
                <div class='metric-label'>Anomaly Score</div>
                <div class='metric-value' style='color:{val_color} !important'>{anomaly:.2f}</div>
                <div class='metric-sub'>{'⚠️ HIGH DEVIATION' if is_high_risk else 'Within Variance'}</div>
            </div>""", unsafe_allow_html=True)
            
        with r2_c1:
            mood = 0.75
            if 'mood' in event['event_type']: mood = safe_float(event['value'])
            st.markdown(f"""<div class='ios-card'><div class='metric-label'>Mood Index</div><div class='metric-value'>{mood:.2f}</div></div>""", unsafe_allow_html=True)
            st.progress(min(mood, 1.0))

        with r2_c3:
            asthma = 0.2
            if 'asthma' in event['event_type']: asthma = safe_float(event['value'])
            st.markdown(f"""<div class='ios-card'><div class='metric-label'>Asthma Risk</div><div class='metric-value'>{asthma:.2f}</div></div>""", unsafe_allow_html=True)
            st.progress(min(asthma, 1.0))

        st.markdown("#### 🧠 AI Assessment")
        st.info(event.get('llm_reasoning', "Processing clinical context..."))

# --- 7. AUTO-POLL ---
if mode == "🔴 Live Stream":
    time.sleep(1)
    st.rerun()