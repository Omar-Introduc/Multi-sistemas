import sys
import os
import json
import threading
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketServer, send_msg
from src.training.model import AIModel

class TrainingServer(SocketServer):
    def __init__(self, host='0.0.0.0', port=5002, model_path='model.pkl'):
        super().__init__(host, port)
        self.model = AIModel()
        self.model_path = model_path
        # Load existing model if available
        self.model.load(self.model_path)

    def handle_client(self, client_sock):
        print("Training Client Connected")
        try:
            while True:
                # We need to import recv_msg here or make it a static method of a class
                from src.common.socket_comm import recv_msg
                msg = recv_msg(client_sock)
                if not msg:
                    break
                
                print(f"Received request: {msg.msg_type}")
                
                if msg.msg_type == 'TRAIN':
                    # Payload should contain 'data' (list of inputs) and 'labels'
                    data = msg.payload.get('dataset', [])
                    if data:
                        print(f"Received dataset with {len(data)} samples")
                        # Train in a separate thread to not block? 
                        # For now, blocking is fine or we can spawn a training thread.
                        # If we want "Distributed" we might forward this to other nodes.
                        # Here we implement the "Sequential" processing on this node.
                        self.model.train(data)
                        self.model.save(self.model_path)
                        send_msg(client_sock, 'TRAIN_COMPLETE', {'status': 'success'})
                    else:
                        send_msg(client_sock, 'ERROR', {'message': 'Empty dataset'})
                
                elif msg.msg_type == 'GET_MODEL':
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
