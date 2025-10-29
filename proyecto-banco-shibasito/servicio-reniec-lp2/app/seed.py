from .database import SessionLocal, engine, Base
from .models import Persona
import time

def seed_data():
    # Wait for the database to be fully ready
    time.sleep(15)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if data already exists
    if db.query(Persona).count() == 0:
        print("Seeding database...")
        # Create sample personas
        personas = [
            Persona(dni="12345678", nombre="Juan", apellido="Perez"),
            Persona(dni="87654321", nombre="Maria", apellido="Gomez"),
            Persona(dni="11223344", nombre="Carlos", apellido="Rodriguez")
        ]

        db.bulk_save_objects(personas)
        db.commit()
        print("Database seeded successfully.")
    else:
        print("Database already seeded.")

    db.close()

if __name__ == "__main__":
    seed_data()
