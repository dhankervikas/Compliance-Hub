"""
Quick Policy Generator
======================
Generates priority policies with one command
"""
import os
from app.services.ai_policy_service import PolicyGenerationService

# Set API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not set in .env file!")
    exit(1)

# Priority policies to generate
PRIORITY_POLICIES = [
    "ISMS Scope",
    "Context of the Organization",
    "Information Security Policy",
    "Access Control Policy",
    "Incident Response Policy",
    "Backup and Recovery Policy"
]

print("Generating 6 priority policies...\n")

service = PolicyGenerationService(api_key=api_key)

for i, policy_name in enumerate(PRIORITY_POLICIES, 1):
    print(f"[{i}/6] Generating: {policy_name}")
    result = service.generate_policy(policy_name)
    
    if result.get("success"):
        print(f"  ✅ {result['metadata']['word_count']} words")
        
        # Save to file
        filename = f"{policy_name.replace(' ', '_')}.md"
        filepath = f"generated_policies/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result["content"])
        print(f"  📄 Saved to: {filepath}\n")
    else:
        print(f"  ❌ Failed: {result.get('error')}\n")

print("✅ Done!")
