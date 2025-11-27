import socket
import threading
import sys
import os
import time
import datetime
import cv2
import json
import struct

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.common.network import recv_image, send_msg
from src.training.model import AIModel

HOST = '0.0.0.0'
PORT = 5003

class TestingServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(5)

        self.model = AIModel()
        self.load_model()

        self.logs = []
        self.logs_lock = threading.Lock()

        self.watchmen = []
        self.watchmen_lock = threading.Lock()

    def log_debug(self, msg):
        print(f"[SERVER] {msg}", flush=True)

    def load_model(self):
        model_path = os.path.join("models", "model.pkl")
        if self.model.load(model_path):
            self.log_debug("Model loaded successfully.")
        else:
            self.log_debug("Warning: Model could not be loaded.")

    def start(self):
        self.log_debug(f"Testing Server started on {HOST}:{PORT}")
        while True:
            client_sock, addr = self.server_socket.accept()
            self.log_debug(f"Client connected: {addr}")
            threading.Thread(target=self.handle_client, args=(client_sock, addr)).start()

    def handle_client(self, conn, addr):
        try:
            while True:
                # Read first chunk length
                raw_len = self.recvall(conn, 4)
                if not raw_len:
                    self.log_debug(f"Client {addr} disconnected (EOF on len).")
                    break
                length = struct.unpack('>I', raw_len)[0]

                # Read first chunk (Metadata or Message)
                data = self.recvall(conn, length)
                if not data:
                    self.log_debug(f"Client {addr} disconnected (EOF on data).")
                    break

                msg = json.loads(data.decode('utf-8'))
                msg_type = msg.get("type")

                if msg_type == "frame":
                    # Read image size
                    raw_img_len = self.recvall(conn, 4)
                    if not raw_img_len:
                        self.log_debug(f"Client {addr} disconnected (EOF on img len).")
                        break
                    img_len = struct.unpack('>I', raw_img_len)[0]

                    img_bytes = self.recvall(conn, img_len)
                    if not img_bytes:
                        self.log_debug(f"Client {addr} disconnected (EOF on img data).")
                        break

                    nparr = np.frombuffer(img_bytes, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    self.process_frame(image, msg)

                elif msg_type == "watchman_connect":
                    self.log_debug(f"Watchman connected: {addr}")
                    with self.watchmen_lock:
                        self.watchmen.append(conn)
                    with self.logs_lock:
                         send_msg(conn, {"type": "log_update", "logs": self.logs})
                    self.wait_for_close(conn)
                    return

        except Exception as e:
            self.log_debug(f"Error handling client {addr}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()
            with self.watchmen_lock:
                if conn in self.watchmen:
                    self.watchmen.remove(conn)

    def wait_for_close(self, sock):
        try:
            while True:
                d = sock.recv(1024)
                if not d:
                    break
        except:
            pass

    def recvall(self, sock, n):
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def process_frame(self, image, meta):
        label = self.model.predict(image)
        self.log_debug(f"Processing frame from camera {meta.get('camera_id')}: Predicted {label}")

        if label != "Unknown" and label != "Unknown (Untrained)":
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_debug(f"Detected {label} at {timestamp}")

            filename = f"{label}_{int(time.time())}.jpg"
            filepath = os.path.join("logs", filename)
            if not os.path.exists("logs"):
                os.makedirs("logs")
            cv2.imwrite(filepath, image)

            log_entry = {
                "type": label,
                "photo": filepath,
                "date": timestamp.split()[0],
                "time": timestamp.split()[1],
                "camera_id": meta.get("camera_id")
            }

            with self.logs_lock:
                self.logs.append(log_entry)

            self.notify_watchmen(log_entry)

    def notify_watchmen(self, log_entry):
        msg = {"type": "new_detection", "log": log_entry}
        with self.watchmen_lock:
            for w in self.watchmen:
                try:
                    send_msg(w, msg)
                except:
                    pass

if __name__ == "__main__":
    import numpy as np
    server = TestingServer()
    server.start()
