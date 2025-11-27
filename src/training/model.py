import cv2
import numpy as np
import os
import pickle

class AIModel:
    def __init__(self):
        # Using KNN as it is simple and supported by OpenCV
        self.knn = cv2.ml.KNearest_create()
        self.trained = False
        self.label_map = {} # Maps integer labels to string names

    def prepare_data(self, images):
        """
        Flattens images or extracts features.
        For simplicity, we resize to 32x32 and flatten.
        """
        data = []
        for img in images:
            if img is None:
                continue
            # Resize to small fixed size
            resized = cv2.resize(img, (32, 32))
            # Flatten
            flattened = resized.reshape(-1).astype(np.float32)
            data.append(flattened)
        return np.array(data)

    def train(self, images, labels, label_names):
        """
        images: list of numpy arrays
        labels: list of integers
        label_names: dict mapping int to string
        """
        if not images:
            print("No images to train on.")
            return

        train_data = self.prepare_data(images)
        train_labels = np.array(labels, dtype=np.int32)

        self.knn.train(train_data, cv2.ml.ROW_SAMPLE, train_labels)
        self.label_map = label_names
        self.trained = True
        print(f"Model trained with {len(images)} images and {len(label_names)} classes.")

    def predict(self, image):
        if not self.trained:
            return "Unknown (Untrained)"

        data = self.prepare_data([image])
        ret, results, neighbours, dist = self.knn.findNearest(data, k=3)

        label_idx = int(results[0][0])
        return self.label_map.get(str(label_idx), "Unknown")

    def save(self, filepath):
        # OpenCV's save only saves the model structure/weights
        # We also need to save the label map.
        self.knn.save(filepath)
        with open(filepath + ".labels", 'wb') as f:
            pickle.dump(self.label_map, f)
        print(f"Model saved to {filepath}")

    def load(self, filepath):
        if not os.path.exists(filepath):
            print(f"Model file {filepath} not found.")
            return False

        self.knn = cv2.ml.KNearest_load(filepath)

        if os.path.exists(filepath + ".labels"):
            with open(filepath + ".labels", 'rb') as f:
                self.label_map = pickle.load(f)

        self.trained = True
        print(f"Model loaded from {filepath}")
        return True
