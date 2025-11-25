import sys
import os
import json
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketClient

def train_model(host='127.0.0.1', port=5002):
    client = SocketClient(host, port)
    try:
        client.connect()
        print("Connected to Training Server.")
        
        # Create dummy dataset
        # List of tuples/lists: [image_data, label]
        # For our mock model, data doesn't matter much, just the structure
        dataset = [
            ([0]*100, "Person"),
            ([0]*100, "Car"),
            ([0]*100, "Dog")
        ]
        
        print("Sending training request...")
        client.send('TRAIN', {'dataset': dataset})
        
        msg = client.receive()
        if msg:
            print(f"Server Response: {msg.msg_type} - {msg.payload}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    train_model()
