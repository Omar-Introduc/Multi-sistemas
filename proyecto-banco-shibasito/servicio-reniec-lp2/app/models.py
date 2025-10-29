from sqlalchemy import Column, Integer, String
from .database import Base

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), unique=True, index=True)
    nombre = Column(String(50))
    apellido = Column(String(50))
