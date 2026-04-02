import httpx
from main import app
import sys

try:
    print("Attempting to initialize ASGITransport...")
    transport = httpx.ASGITransport(app=app)
    print("ASGITransport initialized.")
    
    print("Attempting to initialize Client...")
    with httpx.Client(transport=transport, base_url="http://testserver") as client:
        print("Client initialized and entered context.")
        response = client.get("/")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
