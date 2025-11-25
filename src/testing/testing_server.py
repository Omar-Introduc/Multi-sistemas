import sys
import os
import time
import threading
import json
import base64
import cv2
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketServer, SocketClient, send_msg, recv_msg
from src.training.model import AIModel

class TestingServer(SocketServer):
    def __init__(self, host='0.0.0.0', port=5003, video_host='127.0.0.1', video_port=5001, training_host='127.0.0.1', training_port=5002):
        super().__init__(host, port)
        self.video_host = video_host
        self.video_port = video_port
        self.training_host = training_host
        self.training_port = training_port
        
        self.model = AIModel()
        self.model_path = 'downloaded_model.pkl'
        
        self.video_client = None
        self.training_client = None
        
        self.vigilantes = [] # List of connected vigilante clients

    def start(self):
        super().start()
        # Start background thread to fetch frames and process
        process_thread = threading.Thread(target=self._process_loop)
        process_thread.daemon = True
        process_thread.start()
        
        # Start background thread to update model periodically
        update_thread = threading.Thread(target=self._model_update_loop)
        update_thread.daemon = True
        update_thread.start()

    def _model_update_loop(self):
        while self.running:
            try:
                # Connect to Training Server to get model
                client = SocketClient(self.training_host, self.training_port)
                client.connect()
                client.send('GET_MODEL', {})
                msg = client.receive()
                if msg and msg.msg_type == 'MODEL_DATA':
                    b64_model = msg.payload.get('model_file')
                    if b64_model:
                        model_bytes = base64.b64decode(b64_model)
                        with open(self.model_path, 'wb') as f:
                            f.write(model_bytes)
                        self.model.load(self.model_path)
                        print("Model updated successfully")
                client.close()
            except Exception as e:
                print(f"Error updating model: {e}")
            
            time.sleep(60) # Check every minute

    def _process_loop(self):
        # Connect to Video Server
        while self.running:
            try:
                if not self.video_client:
                    self.video_client = SocketClient(self.video_host, self.video_port)
                    self.video_client.connect()
                
                # Request Frame
                self.video_client.send('GET_FRAME', {})
                msg = self.video_client.receive()
                
                if msg and msg.msg_type == 'FRAME_RESPONSE':
                    b64_frame = msg.payload.get('frame')
                    frame_id = msg.payload.get('id')
                    
                    if b64_frame:
                        # Decode image
                        img_bytes = base64.b64decode(b64_frame)
                        nparr = np.frombuffer(img_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        # Inference
                        if self.model.is_trained:
                            prediction = self.model.predict(frame)
                            print(f"Frame {frame_id}: Detected {prediction}")
                            
                            # If interesting detection (not "Unknown" or specific target), alert
                            if prediction != "Unknown":
                                self._broadcast_alert(prediction, frame_id, b64_frame)
                        else:
                            print("Model not trained yet, skipping inference")
                
                time.sleep(0.1) # FPS control
                
            except Exception as e:
                print(f"Error in process loop: {e}")
                if self.video_client:
                    self.video_client.close()
                    self.video_client = None
                time.sleep(2)

    def _broadcast_alert(self, detection, frame_id, b64_image):
        alert_data = {
            'type': detection,
            'time': time.strftime('%H:%M:%S'),
            'date': time.strftime('%d/%m/%Y'),
            'camera_id': self.video_host, # Simplified
            'image': b64_image
        }
        
        # Send to all connected Vigilantes
        # We need to manage the list of clients safely
        # The parent SocketServer adds clients to self.clients
        # We can iterate over them.
        # Note: self.clients contains raw sockets.
        
        disconnected = []
        for client_sock in self.clients:
            try:
                send_msg(client_sock, 'ALERT', alert_data)
            except:
                disconnected.append(client_sock)
        
        for d in disconnected:
            if d in self.clients:
                self.clients.remove(d)

    def handle_client(self, client_sock):
        # Vigilante connected
        print("Vigilante Connected")
        # Keep connection open for push notifications
        # We don't need to read much, maybe just a heartbeat or initial config
        try:
            while True:
                msg = recv_msg(client_sock)
                if not msg:
                    break
        except:
            pass
        finally:
            client_sock.close()

if __name__ == "__main__":
    # Usage: python testing_server.py [video_host] [video_port] [training_host] [training_port]
    server = TestingServer()
    server.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
