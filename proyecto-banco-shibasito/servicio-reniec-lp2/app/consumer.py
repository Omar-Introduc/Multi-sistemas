import pika
import os
import json
from .database import SessionLocal
from .models import Persona

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")

def callback(ch, method, properties, body):
    data = json.loads(body)
    dni = data.get("dni")
    print(f" [x] Received DNI for verification: {dni}")

    db = SessionLocal()
    persona = db.query(Persona).filter(Persona.dni == dni).first()
    db.close()

    response = {}
    if persona:
        response = {
            "dni": persona.dni,
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "status": "VALID"
        }
    else:
        response = {
            "dni": dni,
            "status": "INVALID"
        }

    # Send response back
    ch.basic_publish(
        exchange='',
        routing_key='respuesta_verificacion',
        body=json.dumps(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue='verificacion_dni')
    channel.queue_declare(queue='respuesta_verificacion')

    channel.basic_consume(
        queue='verificacion_dni',
        on_message_callback=callback
    )

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
