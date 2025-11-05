import os
os.environ["TESTING"] = "True"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from crud import create_persona, get_persona_by_dni
from schemas import PersonaCreate
from database import Base, engine
import pytest

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_persona(db_session):
    persona_data = {
        "dni": "12345678",
        "nombres": "Test",
        "apellido_paterno": "User",
        "apellido_materno": "One",
        "fecha_nacimiento": "2000-01-01",
        "sexo": "M",
        "estado_civil": "soltero",
        "lugar_nacimiento": "Lima",
        "direccion_actual": "Lima"
    }
    persona_in = PersonaCreate(**persona_data)
    persona_created = create_persona(db_session, persona_in)
    assert persona_created.dni == persona_data["dni"]

    persona_retrieved = get_persona_by_dni(db_session, "12345678")
    assert persona_retrieved.dni == persona_data["dni"]
