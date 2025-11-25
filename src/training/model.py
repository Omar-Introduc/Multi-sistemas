import os
import pickle
import time
import cv2
import numpy as np
import math

class AIModel:
    def __init__(self):
        self.model_data = {
            'features': [],
            'labels': []
        }
        self.is_trained = False
        # HOG Descriptor initialization
        # WinSize, BlockSize, BlockStride, CellSize, NBins
        self.hog = cv2.HOGDescriptor((64, 128), (16, 16), (8, 8), (8, 8), 9)

    def _extract_features(self, image):
        """
        Extract HOG features from an image.
        Image should be resized to 64x128 for this HOG config.
        """
        try:
            # Resize to fixed size for HOG
            resized = cv2.resize(image, (64, 128))
            # Compute HOG descriptors
            hist = self.hog.compute(resized)
            return hist.flatten()
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None

    def train(self, dataset):
        """
        Train the model (KNN style: store features).
        dataset: List of tuples (image_data, label)
        image_data: can be raw bytes or numpy array
        """
        print(f"Starting training with {len(dataset)} samples...")
        
        features_list = []
        labels_list = []
        
        for i, (img_data, label) in enumerate(dataset):
            # Convert to numpy array if needed
            if isinstance(img_data, bytes):
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            elif isinstance(img_data, np.ndarray):
                if len(img_data.shape) == 3:
                    img = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)
                else:
                    img = img_data
            else:
                # Assuming list of ints (mock data) - skip or try to convert
                # For real usage, we expect bytes or ndarray
                continue

            if img is None:
                continue

            features = self._extract_features(img)
            if features is not None:
                features_list.append(features)
                labels_list.append(label)
        
        self.model_data['features'] = features_list
        self.model_data['labels'] = labels_list
        self.is_trained = True
        print(f"Training completed. Stored {len(features_list)} feature vectors.")

    def predict(self, image_data, k=3):
        """
        Predict class using KNN.
        """
        if not self.is_trained:
            return "Unknown"
            
        # Prepare input image
        if isinstance(image_data, bytes):
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        elif isinstance(image_data, np.ndarray):
            if len(image_data.shape) == 3:
                img = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
            else:
                img = image_data
        else:
            return "Unknown"

        if img is None:
            return "Unknown"

        query_features = self._extract_features(img)
        if query_features is None:
            return "Unknown"

        # KNN Logic: Find k nearest neighbors
        distances = []
        for i, features in enumerate(self.model_data['features']):
            # Euclidean distance
            dist = np.linalg.norm(query_features - features)
            distances.append((dist, self.model_data['labels'][i]))
        
        # Sort by distance
        distances.sort(key=lambda x: x[0])
        
        # Get top k
        k_nearest = distances[:k]
        
        if not k_nearest:
            return "Unknown"
            
        # Vote
        votes = {}
        for d, label in k_nearest:
            votes[label] = votes.get(label, 0) + 1
            
        # Get winner
        winner = max(votes, key=votes.get)
        
        # Optional: Confidence threshold based on distance?
        # For now, just return winner
        return winner

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.model_data, f)
        print(f"Model saved to {path}")

    def load(self, path):
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    self.model_data = pickle.load(f)
                # Check if valid model
                if isinstance(self.model_data, dict) and self.model_data.get('features'):
                    self.is_trained = True
                    print(f"Model loaded from {path} with {len(self.model_data['features'])} samples")
                else:
                    self.model_data = {'features': [], 'labels': []} # Reset
                    self.is_trained = False
                    print("Loaded invalid or empty model, reset.")
            except (pickle.UnpicklingError, EOFError, KeyError) as e:
                print(f"Error loading model file {path}: {e}. Resetting model.")
                self.model_data = {'features': [], 'labels': []} # Reset
                self.is_trained = False
        else:
            print(f"Model file {path} not found")
