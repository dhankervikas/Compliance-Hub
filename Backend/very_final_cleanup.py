
import os

files = [
    "seed_remote.py",
    "seed_processes_fixed.py",
    "seed_processes_remote.py",
    "create_remote_admin.py",
    "update_frontend_ui.py",
    "read_framework_detail.py"
]

print("Final Cleanup...")
for f in files:
    try:
        if os.path.exists(f):
            os.remove(f)
            print(f"[Deleted] {f}")
    except Exception as e:
        print(f"[Error] {f}: {e}")
