import os
import pymysql
import time

# Database connection details from environment variables
DB_HOST = "mysql-db"
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE")

def seed_data():
    """Seeds the database with initial data."""
    conn = None
    try:
        # Wait for the database to be ready
        time.sleep(10)

        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME)
        cursor = conn.cursor()

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM personas")
        if cursor.fetchone()[0] > 0:
            print("Data already seeded.")
            return

        # Insert sample data
        personas_data = [
            ('12345678', 'Juan', 'Perez', 'Gomez', '1990-01-01', 'M', 'soltero', 'Lima', 'Av. Siempre Viva 123'),
            ('87654321', 'Maria', 'Lopez', 'Rodriguez', '1992-02-02', 'F', 'casado', 'Arequipa', 'Calle Falsa 456')
        ]

        insert_query = """
        INSERT INTO personas (dni, nombres, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado_civil, lugar_nacimiento, direccion_actual)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.executemany(insert_query, personas_data)
        conn.commit()
        print("Data seeded successfully.")

    except pymysql.MySQLError as e:
        print(f"Error seeding data: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_data()
