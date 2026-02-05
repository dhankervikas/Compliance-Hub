import google.generativeai as genai
from app.config import settings
import traceback

print("--- Testing Gemini Generation ---")
api_key = settings.GEMINI_API_KEY
if not api_key:
    print("No API Key.")
    exit()

print(f"Key: {api_key[:5]}...")
genai.configure(api_key=api_key)

# Try the model we configured
# Try candidates
CANDIDATES = [
    'gemini-2.0-flash-lite-preview-02-05',
    'gemini-flash-latest',
    'gemini-2.0-flash-exp',
    'gemini-1.5-pro-latest'
]

for model_name in CANDIDATES:
    print(f"--- Attempting: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello in JSON format.")
        print(f"SUCCESS with {model_name}!")
        print(response.text)
        break
    except Exception as e:
        print(f"FAILED {model_name}: {e}")

