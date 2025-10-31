"""
Ejemplo de uso de los modelos RENIEC

Este archivo muestra cómo crear instancias de los modelos
y sus validaciones correspondientes.
"""

from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Ciudadano, ReniecSession, Validador, Base

# Ejemplo de creación de engine para MySQL
# engine = create_engine("mysql+mysqlconnector://usuario:password@localhost:3306/reniec_db")

# Crear todas las tablas
# Base.metadata.create_all(engine)

# Crear session
# Session = sessionmaker(bind=engine)
# session = Session()

def ejemplo_ciudadano():
    """Ejemplo de uso del modelo Ciudadano"""
    
    # Modelo Pydantic para validaciones
    ciudadano_data = CiudadanoModel(
        dni="12345678",
        nombres="Juan Carlos",
        apellidos="Pérez González",
        fecha_nacimiento=date(1990, 5, 15),
        estado_civil="soltero",
        direccion="Av. Principal 123, Lima, Perú",
        telefono="987654321",
        email="juan.perez@email.com",
        estado=True
    )
    
    # Crear instancia SQLAlchemy
    ciudadano = Ciudadano(
        dni=ciudadano_data.dni,
        nombres=ciudadano_data.nombres,
        apellidos=ciudadano_data.apellidos,
        fecha_nacimiento=ciudadano_data.fecha_nacimiento,
        estado_civil=ciudadano_data.estado_civil,
        direccion=ciudadano_data.direccion,
        telefono=ciudadano_data.telefono,
        email=ciudadano_data.email,
        estado=ciudadano_data.estado
    )
    
    return ciudadano

def ejemplo_reniec_session(ciudadano_id: int):
    """Ejemplo de uso del modelo ReniecSession"""
    
    # Modelo Pydantic
    session_data = ReniecSessionModel(
        session_id="sess_abc123def456",
        dni="12345678",
        timestamp=datetime.now(),
        estado=True,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # Crear instancia SQLAlchemy
    session = ReniecSession(
        session_id=session_data.session_id,
        dni=session_data.dni,
        timestamp=session_data.timestamp,
        estado=session_data.estado,
        ip_address=session_data.ip_address,
        user_agent=session_data.user_agent,
        ciudadano_id=ciudadano_id
    )
    
    return session

def ejemplo_validador():
    """Ejemplo de uso del modelo Validador"""
    
    # Modelo Pydantic
    validador_data = ValidadorModel(
        nombre="ValidadorDNIv2",
        version="2.1.0",
        estado="activo"
    )
    
    # Crear instancia SQLAlchemy
    validador = Validador(
        nombre=validador_data.nombre,
        version=validador_data.version,
        estado=True
    )
    validador.activate()
    
    return validador

def mostrar_relaciones():
    """Muestra cómo funcionan las relaciones entre modelos"""
    print("=== RELACIONES ENTRE MODELOS ===\n")
    
    # Crear ciudadano
    ciudadano = Ciudadano(
        dni="87654321",
        nombres="María Elena",
        apellidos="Rodríguez Silva",
        fecha_nacimiento=date(1985, 8, 22),
        estado_civil="casada",
        direccion="Calle Secundaria 456, Arequipa, Perú",
        telefono="987123456",
        email="maria.rodriguez@email.com",
        estado=True
    )
    
    # Crear sesión para este ciudadano
    sesion = ReniecSession(
        session_id="sess_xyz789abc123",
        dni="87654321",
        timestamp=datetime.now(),
        estado=True,
        ip_address="10.0.0.50",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        ciudadano=ciudadano  # Relación establecida
    )
    
    print(f"Ciudadano: {ciudadano.nombres} {ciudadano.apellidos}")
    print(f"Sesiones del ciudadano: {len(ciudadano.sesiones) if ciudadano.sesiones else 0}")
    print(f"Sesión ID: {sesion.session_id}")
    print(f"DNI en sesión: {sesion.dni}")
    print(f"Ciudadano desde sesión: {sesion.ciudadano.nombres if sesion.ciudadano else 'N/A'}")

if __name__ == "__main__":
    print("=== EJEMPLOS DE USO DE MODELOS RENIEC ===\n")
    
    # Ejemplo de ciudadano
    print("1. MODELO CIUDADANO")
    print("-" * 50)
    try:
        ciudadano = ejemplo_ciudadano()
        print(f"✓ Ciudadano creado: {ciudadano.nombres} {ciudadano.apellidos}")
        print(f"  DNI: {ciudadano.dni}")
        print(f"  Email: {ciudadano.email}")
        print(f"  Estado: {'Activo' if ciudadano.estado else 'Inactivo'}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    # Ejemplo de sesión
    print("2. MODELO RENIEC SESSION")
    print("-" * 50)
    try:
        sesion = ejemplo_reniec_session(ciudadano_id=1)
        print(f"✓ Sesión creada: {sesion.session_id}")
        print(f"  DNI: {sesion.dni}")
        print(f"  IP: {sesion.ip_address}")
        print(f"  Estado: {'Activa' if sesion.estado else 'Inactiva'}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    # Ejemplo de validador
    print("3. MODELO VALIDADOR")
    print("-" * 50)
    try:
        validador = ejemplo_validador()
        print(f"✓ Validador creado: {validador.nombre}")
        print(f"  Versión: {validador.version}")
        print(f"  Estado: {'Activo' if validador.estado else 'Inactivo'}")
        print(f"  Fecha activación: {validador.fecha_activacion}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()
    
    # Mostrar relaciones
    mostrar_relaciones()
    
    print("\n=== FIN DE EJEMPLOS ===")
