import cv2
import sys
import os
import time
import threading
import json

# Add project root to path to import common modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketServer, send_msg

class VideoServer(SocketServer):
    def __init__(self, host='0.0.0.0', port=5001, video_source=0):
        super().__init__(host, port)
        self.video_source = video_source
        self.cap = None
        self.lock = threading.Lock()
        self.current_frame = None
        self.frame_count = 0

    def start_capture(self):
        # Open video source (RTSP URL or Camera ID)
        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            print(f"Error: Could not open video source {self.video_source}")
            return

        print(f"Video capture started on source {self.video_source}")
        capture_thread = threading.Thread(target=self._capture_loop)
        capture_thread.daemon = True
        capture_thread.start()

    def _capture_loop(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.current_frame = frame
                    self.frame_count += 1
            else:
                print("Failed to read frame")
                time.sleep(1)

    def handle_client(self, client_sock):
        print("Video Client Connected")
        try:
            while True:
                msg = self.receive_from_client(client_sock) # Helper needed or use recv_msg directly
                # Since recv_msg is standalone in socket_comm, we need to import it or wrap it.
                # Let's assume we use the standalone recv_msg for now.
                from src.common.socket_comm import recv_msg
                
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
                        # Send frame
                        # We might need a specific message type for binary data or base64 it.
                        # For efficiency, let's send raw bytes if possible, but our SocketMessage uses JSON.
                        # Let's base64 encode for the JSON protocol for now to keep it simple, 
                        # or send a "FRAME_METADATA" then raw bytes.
                        # Given the constraints, let's use base64 in JSON for simplicity unless performance is hit.
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
    # Example usage: python video_server.py <rtsp_url_or_id>
    source = 0
    if len(sys.argv) > 1:
        source = sys.argv[1]
        # Try to convert to int if it's a number (camera index)
        try:
            source = int(source)
        except ValueError:
            pass 

    server = VideoServer(video_source=source)
    server.start()
    server.start_capture()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
