
import uvicorn
import os
import sys

# Ensure we can import app
sys.path.append(os.getcwd())

if __name__ == "__main__":
    print("Starting Uvicorn on port 8001...")
    try:
        uvicorn.run("app.main:app", host="127.0.0.1", port=8002, log_level="debug")
    except Exception as e:
        print(f"Uvicorn Failed: {e}")
