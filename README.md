# 🦁 Leo: The AI Diabetes Companion
**TELUS Hackathon Submission - Track 3: AI + Healthcare**

## 🚀 What it is
Leo is an AI Agent that lives in a child's device. Instead of scary medical data, Leo uses "Child-Centric NLP" to turn glucose monitoring into a game.
- **Low Glucose** = "Leo is hungry! We need Magic Fuel (Juice)."
- **High Glucose** = "Shields down! We need a Recharge (Insulin)."

## 🛠️ Tech Stack
- **Brain:** Google Gemma-3-27b (via TELUS Endpoint)
- **Safety:** Local RAG Engine (SentenceTransformers) for medical accuracy.
- **Interface:** Streamlit (Python)

## 📸 How to Run
1. `pip install -r requirements.txt`
2. `streamlit run app.py`
