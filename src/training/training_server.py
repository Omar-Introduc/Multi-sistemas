import socket
import threading
import sys
import os
import time

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.common.network import recv_image, send_msg
from src.training.model import AIModel

HOST = '0.0.0.0'
PORT = 5002

class TrainingServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(5)
        self.model = AIModel()
        self.training_data = [] # List of (image, label_id)
        self.label_map = {} # label_id -> name
        self.lock = threading.Lock()

    def start(self):
        print(f"Training Server started on {HOST}:{PORT}")
        while True:
            client_sock, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client_sock,)).start()

    def handle_client(self, conn):
        try:
            while True:
                # Receive image + metadata
                # Metadata expected: {"type": "data", "label_id": 1, "label_name": "cat"}
                # OR {"type": "command", "cmd": "train"}
                image, meta = recv_image(conn)

                if meta is None:
                    # Try receiving simple JSON message if image recv failed (might be a command without image)
                    # However, recv_image expects a specific format.
                    # Let's adjust protocol: The client sends a command first, then data.
                    # Or we stick to one protocol.
                    # For simplicity, recv_image handles metadata only if image is attached.
                    # But if we want to send just a "train" command?
                    # Let's check if the connection is closed.
                    break

                msg_type = meta.get("type")

                if msg_type == "data":
                    label_id = meta.get("label_id")
                    label_name = meta.get("label_name")

                    with self.lock:
                        self.training_data.append((image, label_id))
                        self.label_map[str(label_id)] = label_name

                    print(f"Received training image for {label_name}")
                    send_msg(conn, {"status": "received"})

                elif msg_type == "command" and meta.get("cmd") == "train":
                    print("Received train command. Starting training...")
                    self.train_model()
                    send_msg(conn, {"status": "training_complete"})

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            conn.close()

    def train_model(self):
        with self.lock:
            if not self.training_data:
                print("No data to train.")
                return

            images = [x[0] for x in self.training_data]
            labels = [x[1] for x in self.training_data]

            self.model.train(images, labels, self.label_map)

            # Save model
            model_path = os.path.join("models", "model.pkl")
            if not os.path.exists("models"):
                os.makedirs("models")
            self.model.save(model_path)

if __name__ == "__main__":
    server = TrainingServer()
    server.start()
