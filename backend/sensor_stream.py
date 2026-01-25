import asyncio
import aiohttp
import json
from backend.data_simulator import MedicalDataSimulator  # Imports your rich simulator

# --- CONFIGURATION ---
API_URL = "http://localhost:8000/api/log/health"

async def run_rich_sensor_stream():
    print(f"📡 CONNECTING TO LEO BRAIN AT {API_URL}...")
    
    # Initialize the "Smart" Simulator (Rule-based mode for speed)
    simulator = MedicalDataSimulator(deepseek_api_key=None)
    
    async with aiohttp.ClientSession() as session:
        # Start the simulator context
        async with simulator:
            while True:
                # 1. Generate RICH Data (Heart, Glucose, Mood, etc.)
                # This uses the complex logic from your friend's code
                event_data = await simulator.generate_and_analyze_event()
                
                # 2. Format it for the API
                # We map the simulator's output to the format our Backend expects
                payload = {
                    "timestamp": event_data["timestamp"],
                    "event_type": event_data["event_type"],
                    "value": event_data["value"],
                    "unit": event_data["unit"],
                    "urgency": event_data["urgency"],
                    "metadata": event_data["metadata"],
                    "safety_status": event_data["safety_status"],
                    "health_score": event_data.get("health_score", 100),
                    # Pass extra fields so we can debug if needed
                    "llm_reasoning": event_data.get("llm_reasoning", "")
                }
                
                # 3. Send to Backend
                try:
                    async with session.post(API_URL, json=payload) as response:
                        server_reply = await response.json()
                        
                        # Print a nice log message
                        status_icon = "🔴" if payload['safety_status'] == "DANGER" else "🟢"
                        print(f"{status_icon} SENT: {payload['event_type']} | {payload['value']} {payload['unit']} | SERVER: {server_reply.get('event')}")
                        
                except Exception as e:
                    print(f"❌ CONNECTION ERROR: Is the FastAPI server running? ({e})")

                # 4. Wait (Fast updates for the demo!)
                await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(run_rich_sensor_stream())
    except KeyboardInterrupt:
        print("\n🛑 Stream stopped.")