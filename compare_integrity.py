import os
import filecmp
import shutil

SOURCE_DIR = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product"
DEST_DIR = r"C:\Projects\Compliance_Product"

IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'node_modules', '.idea', '.vscode', 'Frontend_Backup', 'reports', 'uploads', 'mocks', 'generated_docs'}

def get_all_files(directory):
    file_set = set()
    for root, dirs, files in os.walk(directory):
        # Filter directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith('.pyc') or file.endswith('.log') or file.endswith('.txt'):
                continue
            
            rel_path = os.path.relpath(os.path.join(root, file), directory)
            file_set.add(rel_path)
    return file_set

def compare_dirs():
    print(f"Comparing Source: {SOURCE_DIR}")
    print(f"       vs Dest:   {DEST_DIR}")
    
    source_files = get_all_files(SOURCE_DIR)
    dest_files = get_all_files(DEST_DIR)
    
    missing_in_dest = source_files - dest_files
    missing_in_source = dest_files - source_files
    
    print(f"\n--- MISSING IN DESTINATION (C:\\Projects) [{len(missing_in_dest)}] ---")
    for f in sorted(list(missing_in_dest))[:20]:
        print(f" [MISSING] {f}")
    if len(missing_in_dest) > 20: print(f" ... and {len(missing_in_dest)-20} more.")

    print(f"\n--- MISSING IN SOURCE (OneDrive) [{len(missing_in_source)}] ---")
    for f in sorted(list(missing_in_source))[:20]:
        print(f" [NEW] {f}")
    if len(missing_in_source) > 20: print(f" ... and {len(missing_in_source)-20} more.")

    # Check content of shared files
    common_files = source_files.intersection(dest_files)
    print(f"\n--- CONTENT DIFFS (Sample) ---")
    diff_count = 0
    for f in common_files:
        src_path = os.path.join(SOURCE_DIR, f)
        dst_path = os.path.join(DEST_DIR, f)
        
        try:
            if not filecmp.cmp(src_path, dst_path, shallow=False):
                print(f" [DIFF] {f}")
                diff_count += 1
                if diff_count > 10:
                    print(" ... stopping diff check (too many)")
                    break
        except Exception as e:
            print(f" [ERR] {f}: {e}")

if __name__ == "__main__":
    compare_dirs()
