# Medicine Dispenser System

## Overview

This project implements a full-stack automated medicine dispenser system. It provides:
- A Python FastAPI backend with endpoints for user management, prescriptions, inventory, dispensing schedules, and dispensing operations.
- A Vanilla HTML/CSS/JS frontend SPA (Single Page Application) built seamlessly into the FastAPI server.
- SQLAlchemy models that map directly to the BCNF compliant PostgreSQL schema.
- Role‑based access control (Doctor, Caregiver, Patient) using JWT authentication.
- Secure transactional endpoints for dispensing using row-level locking.
- Comprehensive testing suite with `pytest`.

## Architecture Diagram

```
Client (Vanilla JS/HTML) → FastAPI (Sync Router) → Service layer → SQLAlchemy (Sync) → PostgreSQL
```

## Getting Started

1. Set up your PostgreSQL database (must be PostgreSQL 17.10) and initialize the schema using `schema/schema.sql`.
2. Install Python dependencies: 
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your database connection string and secret keys.
4. Run the seed script to populate initial testing data: 
   ```bash
   python backend/seed.py
   ```
5. Start the API and Frontend server on port 8001: 
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
   ```
6. Open your browser and navigate to `http://localhost:8001/` to access the application dashboard.
7. Visit the API Documentation (Swagger UI) at `http://localhost:8001/docs`.

## Development

- Run tests: `pytest -v`
- The `frontend/` directory contains all UI logic. It relies on standard browser APIs.
- The `backend/` directory contains all FastAPI routes, Pydantic schemas, and SQLAlchemy models.
