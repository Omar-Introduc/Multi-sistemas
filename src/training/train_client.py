import socket
import sys
import os
import cv2
import time

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.common.network import send_image, recv_msg

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5002

def train_directory(directory, label_id, label_name):
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_IP, SERVER_PORT))

        files = os.listdir(directory)
        for f in files:
            path = os.path.join(directory, f)
            img = cv2.imread(path)
            if img is None:
                continue

            print(f"Sending {f} as {label_name}...")
            meta = {
                "type": "data",
                "label_id": label_id,
                "label_name": label_name
            }
            send_image(sock, img, meta)
            resp = recv_msg(sock)
            # print(f"Server response: {resp}")

        # Send train command
        print("Sending train command...")
        meta = {
            "type": "command",
            "cmd": "train"
        }
        # Send a 1x1 dummy image because our protocol expects an image
        # This is a bit hacky but keeps network.py simple.
        import numpy as np
        dummy_img = np.zeros((1,1,3), np.uint8)
        send_image(sock, dummy_img, meta)
        resp = recv_msg(sock)
        print(f"Final response: {resp}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python train_client.py <image_dir> <label_id> <label_name>")
        sys.exit(1)

    directory = sys.argv[1]
    label_id = int(sys.argv[2])
    label_name = sys.argv[3]

    train_directory(directory, label_id, label_name)
