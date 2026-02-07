
import os
import sys

def check_ai_setup():
    print("=== AI Setup Verification Tool ===")
    
    # 1. Check Module
    try:
        import openai
        print("[OK] openai library installed.")
    except ImportError:
        print("[ERROR] 'openai' library missing. Run: pip install openai")
        return

    # 2. Check Environment Variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY environment variable is NOT set.")
        print("Tip: set OPENAI_API_KEY=sk-...")
        return
    else:
        print(f"[OK] OPENAI_API_KEY found (starts with {api_key[:8]}...)")

    # 3. Test Connection
    print("Testing connection to OpenAI...")
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("[SUCCESS] OpenAI is reachable!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")

if __name__ == "__main__":
    check_ai_setup()
