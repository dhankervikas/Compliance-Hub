from app.config import settings
import os

print("--- Environment Check (Gemini) ---")
print(f"Base Directory: {settings.BASE_DIR}")
print(f"Env File: {settings.Config.env_file}")

gemini_key = settings.GEMINI_API_KEY
if gemini_key:
    masked = gemini_key[:8] + "..." + gemini_key[-4:]
    print(f"[OK] GEMINI_API_KEY found: {masked}")
else:
    print("[FAIL] GEMINI_API_KEY NOT found in settings.")
    print("Please check your .env file.")

print("-------------------------")
