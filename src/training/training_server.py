import sys
import os
import json
import threading
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketServer, SocketClient, send_msg, recv_msg
from src.training.model import AIModel
import base64
import numpy as np

def load_config():
    try:
        with open('../../config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class TrainingServer(SocketServer):
    def __init__(self):
        config = load_config().get('training_server', {})
                    # Send the model file to the requester (Testing Server)
                    if os.path.exists(self.model_path):
                        with open(self.model_path, 'rb') as f:
                            model_bytes = f.read()
                        # Send as base64 or raw? 
                        # Let's use a simple approach: read bytes, maybe encode if using JSON wrapper
                        import base64
                        b64_model = base64.b64encode(model_bytes).decode('utf-8')
                        send_msg(client_sock, 'MODEL_DATA', {'model_file': b64_model})
                    else:
                        send_msg(client_sock, 'ERROR', {'message': 'Model not found'})

        except Exception as e:
            print(f"Error handling training client: {e}")
        finally:
            client_sock.close()

if __name__ == "__main__":
    server = TrainingServer()
    server.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
