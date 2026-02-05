
import sys
import os

# Ensure backend directory is in path
sys.path.append(os.getcwd())

try:
    from app.main import app
    from fastapi.routing import APIRoute

    print("--- INSPECTING FASTAPI ROUTES ---")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"Path: {route.path} | Methods: {route.methods} | Name: {route.name}")
            if route.dependencies:
                print(f"  Dependencies: {route.dependencies}")
            
    print("\n--- GLOBAL DEPENDENCIES ---")
    print(app.dependency_overrides)
    # Global deps are in app.router.dependencies? No, app.dependencies list from init.
    # But we can check if middleware is present.
    print("\n--- MIDDLEWARE STACK ---")
    for m in app.user_middleware:
        print(f"  {m.cls.__name__}")

except Exception as e:
    print(f"Error inspecting app: {e}")
