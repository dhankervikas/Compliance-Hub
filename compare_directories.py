import os
import shutil

SOURCE_DIR = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product"
DEST_DIR = r"C:\Projects\Compliance_Product"

IGNORE = {'.git', 'node_modules', '__pycache__', 'venv', '.pytest_cache', 'dist', 'build', 'coverage'}

def compare_dirs(src, dst):
    missing_files = []
    missing_dirs = []
    
    # Walk source directory
    for root, dirs, files in os.walk(src):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE]
        
        rel_path = os.path.relpath(root, src)
        if rel_path == ".": rel_path = ""
        
        target_root = os.path.join(dst, rel_path)
        
        # Check if directory exists in target
        if not os.path.exists(target_root):
            missing_dirs.append(rel_path)
            # If dir is missing, all its contents are missing too, but we just list dir for brevity
            continue
            
        # Check files
        for f in files:
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_root, f)
            
            if not os.path.exists(dst_file):
                missing_files.append(os.path.join(rel_path, f))
                
    return missing_dirs, missing_files

if __name__ == "__main__":
    print(f"Comparing contents of:\nSource: {SOURCE_DIR}\nDest:   {DEST_DIR}\n")
    dirs, files = compare_dirs(SOURCE_DIR, DEST_DIR)
    
    print("-" * 40)
    print(f"Missing Directories: {len(dirs)}")
    for d in dirs[:20]:
        print(f" [D] {d}")
    if len(dirs) > 20: print(f" ... and {len(dirs)-20} more.")
    
    print("-" * 40)
    print(f"Missing Files: {len(files)}")
    for f in files[:20]:
        print(f" [F] {f}")
    if len(files) > 20: print(f" ... and {len(files)-20} more.")
    
    print("-" * 40)
    if not dirs and not files:
        print("SUCCESS: Directories match (excluding ignored items).")
    else:
        print("ACTION REQUIRED: Run sync to fix missing items.")
