import sys
import os
import time
import json
import base64
import threading

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketClient, recv_msg

def load_config():
    try:
        with open('../../config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class VigilanteClient:
    def __init__(self):
        config = load_config().get('vigilante_client', {})
        host = config.get('testing_host', '127.0.0.1')
        port = config.get('testing_port', 5003)
        
        self.host = host
        self.port = port
        self.client = SocketClient(host, port)
        self.running = True
        self.output_dir = 'captured_alerts'
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def start(self):
        try:
            self.client.connect()
            print(f"Connected to Testing Server at {self.host}:{self.port}")
            print("Waiting for alerts...")
            print("-" * 50)
            print(f"{'TYPE':<15} | {'TIME':<10} | {'CAMERA':<15} | {'IMAGE'}")
            print("-" * 50)
            
            while self.running:
                msg = self.client.receive()
                if not msg:
                    print("Disconnected from server.")
                    break
                
                if msg.msg_type == 'ALERT':
                    self._handle_alert(msg.payload)
                
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            self.client.close()

    def _handle_alert(self, payload):
        alert_type = payload.get('type', 'Unknown')
        alert_time = payload.get('time', '??:??')
        camera = payload.get('camera_id', 'Unknown')
        b64_image = payload.get('image')
        
        image_status = "No Image"
        if b64_image:
            try:
                img_bytes = base64.b64decode(b64_image)
                filename = f"{alert_type}_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(img_bytes)
                image_status = f"Saved: {filename}"
            except Exception as e:
                image_status = f"Error saving: {e}"
        
        print(f"{alert_type:<15} | {alert_time:<10} | {camera:<15} | {image_status}")

if __name__ == "__main__":
    # Usage: python vigilante_client.py
    client = VigilanteClient()
    try:
        client.start()
    except KeyboardInterrupt:
        print("\nExiting...")
