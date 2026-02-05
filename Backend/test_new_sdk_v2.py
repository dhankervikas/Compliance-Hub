from google import genai
from app.config import settings

api_key = settings.GEMINI_API_KEY
if not api_key:
    print("No API Key")
    exit()

print("Testing google-genai SDK with forced settings...")
try:
    # Try default
    print("\n--- Try 1: Default ---")
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents="Hello"
        )
        print(f"SUCCESS (Default): {response.text}")
    except Exception as e:
        print(f"FAILED (Default): {e}")

    # Try 2: Explicit v1alpha
    print("\n--- Try 2: Force v1alpha ---")
    client_v1 = genai.Client(api_key=api_key, http_options={'api_version':'v1alpha'})
    try:
        response = client_v1.models.generate_content(
            model="gemini-1.5-flash", 
            contents="Hello"
        )
        print(f"SUCCESS (v1alpha): {response.text}")
    except Exception as e:
        print(f"FAILED (v1alpha): {e}")

    # Try 3: gemini-2.0-flash-exp (should default to v1alpha for this model?)
    print("\n--- Try 3: gemini-2.0-flash-exp ---")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", 
            contents="Hello"
        )
        print(f"SUCCESS (2.0): {response.text}")
    except Exception as e:
        print(f"FAILED (2.0): {e}")

except Exception as e:
    print(f"FAILED SETUP: {e}")
