from pydantic import BaseModel
from datetime import date
from enum import Enum

class Sexo(str, Enum):
    M = 'M'
    F = 'F'

class EstadoCivil(str, Enum):
    soltero = 'soltero'
    casado = 'casado'
    divorciado = 'divorciado'
    viudo = 'viudo'

class PersonaBase(BaseModel):
    dni: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: date
    sexo: Sexo
    estado_civil: EstadoCivil
    lugar_nacimiento: str
    direccion_actual: str

class PersonaCreate(PersonaBase):
    pass

class PersonaResponse(PersonaBase):
    class Config:
        orm_mode = True
