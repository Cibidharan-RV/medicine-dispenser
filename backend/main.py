import uvicorn
from fastapi import FastAPI
from backend.database import engine
from backend.routers import auth

app = FastAPI(
    title="Medicine Dispenser System API",
    version="0.1.0",
    description="Backend for the automated medicine dispenser project.",
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")

@app.on_event("startup")
def startup():
    # Verify DB connection at startup (sync)
    with engine.connect() as conn:
        pass  # Just ensuring connection works

@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "environment": "development"}
    
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
