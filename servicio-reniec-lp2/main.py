from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import engine, get_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/personas/", response_model=schemas.PersonaResponse)
def create_persona(persona: schemas.PersonaCreate, db: Session = Depends(get_db)):
    db_persona = crud.get_persona_by_dni(db, dni=persona.dni)
    if db_persona:
        raise HTTPException(status_code=400, detail="DNI already registered")
    return crud.create_persona(db=db, persona=persona)

@app.get("/personas/{dni}", response_model=schemas.PersonaResponse)
def read_persona(dni: str, db: Session = Depends(get_db)):
    db_persona = crud.get_persona_by_dni(db, dni=dni)
    if db_persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")
    return db_persona
