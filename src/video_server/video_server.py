import cv2
import sys
import os
import time
import threading
import json

# Add project root to path to import common modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketServer, send_msg, recv_msg

def load_config():
    try:
        with open('../../config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Config file not found, using defaults")
        return {}

class VideoServer(SocketServer):
    def __init__(self):
        config = load_config().get('video_server', {})
        host = config.get('host', '0.0.0.0')
        port = config.get('port', 5001)
        video_source = config.get('source', 0)
        
        super().__init__(host, port)
        self.video_source = video_source
        self.cap = None
        self.lock = threading.Lock()
        self.current_frame = None
        self.frame_count = 0

    def start_capture(self):
        print(f"Starting capture thread for source: {self.video_source}")
        capture_thread = threading.Thread(target=self._capture_loop)
        capture_thread.daemon = True
        capture_thread.start()

    def _capture_loop(self):
        print(f"Initializing capture in thread...")
        self.cap = cv2.VideoCapture(self.video_source)
        
        if not self.cap.isOpened():
             print(f"Error: Could not open video source {self.video_source} in thread.")
             return

        print(f"Capture opened. Backend: {self.cap.getBackendName()}")
        
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.current_frame = frame
                    self.frame_count += 1
                # If reading from file, limit speed to not consume 100% CPU
                if isinstance(self.video_source, str):
                    time.sleep(1/30) 
            else:
                # If it's a file and we reached the end, loop it
                if isinstance(self.video_source, str) and os.path.exists(self.video_source):
                    print("End of video file, restarting...")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                else:
                    print("Failed to read frame (stream ended or error)")
                    time.sleep(1)
                    # Try to reconnect if it's a stream
                    if not self.cap.isOpened():
                         self.cap.release()
                         self.cap = cv2.VideoCapture(self.video_source)

    def handle_client(self, client_sock):
        print("Video Client Connected")
        try:
            while True:
                # Use recv_msg from common module
                msg = recv_msg(client_sock)
                if not msg:
                    break
                
                if msg.msg_type == 'GET_FRAME':
                    with self.lock:
                        frame = self.current_frame
                    
                    if frame is not None:
                        # Encode frame to JPEG
                        _, buffer = cv2.imencode('.jpg', frame)
                        jpg_as_text = buffer.tobytes()
                        import base64
                        b64_frame = base64.b64encode(jpg_as_text).decode('utf-8')
                        send_msg(client_sock, 'FRAME_RESPONSE', {'frame': b64_frame, 'id': self.frame_count})
                    else:
                        send_msg(client_sock, 'ERROR', {'message': 'No frame available'})
                
        except Exception as e:
            print(f"Error handling video client: {e}")
        finally:
            client_sock.close()

if __name__ == "__main__":
    # Usage: python video_server.py [source]
    # Source from args overrides config
    server = VideoServer()
    
    if len(sys.argv) > 1:
        source = sys.argv[1]
        try:
            source = int(source)
        except ValueError:
            pass
        server.video_source = source

    server.start()
    server.start_capture()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
