
import requests
import sys

# Production Backend URL
API_URL = "https://assurisk-backend.onrender.com/api/v1/auth"
# User Data
USER_DATA = {
    "username": "admin",
    "password": "admin123",
    "email": "admin@assurisk.ai",
    "full_name": "System Administrator"
}

print(f"Registering Admin User at {API_URL}...")

try:
    # 1. Register
    response = requests.post(f"{API_URL}/register", json=USER_DATA)
    
    if response.status_code == 201:
        print("SUCCESS: Admin user created.")
    elif response.status_code == 400:
        print("WARNING: User likely already exists (or DB persistent?).")
        print(response.json())
    else:
        print(f"ERROR: Failed to register ({response.status_code})")
        print(response.text)

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
