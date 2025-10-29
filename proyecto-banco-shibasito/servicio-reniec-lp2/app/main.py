from . import consumer
from .database import engine, Base
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def wait_for_db():
    retries = 10
    while retries > 0:
        try:
            engine = create_engine(DATABASE_URL)
            engine.connect()
            return engine
        except OperationalError:
            print("Database not ready, retrying...")
            time.sleep(5)
            retries -= 1
    raise Exception("Database not ready after multiple retries")

engine = wait_for_db()
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    consumer.start_consuming()
