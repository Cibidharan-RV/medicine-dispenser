import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

def test_db_connectivity(db_session):
    # Verify we can query the test database
    assert db_session.execute(text("SELECT 1")).scalar() == 1

def test_register_and_login(client: TestClient):
    # Register a doctor
    user_data = {
        "username": "testdoctor",
        "password": "password123",
        "role": "DOCTOR",
        "first_name": "Test",
        "last_name": "Doctor"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    
    # Login (using OAuth2 form data)
    login_data = {
        "username": "testdoctor",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

def test_role_authorization(client: TestClient):
    # Register patient
    client.post("/api/v1/users/", json={
        "username": "testpatient",
        "password": "password123",
        "role": "PATIENT",
        "first_name": "Test",
        "last_name": "Patient"
    })
    
    # Login as patient
    token = client.post("/api/v1/auth/login", data={"username": "testpatient", "password": "password123"}).json()["access_token"]
    
    # Attempt to create a prescription (Requires DOCTOR)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/prescriptions/", json={
        "patient_id": 1,
        "prescription_date": "2023-10-01",
        "start_date": "2023-10-01",
        "end_date": "2023-10-10"
    }, headers=headers)
    
    # Should be forbidden
    assert response.status_code == 403
