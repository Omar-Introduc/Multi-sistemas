import pika
import os
import json
import sys
from database import SessionLocal
from crud import get_persona_by_dni
from prometheus_client import start_http_server, Counter

MESSAGES_PROCESSED = Counter('reniec_messages_processed_total', 'Total messages processed')
MESSAGES_FAILED = Counter('reniec_messages_failed_total', 'Total messages failed to process')

def publish_response(channel, dni, is_valid):
    response = {
        "dni": dni,
        "isValid": is_valid
    }
    channel.basic_publish(
        exchange='bank_direct',
        routing_key='bank.loan.response',
        body=json.dumps(response),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    print(f" [x] Sent response for DNI {dni}: {'Valid' if is_valid else 'Invalid'}")

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(" [.] Malformed JSON received.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        MESSAGES_FAILED.inc()
        return

    dni = data.get("dni")

    if not dni:
        print(" [.] Missing DNI in message.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        MESSAGES_FAILED.inc()
        return

    db = SessionLocal()
    try:
        persona = get_persona_by_dni(db, dni)
        is_valid = persona is not None
        publish_response(ch, dni, is_valid)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        MESSAGES_PROCESSED.inc()
    except Exception as e:
        print(f" [!] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        MESSAGES_FAILED.inc()
    finally:
        db.close()

def main():
    start_http_server(8001)  # Prometheus metrics server

    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    username = os.getenv("RABBITMQ_DEFAULT_USER", "rabbit_user")
    password = os.getenv("RABBITMQ_DEFAULT_PASS", "rabbit_pass")
    credentials = pika.PlainCredentials(username, password)
    
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
