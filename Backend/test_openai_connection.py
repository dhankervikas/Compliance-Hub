import os
import openai
from dotenv import load_dotenv

# Load Env
load_dotenv(".env")

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key Loaded: {api_key[:8]}...{api_key[-4:] if api_key else 'None'}")

client = openai.OpenAI(api_key=api_key)

try:
    print("Testing gpt-4o...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("Success gpt-4o:", response.choices[0].message.content)
except Exception as e:
    print("Failed gpt-4o:", e)
    
try:
    print("\nTesting gpt-3.5-turbo...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("Success gpt-3.5-turbo:", response.choices[0].message.content)
except Exception as e:
    print("Failed gpt-3.5-turbo:", e)
