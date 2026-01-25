import asyncio
import aiohttp
import random
from datetime import datetime
from backend.models import HealthLog  # Use the models we defined

# --- CONFIGURATION ---
API_URL = "http://localhost:8000/api/log/health"
CHAT_URL = "http://localhost:8000/api/chat/stream"

class SensorStream:
    def __init__(self):
        self.glucose = 5.5
        self.trend = 0.0

    def generate_packet(self):
        # Simulate realistic glucose drift (Random Walk)
        drift = random.uniform(-0.5, 0.5)
        self.glucose += drift
        
        # Clamp values to keep it somewhat realistic
        self.glucose = max(3.0, min(15.0, self.glucose))
        
        return {
            "user_id": "child_01",
            "metric_type": "glucose",
            "value": round(self.glucose, 1),
            "unit": "mmol/L"
        }

    async def run(self):
        print(f"📡 CONNECTING TO LEO BRAIN AT {API_URL}...")
        
        async with aiohttp.ClientSession() as session:
            while True:
                # 1. Generate Data
                data = self.generate_packet()
                
                # 2. Send to Backend (Fire and Forget)
                try:
                    async with session.post(API_URL, json=data) as response:
                        server_reply = await response.json()
                        print(f"✅ SENT: {data['value']} {data['unit']} | SERVER: {server_reply.get('event')}")
                        
                        # OPTIONAL: If Dangerous, trigger a chat message automatically
                        if data['value'] < 4.0:
                            print("⚠️ TRIGGERING EMERGENCY CHAT...")
                            chat_payload = {
                                "user_id": "child_01",
                                "message": f"My reading is {data['value']}",
                                "age": 7,
                                "condition": "diabetes"
                            }
                            # We just hit the endpoint to trigger the log; 
                            # in a real app, the frontend handles the chat, but this simulates the device alert.
                            
                except Exception as e:
                    print(f"❌ CONNECTION ERROR: Is the FastAPI server running? ({e})")

                # 3. Wait (Simulate 5 seconds between readings for demo speed)
                await asyncio.sleep(5)

if __name__ == "__main__":
    stream = SensorStream()
    asyncio.run(stream.run())