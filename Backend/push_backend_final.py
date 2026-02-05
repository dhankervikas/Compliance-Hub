
import subprocess
import os

backend_dir = os.path.abspath(r"..\..\Backend\AssuRisk")
remote_url = "https://github.com/dhankervikas/assurisk-backend.git"
print(f"Backend Dir: {backend_dir}")
print(f"Remote URL: {remote_url}")

def run_git(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=backend_dir,
            capture_output=True,
            text=True,
            check=False 
        )
        print(f"CMD: git {' '.join(args)}")
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode
    except Exception as e:
        print(f"FAILED: {e}")
        return -1

# Add Remote
# Removing first just in case it exists from a failed run
run_git(["remote", "remove", "origin"]) 
run_git(["remote", "add", "origin", remote_url])

# Push (Force update to overwrite empty init)
print("Force Pushing to origin main...")
run_git(["push", "--force", "-u", "origin", "main"])
