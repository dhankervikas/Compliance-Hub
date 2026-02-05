
import uvicorn
import os
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Import the existing app structure - mimicking main.py content logic here
# But importing from app.main is safer IF we trust debug_imports.
# Let's try importing app.main FIRST. If that fails we paste.
# Actually, let's paste the KEY parts: Middleware.

from app.main import app as application
import app.main
print(f"!!! REAL MAIN.PY LOCATION: {app.main.__file__} !!!")
print(f"!!! APP TYPE: {type(application)} !!!")
# We know app.main has the ForcePreflightMiddleware added.

if __name__ == "__main__":
    print("Starting FIXED Server...")
    uvicorn.run(application, host="127.0.0.1", port=8000)
