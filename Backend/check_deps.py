
import json

target_path = r"..\..\Frontend\package.json"

try:
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        deps = data.get("dependencies", {})
        if "lucide-react" in deps:
            print("LUCIDE-REACT: FOUND")
        else:
            print("LUCIDE-REACT: MISSING")
except Exception as e:
    print(f"Error: {e}")
