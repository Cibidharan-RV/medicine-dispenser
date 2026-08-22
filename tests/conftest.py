import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import Base, get_db

# Use a separate test database. MUST NOT be the development database.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://postgres:rvcd123@localhost:5432/medicine_dispenser_test"
)

try:
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception:
    engine = None

@pytest.fixture(scope="function")
def setup_db():
    if not engine:
        pytest.skip("Test database engine could not be initialized.")
    # Create test tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown test tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_db):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
