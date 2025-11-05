from sqlalchemy import Column, String, Date, Enum
from database import Base

class Persona(Base):
    __tablename__ = "personas"

    dni = Column(String(8), primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(Enum('M', 'F'), nullable=False)
    estado_civil = Column(Enum('soltero', 'casado', 'divorciado', 'viudo'), nullable=False)
    lugar_nacimiento = Column(String(100), nullable=False)
    direccion_actual = Column(String(255), nullable=False)
