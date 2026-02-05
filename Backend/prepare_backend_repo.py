
import subprocess
import os

backend_dir = os.path.abspath(r"..\..\Backend\AssuRisk")
print(f"Backend Dir: {backend_dir}")

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

# Init
run_git(["init"])

# Config (local to this repo, just in case)
# run_git(["config", "user.email", "you@example.com"]) 
# run_git(["config", "user.name", "Your Name"])

# Add
run_git(["add", "."])

# Commit
run_git(["commit", "-m", "Initial backend commit for deployment"])

# Rename branch
run_git(["branch", "-M", "main"])

print("Ready to add remote!")
