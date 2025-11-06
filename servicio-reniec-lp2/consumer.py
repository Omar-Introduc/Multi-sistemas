import pika
import os
import json
from database import SessionLocal
from crud import get_persona_by_dni

def callback(ch, method, properties, body):
    # ... (esta función no cambia) ...
    print(" [x] Received %r" % body)
    data = json.loads(body)
    dni = data.get("dni")

    db = SessionLocal()
    try:
        persona = get_persona_by_dni(db, dni)
        if persona:
            print(f" [.] DNI {dni} is valid.")
            # Here you would publish a response to another queue
        else:
            print(f" [.] DNI {dni} is not valid.")
            # Here you would publish a response to another queue
    finally:
        db.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    # AÑADE ESTAS LÍNEAS
    username = os.getenv("RABBITMQ_DEFAULT_USER", "rabbit_user") # Usa el default de tu .env si no existe
    password = os.getenv("RABBITMQ_DEFAULT_PASS", "rabbit_pass") # Usa el default de tu .env si no existe
    credentials = pika.PlainCredentials(username, password)
    
    # MODIFICA ESTA LÍNEA
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
    )
    
    channel = connection.channel()

    channel.queue_declare(queue='bank.validate.loan', durable=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue='bank.validate.loan', on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)