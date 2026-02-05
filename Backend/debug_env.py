import sys
import os

print("--- SYS.EXECUTABLE ---")
print(sys.executable)
print("--- SYS.PREFIX ---")
print(sys.prefix)

print("--- SYS.PATH ---")
for p in sys.path:
    print(p)

print("\n--- CWD ---")
print(os.getcwd())

try:
    import app.api.deps
    print("\n--- APP.API.DEPS FILE ---")
    print(app.api.deps.__file__)
except ImportError:
    print("\nCould not import app.api.deps")
except Exception as e:
    print(f"\nError: {e}")
