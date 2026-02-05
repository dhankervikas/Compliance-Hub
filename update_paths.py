import os

OLD_PATH = r"C:\Projects\Compliance_Product"
NEW_PATH = r"C:\Projects\Compliance_Product"
ROOT_DIR = r"C:\Projects\Compliance_Product"

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if OLD_PATH.lower() in content.lower():
            # Perform case-insensitive replacement if needed, but for now simple string replace
            # We can use regex for case insensitive, but let's try direct replace first as it's safer
            # Actually, Windows paths are case insensitive, but the string in code might be exact match or not.
            # Let's handle the specific string we saw: "C:\Projects\Compliance_Product"
            
            new_content = content.replace(OLD_PATH, NEW_PATH)
            
            # Also handle double backslashes if present
            old_path_escaped = OLD_PATH.replace('\\', '\\\\')
            new_path_escaped = NEW_PATH.replace('\\', '\\\\')
            new_content = new_content.replace(old_path_escaped, new_path_escaped)

             # Also handle forward slashes
            old_path_forward = OLD_PATH.replace('\\', '/')
            new_path_forward = NEW_PATH.replace('\\', '/')
            new_content = new_content.replace(old_path_forward, new_path_forward)

            if content != new_content:
                print(f"Updating {filepath}")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    print(f"Scanning {ROOT_DIR}...")
    for root, dirs, files in os.walk(ROOT_DIR):
        if '.git' in dirs:
            dirs.remove('.git')
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if 'venv' in dirs:
            dirs.remove('venv')
            
        for file in files:
            if file.endswith(('.py', '.js', '.bat', '.md', '.json', '.txt')):
                filepath = os.path.join(root, file)
                replace_in_file(filepath)
    print("Done.")

if __name__ == "__main__":
    main()
