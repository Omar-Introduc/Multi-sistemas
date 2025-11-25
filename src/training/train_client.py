import sys
import os
import json
import time
import cv2
import base64
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketClient

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, filename))
        if img is not None:
            images.append(img)
    return images

def train_model(data_path, host='127.0.0.1', port=5002):
    client = SocketClient(host, port)
    try:
        client.connect()
        print("Connected to Training Server.")
        
        dataset = []
        
        # Structure: data_path/class_name/image.jpg
        if not os.path.exists(data_path):
            print(f"Data path {data_path} does not exist.")
            return

        print("Loading images...")
        for class_name in os.listdir(data_path):
            class_dir = os.path.join(data_path, class_name)
            if os.path.isdir(class_dir):
                images_in_class = []
                # First pass: collect valid images
                for img_name in os.listdir(class_dir):
                    img_path = os.path.join(class_dir, img_name)
                    img = cv2.imread(img_path)
                    if img is not None:
                        images_in_class.append((img, class_name))
                
                # Check condition: > 2 images
                if len(images_in_class) > 2:
                    print(f"Loading class: {class_name} ({len(images_in_class)} images)")
                    for img, label in images_in_class:
                        _, buf = cv2.imencode('.jpg', img)
                        b64 = base64.b64encode(buf).decode('utf-8')
                        dataset.append((b64, label))
                else:
                    print(f"Skipping class: {class_name} (Found {len(images_in_class)} images, required > 2)")
        
        print(f"Sending training request with {len(dataset)} images...")
        # Note: We send (b64_string, label) tuples. 
        # The server expects this structure in the 'dataset' key.
        # However, our server logic might need adjustment if it expects raw bytes or ndarray directly in memory.
        # But since we use JSON for transport, we MUST use base64 strings here.
        # The server's _distribute_training needs to handle this.
        # Wait, _distribute_training in TrainingServer iterates and checks type.
        # If it's bytes (b64 string is bytes/str), it might try to encode AGAIN.
        # Let's check TrainingServer logic.
        # It checks: if isinstance(img_data, bytes) -> b64encode.
        # If we send b64 string (str), it might skip?
        # Actually, let's send raw bytes of the image file if possible?
        # JSON can't hold raw bytes.
        # So we send b64 strings.
        # In TrainingServer:
        # for img_data, label in chunk:
        #    if isinstance(img_data, bytes): ...
        # We should ensure TrainingServer handles already-b64 strings or decode them?
        # Actually, the TrainingServer is designed to PREPARE payload for Worker.
        # It expects "image_data" to be something it can encode.
        # If we send b64 strings, we should probably decode them to bytes before sending to TrainingServer?
        # No, that's inefficient.
        # Let's just send the b64 strings and let TrainingServer pass them through?
        # TrainingServer Logic:
        # if isinstance(img_data, bytes): b64 = base64.b64encode(img_data).decode('utf-8')
        # If we send a string, it falls through to "continue".
        # We need to fix TrainingServer or send bytes here.
        # Let's send raw bytes of the JPEG here (but we can't put raw bytes in JSON payload of SocketMessage).
        # Ah, SocketMessage uses JSON.dumps. So we MUST use strings (b64) here.
        # So 'dataset' will contain strings.
        # We need to update TrainingServer to handle strings (assume they are b64).
        
        client.send('TRAIN', {'dataset': dataset})
        
        msg = client.receive()
        if msg:
            print(f"Server Response: {msg.msg_type} - {msg.payload}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Usage: python train_client.py <data_folder>
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
        train_model(data_path)
    else:
        print("Usage: python train_client.py <path_to_dataset_folder>")
        print("Dataset structure: folder/class_name/image.jpg")
