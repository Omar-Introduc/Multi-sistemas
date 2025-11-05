from sqlalchemy.orm import Session
import models
import schemas

def get_persona_by_dni(db: Session, dni: str):
    return db.query(models.Persona).filter(models.Persona.dni == dni).first()

def create_persona(db: Session, persona: schemas.PersonaCreate):
    db_persona = models.Persona(**persona.dict())
    db.add(db_persona)
    db.commit()
    db.refresh(db_persona)
    return db_persona
