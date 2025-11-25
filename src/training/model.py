import os
import pickle
import time
import cv2
import numpy as np
import math

class AIModel:
    def __init__(self):
        self.model_data = {
            'features': None,
            'labels': None,
            'label_map': None
        }
        self.knn = cv2.ml.KNearest_create()
        self.is_trained = False
        # HOG Descriptor initialization
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

    def _augment_image(self, image):
        """
        Apply random augmentations to an image.
        """
        # Rotation
        angle = np.random.uniform(-15, 15)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(image, rot_mat, (w, h))

        # Flip
        if np.random.rand() > 0.5:
            image = cv2.flip(image, 1) # Horizontal flip

        # Brightness
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hsv = np.array(hsv, dtype=np.float64)
        hsv[:, :, 2] = hsv[:, :, 2] * (0.5 + np.random.uniform())
        hsv[:, :, 2][hsv[:, :, 2] > 255] = 255
        hsv = np.array(hsv, dtype=np.uint8)
        image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return image

    def train(self, dataset_generator):
        """
        Train the model using OpenCV's KNearest.
        dataset_generator: A generator that yields batches of (image_data, label)
        """
        print("Starting training...")
        
        features_list = []
        labels_list = []
        
        for batch in dataset_generator:
            print(f"Processing batch of {len(batch)} samples...")
            for i, (img_data, label) in enumerate(batch):
                if isinstance(img_data, bytes):
                    nparr = np.frombuffer(img_data, np.uint8)
                    img_color = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                elif isinstance(img_data, np.ndarray):
                    img_color = img_data
                else:
                    continue

                if img_color is None:
                    continue

                img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
                features = self._extract_features(img_gray)
                if features is not None:
                    features_list.append(features)
                    labels_list.append(label)

                num_augmentations = 1  # Reduced from 4 to save memory
                for _ in range(num_augmentations):
                    augmented_img_color = self._augment_image(img_color.copy())
                    augmented_img_gray = cv2.cvtColor(augmented_img_color, cv2.COLOR_BGR2GRAY)
                    features = self._extract_features(augmented_img_gray)
                    if features is not None:
                        features_list.append(features)
                        labels_list.append(label)

        unique_labels = sorted(list(set(labels_list)))
        self.model_data['label_map'] = {label: i for i, label in enumerate(unique_labels)}
        self.model_data['features'] = np.array(features_list, dtype=np.float32)
        self.model_data['labels'] = labels_list
        numerical_labels = np.array([self.model_data['label_map'][l] for l in labels_list], dtype=np.float32)

        self.knn.train(self.model_data['features'], cv2.ml.ROW_SAMPLE, numerical_labels)
        self.is_trained = True
        print(f"Training completed. Model is trained with {len(features_list)} feature vectors.")

    def predict(self, image_data, k=3):
        """
        Predict class using the trained KNN model.
        """
        if not self.is_trained:
            return "Unknown"

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

        query_features = query_features.reshape(1, -1).astype(np.float32)
        ret, results, neighbours, dist = self.knn.findNearest(query_features, k)
        
        numerical_label = int(results[0][0])
        
        for label, index in self.model_data['label_map'].items():
            if index == numerical_label:
                return label
        
        return "Unknown"

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump({
                'features': self.model_data['features'],
                'labels': self.model_data['labels'],
                'label_map': self.model_data['label_map']
            }, f)
        print(f"Model data saved to {path}")

    def load(self, path):
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    saved_data = pickle.load(f)

                self.model_data['features'] = saved_data.get('features')
                self.model_data['labels'] = saved_data.get('labels')
                self.model_data['label_map'] = saved_data.get('label_map')

                if self.model_data['features'] is not None and self.model_data['labels'] is not None and self.model_data['label_map'] is not None:
                    numerical_labels = np.array([self.model_data['label_map'][l] for l in self.model_data['labels']], dtype=np.float32)
                    self.knn.train(self.model_data['features'], cv2.ml.ROW_SAMPLE, numerical_labels)
                    self.is_trained = True
                    print(f"Model loaded from {path} and retrained with {len(self.model_data['features'])} samples")
                else:
                    self.model_data = {'features': None, 'labels': None, 'label_map': None}
                    self.is_trained = False
                    print("Loaded invalid or empty model, reset.")
            except (pickle.UnpicklingError, EOFError, KeyError) as e:
                print(f"Error loading model file {path}: {e}. Resetting model.")
                self.model_data = {'features': None, 'labels': None, 'label_map': None}
                self.is_trained = False
        else:
            print(f"Model file {path} not found")
