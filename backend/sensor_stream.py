import asyncio
import aiohttp
import random

# --- CONFIGURATION ---
API_URL = "http://localhost:8000/api/log/health"

class SensorStream:
    def __init__(self):
        self.glucose = 5.5
        self.bp_systolic = 110
        self.heart_rate = 75
        self.metric_counter = 0  # Cycle through different metrics

    def generate_packet(self):
        self.metric_counter += 1

        # Cycle through different metrics every 3 readings
        metric_cycle = self.metric_counter % 9

        if metric_cycle < 3:
            # Glucose (3 readings)
            drift = random.uniform(-0.5, 0.5)
            pull = (6.0 - self.glucose) * 0.15
            self.glucose += drift + pull
            self.glucose = max(3.0, min(15.0, self.glucose))
            return {
                "user_id": "child_01",
                "metric_type": "glucose",
                "value": round(self.glucose, 1),
                "unit": "mmol/L"
            }

        elif metric_cycle < 6:
            # Blood Pressure - Systolic (3 readings)
            drift = random.uniform(-5, 5)
            pull = (110 - self.bp_systolic) * 0.1
            self.bp_systolic += drift + pull
            self.bp_systolic = max(80, min(150, self.bp_systolic))
            return {
                "user_id": "child_01",
                "metric_type": "blood_pressure",
                "value": round(self.bp_systolic, 0),
                "unit": "mmHg"
            }

        else:
            # Heart Rate (3 readings)
            drift = random.uniform(-3, 3)
            pull = (75 - self.heart_rate) * 0.1
            self.heart_rate += drift + pull
            self.heart_rate = max(50, min(120, self.heart_rate))
            return {
                "user_id": "child_01",
                "metric_type": "heart_rate",
                "value": round(self.heart_rate, 0),
                "unit": "bpm"
            }

    async def send_data(self, session, data, retries=2):
        """Send data with retry logic."""
        for attempt in range(retries):
            try:
                timeout = aiohttp.ClientTimeout(total=3)
                async with session.post(API_URL, json=data, timeout=timeout) as response:
                    if response.status == 200:
                        server_reply = await response.json()
                        return True, server_reply

                    # retry on non-200
                    if attempt < retries - 1:
                        await asyncio.sleep(0.5)
                        continue
                    return False, f"Status {response.status}"

            except (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(0.5)
                    continue
                return False, f"Connection error: {str(e)[:80]}"

            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(0.5)
                    continue
                return False, f"Error: {str(e)[:80]}"

        return False, "Max retries reached"

    async def run(self):
        print(f"📡 CONNECTING TO LEO BRAIN AT {API_URL}...")

        # Keep-alive off avoids some Windows connection pooling weirdness
        connector = aiohttp.TCPConnector(limit=1, force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            while True:
                # 1. Generate Data
                data = self.generate_packet()

                # 2. Send to Backend with retry
                success, result = await self.send_data(session, data)

                if success:
                    print(
                        f"✅ SENT: {data['metric_type']} {data['value']} {data['unit']} "
                        f"| SERVER: {result.get('event')}"
                    )
                else:
                    print(f"⚠️ Failed to send: {result}")

                # 3. Wait (demo speed)
                await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        stream = SensorStream()
        asyncio.run(stream.run())
    except KeyboardInterrupt:
        print("\n🛑 Stream stopped.")
