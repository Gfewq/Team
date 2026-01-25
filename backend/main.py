from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.models import UserMessage, HealthLog
from backend.services.brain_service import analyze_intent, generate_leo_response
import asyncio

app = FastAPI(title="Leo Health API", version="2.0")

# Allow React Frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock this down for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GAMIFICATION STATE (Simple In-Memory for Hackathon) ---
user_stats = {
    "xp": 120,
    "level": 3,
    "streak": 5,
    "status": "Healthy"
}

@app.get("/")
def health_check():
    return {"status": "Leo is awake!", "stats": user_stats}

@app.post("/api/chat/stream")
async def chat_stream(user_msg: UserMessage):
    """
    The Main Interaction Loop:
    1. Analyze Intent (DeepSeek)
    2. Stream Response (Gemma)
    """
    print(f"🦁 User ({user_msg.age}y): {user_msg.message}")
    
    # 1. Logic / Safety Check
    intent = await analyze_intent(user_msg.message, user_msg.age)
    print(f"🧠 Brain Analysis: {intent}")
    
    # 2. Empathy Stream
    return StreamingResponse(
        generate_leo_response(user_msg, intent), 
        media_type="text/event-stream"
    )

@app.post("/api/log/health")
def log_health(log: HealthLog):
    global user_stats
    
    # 1. Update Game Stats based on Health Score
    if log.health_score:
        user_stats["xp"] += int(log.health_score / 10) # 100 health = 10 XP
    
    # 2. Update Status Text based on Event Type
    if log.safety_status == "DANGER":
        user_stats["status"] = "Needs Help! 🚨"
    elif log.safety_status == "MONITOR":
        user_stats["status"] = "Check Engine ⚠️"
    else:
        user_stats["status"] = "Super Strong 🦁"

    # 3. Dynamic Avatar State (For the UI to react)
    # We send this back so the frontend knows if Leo should look sad/happy
    avatar_mood = "happy"
    if log.event_type == "glucose_drop" or log.safety_status == "DANGER":
        avatar_mood = "worried"
    
    # Check for level up
    if user_stats["xp"] >= user_stats["level"] * 100:
        user_stats["level"] += 1
        user_stats["xp"] = 0
    
    return {
        "event": "LOGGED", 
        "xp_gained": int(log.health_score / 10) if log.health_score else 5,
        "avatar_mood": avatar_mood
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)