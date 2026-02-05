
import os

frontend_path = r"..\..\Frontend\src\components\Login.js"

try:
    with open(frontend_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # The block to remove
    target_block = r"""
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Default credentials:</p>
          <p className="font-mono">admin / admin123</p>
        </div>"""
    
    # Remove it (strip whitespace to match exactly if needed, or better, use replace on the string literal if exact match)
    # The read output showed exactly the indentation. Let's try flexible replacement or just exact string match from read output.
    
    # Exact match from previous output:
    target_block_exact = """        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Default credentials:</p>
          <p className="font-mono">admin / admin123</p>
        </div>"""
        
    if target_block_exact in content:
        new_content = content.replace(target_block_exact, "")
        with open(frontend_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("SUCCESS: Credentials removed.")
    else:
        print("WARNING: Could not find exact block. Trying simpler replacement...")
        # Fallback: remove just the inner text if block doesn't match
        # But for now, let's assume exact match works or fail.
        print("Content sample around target:")
        print(content[-500:])

except Exception as e:
    print(f"Error: {e}")
