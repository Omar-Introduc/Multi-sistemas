import sys
import os
import cv2
import numpy as np
import time
import json
import datetime

import json
import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.training.model import AIModel

def evaluate_accuracy(data_path, model_path='model.pkl'):
    print(f"Loading model from {model_path}...")
    model = AIModel()

    # Check possible locations for model
    if os.path.exists(model_path):
        model.load(model_path)
    elif os.path.exists(os.path.join('src', 'training', model_path)):
        model.load(os.path.join('src', 'training', model_path))
    else:
        print("Error: Model file not found.")
        return

    if not model.is_trained:
        print("Error: Model is not trained.")
        return

    print("Model loaded. Starting evaluation...")

    correct_total = 0
    total_samples = 0
    class_metrics = {}

    # Iterate through dataset
    for class_name in os.listdir(data_path):
        class_dir = os.path.join(data_path, class_name)
        if os.path.isdir(class_dir):
            print(f"Evaluating class: {class_name}...")
            correct_class = 0
            total_class = 0

            for img_name in os.listdir(class_dir):
                img_path = os.path.join(class_dir, img_name)
                img = cv2.imread(img_path)
                if img is not None:
                    # Predict
                    try:
                        # The model expects raw image data (numpy array)
                        prediction = model.predict(img)

                        if prediction == class_name:
                            correct_class += 1
                            correct_total += 1

                        total_class += 1
                        total_samples += 1
                    except Exception as e:
                        print(f"Error predicting {img_name}: {e}")

            # Class stats
            accuracy = (correct_class / total_class * 100) if total_class > 0 else 0
            class_metrics[class_name] = {
                'correct': correct_class,
                'total': total_class,
                'accuracy': accuracy
            }
            print(f"  -> Accuracy for {class_name}: {accuracy:.2f}% ({correct_class}/{total_class})")

    # Overall stats
    total_accuracy = (correct_total / total_samples * 100) if total_samples > 0 else 0
    print("\n" + "="*30)
    print("EVALUATION RESULTS")
    print("="*30)
    print(f"Total Samples: {total_samples}")
    print(f"Overall Accuracy: {total_accuracy:.2f}%")
    print("-" * 30)
    for cls, metrics in class_metrics.items():
        print(f"{cls}: {metrics['accuracy']:.2f}%")
    print("="*30)

    # Save History
    history_file = 'training_history.json'
    history_entry = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_samples': total_samples,
        'overall_accuracy': total_accuracy,
        'class_metrics': {k: v['accuracy'] for k, v in class_metrics.items()}
    }

    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            pass

    history.append(history_entry)

    with open(history_file, 'w') as f:
        json.dump(history, f, indent=4)
    print(f"Results saved to {history_file}")

if __name__ == "__main__":
    # Assuming run from project root
    dataset_path = "datasets"
    model_file = "src/training/model.pkl" # Default location after training

    if not os.path.exists(model_file):
        # Try local if running from src/training
        model_file = "model.pkl"

    evaluate_accuracy(dataset_path, model_file)
