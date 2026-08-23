import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database import engine
from backend.routers import auth, users, patients, doctors, prescriptions, schedules, inventory, dispensing, medicines, dispenser

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify DB connection at startup (sync)
    with engine.connect() as conn:
        pass
    yield

app = FastAPI(
    title="Medicine Dispenser System API",
    version="0.1.0",
    description="Backend for the automated medicine dispenser project.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(prescriptions.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(dispensing.router, prefix="/api/v1")
app.include_router(medicines.router, prefix="/api/v1")
app.include_router(dispenser.router, prefix="/api/v1")

@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "environment": "development"}

import os
if os.path.isdir("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
    
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
