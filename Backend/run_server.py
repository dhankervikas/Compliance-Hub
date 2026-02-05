import uvicorn

if __name__ == "__main__":
    print("Starting AssuRisk Backend...")
    # Run Uvicorn programmatically
    # Matches: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    from app.main import app
    uvicorn.run(app, host="0.0.0.0", port=8002)
