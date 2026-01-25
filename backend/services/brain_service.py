import os
import json
import httpx
import asyncio
from backend.models import UserMessage
from backend.knowledge import DIABETES_METAPHORS

# Load Env
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("TELUS_API_BASE")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMMA_KEY = os.getenv("GEMMA_API_KEY")
QWEN_KEY = os.getenv("QWEN_API_KEY")

async def get_embedding(text: str):
    """Uses Qwen-Emb for RAG Retrieval"""
    url = f"{BASE_URL}/v1/embeddings" # Adjusted based on debug_url.py findings
    headers = {"Authorization": f"Bearer {QWEN_KEY}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json={"input": text, "model": "qwen-emb"}, timeout=5.0)
            if resp.status_code == 200:
                return resp.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"RAG Error: {e}")
            return None

async def analyze_intent(message: str, user_age: int):
    """
    PHASE 1: LOGIC ENGINE (DeepSeek V3)
    Classifies intent and checks safety guardrails.
    """
    prompt = f"""
    Analyze this message from a {user_age}-year-old child.
    Output JSON ONLY:
    {{
        "intent": "EMERGENCY" | "SYMPTOM" | "CHAT",
        "risk_level": "HIGH" | "LOW",
        "reasoning": "brief reason"
    }}
    Message: "{message}"
    """
    
    # Simulating DeepSeek call (Replace with actual endpoint if different)
    # Note: Using Qwen-Coder or DeepSeek endpoint here depending on availability
    # For now, we assume the DeepSeek endpoint follows standard OpenAI format
    url = f"{BASE_URL}/deepseek/v1/chat/completions" 
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json={
                "model": "deepseek-v3",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "response_format": {"type": "json_object"} 
            }, timeout=3.0)
            return json.loads(resp.json()["choices"][0]["message"]["content"])
        except:
            # Fallback logic if AI fails
            if "hurt" in message or "blood" in message:
                return {"intent": "EMERGENCY", "risk_level": "HIGH"}
            return {"intent": "CHAT", "risk_level": "LOW"}

async def generate_leo_response(user_input: UserMessage, intent_data: dict):
    """
    PHASE 3: EMPATHY ENGINE (Gemma-3-27b)
    Generates the final child-friendly persona response.
    """
    
    # 1. The "Break Glass" Protocol (Safety Override)
    if intent_data.get("intent") == "EMERGENCY" or intent_data.get("risk_level") == "HIGH":
        yield "🚨 I think we need a grown-up right now! Please go get Mom or Dad."
        return

    # 2. Metaphor Injection
    metaphors = DIABETES_METAPHORS
    system_prompt = f"""
    You are Leo the Lion. You are talking to a {user_input.age}-year-old.
    USE THESE WORDS:
    - Glucose -> {metaphors['glucose']}
    - Insulin -> {metaphors['insulin']}
    
    TONE: Brave, warm, protective.
    RESTRICTION: Max 2 sentences. No medical jargon.
    """

    # 3. Call Gemma
    url = f"https://gemma-3-27b-3ca9s.paas.ai.telus.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GEMMA_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "google/gemma-3-27b-it",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input.message}
        ],
        "stream": True,  # ENABLE STREAMING for "Human feel"
        "max_tokens": 150
    }

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, headers=headers, json=payload, timeout=10.0) as response:
            async for chunk in response.aiter_lines():
                if chunk.startswith("data: "):
                    data_str = chunk.replace("data: ", "")
                    if data_str == "[DONE]": break
                    try:
                        data = json.loads(data_str)
                        content = data["choices"][0]["delta"].get("content", "")
                        if content:
                            yield content
                    except:
                        pass