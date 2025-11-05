import os
os.environ["TESTING"] = "True"

from fastapi.testclient import TestClient
from main import app
from database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
import pytest

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_create_persona(client):
    response = client.post(
        "/personas/",
        json={
            "dni": "12345678",
            "nombres": "Test",
            "apellido_paterno": "User",
            "apellido_materno": "One",
            "fecha_nacimiento": "2000-01-01",
            "sexo": "M",
            "estado_civil": "soltero",
            "lugar_nacimiento": "Lima",
            "direccion_actual": "Lima"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["dni"] == "12345678"

def test_read_persona(client):
    # First create a person to read
    client.post(
        "/personas/",
        json={
            "dni": "12345678",
            "nombres": "Test",
            "apellido_paterno": "User",
            "apellido_materno": "One",
            "fecha_nacimiento": "2000-01-01",
            "sexo": "M",
            "estado_civil": "soltero",
            "lugar_nacimiento": "Lima",
            "direccion_actual": "Lima"
        },
    )
    response = client.get("/personas/12345678")
    assert response.status_code == 200
    data = response.json()
    assert data["dni"] == "12345678"

def test_read_nonexistent_persona(client):
    response = client.get("/personas/87654321")
    assert response.status_code == 404
