
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

# Add
run_git(["add", "."])

# Commit
run_git(["commit", "-m", "Allow all CORS origins for production"])

# Push
print("Pushing update...")
run_git(["push"])
