from starlette.testclient import TestClient
import inspect
print(f"TestClient class: {TestClient}")
print(f"TestClient init signature: {inspect.signature(TestClient.__init__)}")
