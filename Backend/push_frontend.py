
import subprocess
import os

frontend_dir = os.path.abspath(r"..\..\Frontend")
print(f"Frontend Dir: {frontend_dir}")

def run_git(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=frontend_dir,
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

# Check Status
run_git(["status"])

# Add
run_git(["add", "."])

# Commit
run_git(["commit", "-m", "Refactor for production: Env vars and redirect fix"])

# Check Remote
run_git(["remote", "-v"])

# Push
print("Attempting Push...")
run_git(["push"])
