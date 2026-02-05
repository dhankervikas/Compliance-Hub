import os
import shutil

SOURCE_DIR = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product"
DEST_DIR = r"C:\Projects\Compliance_Product"

IGNORE = {'.git', 'node_modules', '__pycache__', 'venv', '.pytest_cache', 'dist', 'build', 'coverage'}

def sync_dirs(src, dst):
    copied_count = 0
    # Walk source directory
    for root, dirs, files in os.walk(src):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE]
        
        rel_path = os.path.relpath(root, src)
        if rel_path == ".": rel_path = ""
        
        target_root = os.path.join(dst, rel_path)
        
        # Ensure target directory exists
        if not os.path.exists(target_root):
            os.makedirs(target_root)
            print(f"[DIR] Created {target_root}")
            
        # Check files
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_root, f)
            
            if not os.path.exists(dst_file):
                try:
                    shutil.copy2(src_file, dst_file)
                    print(f"[FILE] Copied {f}")
                    copied_count += 1
                except Exception as e:
                    print(f"[ERR] Failed to copy {f}: {e}")
                    
    return copied_count

if __name__ == "__main__":
    print(f"Syncing missing items...\nSource: {SOURCE_DIR}\nDest:   {DEST_DIR}\n")
    count = sync_dirs(SOURCE_DIR, DEST_DIR)
    print("-" * 40)
    print(f"Sync Complete. Copied {count} files.")
