import requests

BASE_URL = "https://qwen-emb-3ca9s.paas.ai.telus.com"
API_KEY = "d14ac3d17de38782334555fcc0537969"

paths_to_try = [
    "/v1/embeddings",      # Standard OpenAI
    "/embeddings",         # Common PaaS alternative
    "/v1/models",          # Check if we can just 'ping' the server
    ""                     # Try raw base URL
]

print("--- DIAGNOSING CONNECTION ---")
for path in paths_to_try:
    full_url = BASE_URL + path
    print(f"Trying: {full_url} ...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Simple test payload
    data = {
        "input": "test",
        "model": "qwen-emb"
    }
    
    try:
        # We use GET for /models and POST for embeddings
        if "models" in path:
            response = requests.get(full_url, headers=headers)
        else:
            response = requests.post(full_url, headers=headers, json=data)
            
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS! The correct URL is: {full_url}")
            print("Update your rag_engine.py with this URL.")
            break
        elif response.status_code == 404:
            print("❌ 404 Not Found (Wrong Path)")
        else:
            print(f"⚠️ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Connection Failed: {e}")
    print("-" * 20)