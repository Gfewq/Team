import asyncio
import aiohttp
import json
import argparse
from backend.data_simulator import MedicalDataSimulator
from backend.child_profiles import list_children, get_child

# --- CONFIGURATION ---
API_URL = "http://localhost:8000/api/log/health"


async def run_rich_sensor_stream(child_id: str = None, scenario: str = None):
    """
    Run the sensor stream for a specific child.
    
    Args:
        child_id: ID of the child to simulate for (or None for default)
        scenario: Optional scenario to run (or None for continuous random)
    """
    # Load child profile if specified
    child_name = "Default Child"
    child_profile = None
    
    if child_id:
        child = get_child(child_id)
        if child:
            child_name = child.name
            child_profile = child.model_dump()
            print(f"👶 Simulating for: {child.name} (Age {child.age}, {child.condition})")
        else:
            print(f"⚠️  Child {child_id} not found, using default profile")
    else:
        # List available children
        children = list_children()
        if children:
            print("\n📋 Available children:")
            for c in children:
                print(f"   - {c.id}: {c.name} (Age {c.age}, {c.condition})")
            print(f"\nTip: Run with --child <child_id> to simulate for a specific child\n")
    
    print(f"📡 CONNECTING TO LEO BRAIN AT {API_URL}...")
    
    # Initialize simulator with child profile
    simulator = MedicalDataSimulator(
        child_id=child_id,
        child_profile=child_profile,
        deepseek_api_key=None
    )
    
    async with aiohttp.ClientSession() as session:
        async with simulator:
            # If a scenario was specified, run it
            if scenario:
                print(f"🎬 Running scenario: {scenario}")
                try:
                    events = await simulator.run_scenario(
                        scenario,
                        event_interval_seconds=2,
                        save_to_history=True
                    )
                    print(f"✅ Scenario complete! Generated {len(events)} events")
                    for event in events:
                        status_icon = "🔴" if event.get('safety_status') == "DANGER" else "🟡" if event.get('safety_status') == "MONITOR" else "🟢"
                        print(f"  {status_icon} {event.get('event_type')} | {event.get('value')} {event.get('unit')}")
                    return
                except ValueError as e:
                    print(f"❌ Scenario error: {e}")
                    return
            
            # Otherwise run continuous simulation
            print(f"🔄 Starting continuous simulation for {child_name}...")
            while True:
                # Generate event
                event_data = await simulator.generate_and_analyze_event()
                
                # Format for API
                payload = {
                    "timestamp": event_data["timestamp"],
                    "event_type": event_data["event_type"],
                    "value": event_data["value"],
                    "unit": event_data["unit"],
                    "urgency": event_data["urgency"],
                    "metadata": event_data["metadata"],
                    "safety_status": event_data["safety_status"],
                    "health_score": event_data.get("health_score", 100),
                    "llm_reasoning": event_data.get("llm_reasoning", "")
                }
                
                # Send to Backend
                try:
                    async with session.post(API_URL, json=payload) as response:
                        server_reply = await response.json()
                        status_icon = "🔴" if payload['safety_status'] == "DANGER" else "🟡" if payload['safety_status'] == "MONITOR" else "🟢"
                        print(f"{status_icon} [{child_name}] {payload['event_type']} | {payload['value']} {payload['unit']} | SERVER: {server_reply.get('event')}")
                except Exception as e:
                    print(f"❌ CONNECTION ERROR: Is the FastAPI server running? ({e})")

                await asyncio.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Leo Health Sensor Stream")
    parser.add_argument("--child", type=str, default=None, help="Child ID to simulate for")
    parser.add_argument("--scenario", type=str, default=None, help="Scenario to run (e.g., hypoglycemia_episode)")
    parser.add_argument("--list-scenarios", action="store_true", help="List available scenarios")
    
    args = parser.parse_args()
    
    if args.list_scenarios:
        from backend.scenarios import list_scenarios
        print("\n📋 Available scenarios:")
        for s in list_scenarios():
            print(f"   - {s['id']}: {s['name']} ({s['category']})")
            print(f"     {s['description']}")
        print()
    else:
        try:
            asyncio.run(run_rich_sensor_stream(child_id=args.child, scenario=args.scenario))
        except KeyboardInterrupt:
            print("\n🛑 Stream stopped.")