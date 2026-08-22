# Medicine Dispenser System

## Overview

This project implements a backend API for an automated medicine dispenser system. It provides:
- FastAPI endpoints for user management, prescriptions, inventory, dispensing schedules, and dispensing operations.
- SQLAlchemy models that map directly to the existing PostgreSQL schema in `.schema/schema.sql`.
- Role‑based authentication (admin, doctor, caregiver, patient) using JWTs.
- Comprehensive testing with `pytest` and `httpx`.

## Architecture Diagram

```
Client (frontend) → FastAPI (router) → Service layer → SQLAlchemy (async) → PostgreSQL
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your database credentials.
3. Run the seed script to populate initial data: `python scripts/seed_data.py`
4. Start the API: `uvicorn backend.main:app --reload`
5. Visit Swagger UI at `http://localhost:8000/docs`.

## Development

- Run tests: `pytest -q`
- Add new models/schemas in `backend/models` and `backend/schemas`.
- Extend routers in `backend/routers`.
```
