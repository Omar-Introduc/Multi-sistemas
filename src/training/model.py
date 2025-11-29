import cv2
import numpy as np
import os
import pickle
import xgboost as xgb

class AIModel:
    def __init__(self):
        # Using XGBoost as the main model
        self.model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
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

        self.model.fit(train_data, train_labels)
        self.label_map = label_names
        self.trained = True
        print(f"Model trained with {len(images)} images and {len(label_names)} classes.")

    def predict(self, image):
        if not self.trained:
            return "Unknown (Untrained)"

        data = self.prepare_data([image])
        # XGBoost expects a batch, data is already (1, features)

        prediction = self.model.predict(data)

        label_idx = int(prediction[0])
        return self.label_map.get(str(label_idx), "Unknown")

    def save(self, filepath):
        # Save the model and the label map
        # XGBoost can save to json/ubjson
        model_path = filepath + ".json"
        self.model.save_model(model_path)

        with open(filepath + ".labels", 'wb') as f:
            pickle.dump(self.label_map, f)
        print(f"Model saved to {model_path} and labels to {filepath}.labels")

    def load(self, filepath):
        model_path = filepath + ".json"
        if not os.path.exists(model_path):
            print(f"Model file {model_path} not found.")
            # Backward compatibility check for old pickle model or just fail
            return False

        self.model.load_model(model_path)

        if os.path.exists(filepath + ".labels"):
            with open(filepath + ".labels", 'rb') as f:
                self.label_map = pickle.load(f)

        self.trained = True
        print(f"Model loaded from {model_path}")
        return True
