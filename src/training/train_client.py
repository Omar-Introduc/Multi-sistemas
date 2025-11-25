import sys
import os
import json
import time
import cv2
import base64
import numpy as np
import argparse

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketClient

def train_model(data_path, host='127.0.0.1', port=5002, shard_id=0, num_shards=1):
    client = SocketClient(host, port)
    try:
        client.connect()
        print(f"Connected to Training Server. Client Shard: {shard_id+1}/{num_shards}")
        
        dataset = []
        
        if not os.path.exists(data_path):
            print(f"Data path {data_path} does not exist.")
            return

        print("Loading images...")
        all_images = []
        
        # 1. Collect ALL images first
        for class_name in sorted(os.listdir(data_path)): # Sorted for deterministic order
            class_dir = os.path.join(data_path, class_name)
            if os.path.isdir(class_dir):
                for img_name in sorted(os.listdir(class_dir)):
                    img_path = os.path.join(class_dir, img_name)
                    all_images.append((img_path, class_name))
        
        total_images = len(all_images)
        print(f"Found {total_images} total images in dataset.")
        
        # 2. Select only the slice for this shard
        # Logic: Take every Nth image starting from shard_id
        # Example: 3 shards. 
        # Shard 0 takes indices 0, 3, 6...
        # Shard 1 takes indices 1, 4, 7...
        # Shard 2 takes indices 2, 5, 8...
        my_images = all_images[shard_id::num_shards]
        print(f"This client (Shard {shard_id}) will process {len(my_images)} images out of {total_images}.")
        
        # 3. Load and Encode selected images
        for img_path, label in my_images:
            img = cv2.imread(img_path)
            if img is not None:
                _, buf = cv2.imencode('.jpg', img)
                b64 = base64.b64encode(buf).decode('utf-8')
                dataset.append((b64, label))
        
        if not dataset:
            print("No images to send in this shard.")
            return

        print(f"Sending training request with {len(dataset)} images...")
        client.send('TRAIN', {'dataset': dataset})
        
        msg = client.receive()
        if msg:
            print(f"Server Response: {msg.msg_type} - {msg.payload}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Distributed Training Client')
    parser.add_argument('data_path', help='Path to dataset root folder')
    parser.add_argument('--shard_id', type=int, default=0, help='ID of this client (0 to num_shards-1)')
    parser.add_argument('--num_shards', type=int, default=1, help='Total number of clients running in parallel')
    
    args = parser.parse_args()
    
    train_model(args.data_path, shard_id=args.shard_id, num_shards=args.num_shards)
