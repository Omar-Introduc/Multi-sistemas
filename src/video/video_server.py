import cv2
import socket
import sys
import os
import time
import struct
import json
import numpy as np

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.common.network import send_image

TEST_SERVER_IP = '127.0.0.1'
TEST_SERVER_PORT = 5003

class VideoServer:
    def __init__(self, camera_id=0, video_source=0):
        self.camera_id = camera_id
        self.video_source = video_source
        self.running = False

    def log_debug(self, msg):
        print(f"[VIDEO {self.camera_id}] {msg}", flush=True)

    def start(self):
        self.log_debug(f"Starting Video Server (Camera {self.camera_id})...")

        is_image = False
        if isinstance(self.video_source, str) and (self.video_source.endswith('.jpg') or self.video_source.endswith('.png')):
            is_image = True

        if not is_image:
            cap = cv2.VideoCapture(self.video_source)
            if not cap.isOpened():
                self.log_debug(f"Cannot open video source {self.video_source}")
                return

        self.running = True

        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((TEST_SERVER_IP, TEST_SERVER_PORT))
                self.log_debug(f"Connected to Test Server at {TEST_SERVER_IP}:{TEST_SERVER_PORT}")

                while self.running:
                    if is_image:
                        frame = cv2.imread(self.video_source)
                        if frame is None:
                            self.log_debug("Could not read image file.")
                            self.running = False
                            break
                    else:
                        ret, frame = cap.read()
                        if not ret:
                            self.log_debug("End of video stream.")
                            self.running = False
                            break

                    meta = {
                        "type": "frame",
                        "camera_id": self.camera_id,
                        "timestamp": time.time()
                    }

                    try:
                        self.log_debug(f"Sending frame... {frame.shape}")
                        send_image(sock, frame, meta)
                        time.sleep(0.5)
                    except Exception as e:
                        self.log_debug(f"Connection lost: {e}")
                        break

                sock.close()
                if self.running:
                    self.log_debug("Reconnecting in 2 seconds...")
                    time.sleep(2)

            except Exception as e:
                self.log_debug(f"Could not connect: {e}. Retrying in 2 seconds...")
                time.sleep(2)

        if not is_image:
            cap.release()

if __name__ == "__main__":
    src = 0
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Try to convert to int (for webcam index), otherwise keep as string (file path)
        try:
            src = int(arg)
        except ValueError:
            src = arg

    server = VideoServer(camera_id=1, video_source=src)
    server.start()
