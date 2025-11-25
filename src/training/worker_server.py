import sys
import os
import time
import json
import cv2
import numpy as np
import base64

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.common.socket_comm import SocketServer, send_msg, recv_msg

class WorkerServer(SocketServer):
    def __init__(self, host='0.0.0.0', port=6000):
        super().__init__(host, port)
        # HOG Descriptor initialization (Same as Model)
        self.hog = cv2.HOGDescriptor((64, 128), (16, 16), (8, 8), (8, 8), 9)

    def _extract_features(self, image):
        try:
            resized = cv2.resize(image, (64, 128))
            hist = self.hog.compute(resized)
            return hist.flatten().tolist() # Convert to list for JSON serialization
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None

    def handle_client(self, client_sock):
        print("Master Connected to Worker")
        try:
            while True:
                msg = recv_msg(client_sock)
                if not msg:
                    break
                
                if msg.msg_type == 'PROCESS_TASK':
                    # Payload: {'images': [b64_img1, b64_img2...], 'labels': [...]}
                    images_b64 = msg.payload.get('images', [])
                    labels = msg.payload.get('labels', [])
                    
                    print(f"Worker received batch of {len(images_b64)} images")
                    
                    results = []
                    processed_labels = []
                    
                    for i, b64_img in enumerate(images_b64):
                        try:
                            img_bytes = base64.b64decode(b64_img)
                            nparr = np.frombuffer(img_bytes, np.uint8)
                            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                            
                            features = self._extract_features(img)
                            if features:
                                results.append(features)
                                processed_labels.append(labels[i])
                        except Exception as e:
                            print(f"Error processing image {i}: {e}")
                    
                    # Return results
                    send_msg(client_sock, 'TASK_RESULT', {'features': results, 'labels': processed_labels})
                    
        except Exception as e:
            print(f"Error handling master: {e}")
        finally:
            client_sock.close()

if __name__ == "__main__":
    # Usage: python worker_server.py [port]
    port = 6000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        
    server = WorkerServer(port=port)
    server.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
