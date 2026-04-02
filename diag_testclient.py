from fastapi.testclient import TestClient
from main import app
import sys

try:
    print("Attempting to initialize TestClient...")
    client = TestClient(app)
    print("TestClient initialized.")
    
    response = client.get("/")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
