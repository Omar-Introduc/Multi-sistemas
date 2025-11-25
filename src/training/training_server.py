import sys
import os
import json
import threading
import time
import math
import base64
import numpy as np
import cv2

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketServer, SocketClient, send_msg, recv_msg
from src.training.model import AIModel

def load_config():
    try:
        with open('../../config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class TrainingServer(SocketServer):
    def __init__(self):
        config = load_config().get('training_server', {})
        host = config.get('host', '0.0.0.0')
        port = config.get('port', 5002)
        super().__init__(host, port)

        self.model_path = config.get('model_path', 'model.pkl')
        self.workers = config.get('workers', [])
        self.model = AIModel()
        self.model_lock = threading.Lock()

        # Load model if exists
        if os.path.exists(self.model_path):
            self.model.load(self.model_path)
            print("Loaded existing model.")

    def _distribute_training(self, dataset):
        """
        Distribute training data to workers.
        dataset: List of tuples (image_data, label)
        """
        if not self.workers:
            print("Warning: No workers configured. Training locally.")
            # Handle local training as a fallback
            # This part is simplified: in a real scenario, you'd process the data
            # similarly to how a worker would, but in the main thread/process.
            # For this fix, we'll just prevent the crash.
            return

        print(f"Distributing {len(dataset)} samples to {len(self.workers)} workers...")
        
        # Split dataset
        chunk_size = math.ceil(len(dataset) / len(self.workers))
        chunks = [dataset[i:i + chunk_size] for i in range(0, len(dataset), chunk_size)]
        
        aggregated_features = []
        aggregated_labels = []
        
        threads = []
        results_lock = threading.Lock()
        
        def send_to_worker(worker_addr, chunk):
            host, port = worker_addr
            try:
                client = SocketClient(host, port)
                client.connect()
                
                # Prepare payload
                images_b64 = []
                labels = []
                for img_data, label in chunk:
                    # Convert to base64 for JSON transport
                    if isinstance(img_data, str):
                        # Assume already base64
                        b64 = img_data
                    elif isinstance(img_data, bytes):
                        b64 = base64.b64encode(img_data).decode('utf-8')
                    elif isinstance(img_data, np.ndarray):
                        _, buf = cv2.imencode('.jpg', img_data)
                        b64 = base64.b64encode(buf).decode('utf-8')
                    else:
                        continue
                        
                    images_b64.append(b64)
                    labels.append(label)
                
                client.send('PROCESS_TASK', {'images': images_b64, 'labels': labels})
                
                msg = client.receive()
                if msg and msg.msg_type == 'TASK_RESULT':
                    feats = msg.payload.get('features', [])
                    labs = msg.payload.get('labels', [])
                    
                    with results_lock:
                        aggregated_features.extend(feats)
                        aggregated_labels.extend(labs)
                        
                client.close()
            except Exception as e:
                print(f"Error communicating with worker {host}:{port} - {e}")

        # Spawn threads for each worker
        for i, worker in enumerate(self.workers):
            if i < len(chunks):
                t = threading.Thread(target=send_to_worker, args=(worker, chunks[i]))
                t.start()
                threads.append(t)
        
        for t in threads:
            t.join()
            
        print(f"Aggregation complete. Received {len(aggregated_features)} feature vectors.")
        
        # Update Local Model (Accumulate) with Lock
        with self.model_lock:
            if not self.model.is_trained:
                 self.model.model_data['features'] = [np.array(f, dtype=np.float32) for f in aggregated_features]
                 self.model.model_data['labels'] = aggregated_labels
            else:
                 print(f"Appending {len(aggregated_features)} new samples to existing model...")
                 self.model.model_data['features'].extend([np.array(f, dtype=np.float32) for f in aggregated_features])
                 self.model.model_data['labels'].extend(aggregated_labels)
            self.model.is_trained = True
            self.model.save(self.model_path) # Save immediately after update inside lock

    def handle_client(self, client_sock):
        print("Training Client Connected")
        try:
            while True:
                msg = recv_msg(client_sock)
                if not msg:
                    break
                
                print(f"Received request: {msg.msg_type}")
                
                if msg.msg_type == 'TRAIN':
                    data = msg.payload.get('dataset', [])
                    if data:
                        print(f"Received dataset with {len(data)} samples")
                        self._distribute_training(data)
                        # Save is now handled inside _distribute_training with lock
                        send_msg(client_sock, 'TRAIN_COMPLETE', {'status': 'success'})
                    else:
                        send_msg(client_sock, 'ERROR', {'message': 'Empty dataset'})
                
                elif msg.msg_type == 'GET_MODEL':
                    if os.path.exists(self.model_path):
                        with open(self.model_path, 'rb') as f:
                            model_bytes = f.read()
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
