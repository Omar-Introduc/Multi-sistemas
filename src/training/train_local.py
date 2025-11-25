import os
import sys
import cv2

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.training.model import AIModel

def main():
    print("Starting local training...")
    # Path is relative to project root, assuming script is run from there
    data_path = "datasets"
    dataset = []

    if not os.path.exists(data_path):
        print(f"Data path {data_path} does not exist.")
        return

    print("Loading images...")

    # Create a generator to load images in batches
    def generate_batches(batch_size=32):
        batch = []
        for class_name in sorted(os.listdir(data_path)):
            class_dir = os.path.join(data_path, class_name)
            if os.path.isdir(class_dir):
                for img_name in sorted(os.listdir(class_dir)):
                    img_path = os.path.join(class_dir, img_name)
                    img = cv2.imread(img_path)
                    if img is not None:
                        batch.append((img, class_name))
                        if len(batch) == batch_size:
                            yield batch
                            batch = []
        if batch:
            yield batch

    model = AIModel()
    # The train method will need to be updated to handle a generator
    model.train(generate_batches())

    # Save the model where the evaluation script expects it
    model_path = "src/training/model.pkl"
    model.save(model_path)
    print(f"Local training complete. Model saved to {os.path.abspath(model_path)}")

if __name__ == "__main__":
    main()
