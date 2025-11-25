import kagglehub
import shutil
import os

def setup_dataset():
    print("Downloading dataset from Kaggle...")
    # Download latest version
    path = kagglehub.dataset_download("muniryadi/cat-vs-rabbit")
    print("Path to dataset files:", path)

    # Target directory
    base_target = "datasets"
    if not os.path.exists(base_target):
        os.makedirs(base_target)

    # The dataset structure usually is:
    # path/
    #   cat/
    #   rabbit/
    # Or sometimes path/train/cat... let's inspect or assume simple structure based on description.
    # We will walk and find folders named 'cat' and 'rabbit' (or similar) and move them.

    print("Organizing files...")
    
    # Map source folder names to our target names (Spanish)
    # Adjust based on actual dataset folder names. 
    # Assuming dataset has "cat" and "rabbit" folders.
    mappings = {
        "cat": "gatos",
        "rabbit": "conejos" 
    }

    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            lower_name = dir_name.lower()
            target_name = None
            
            if "cat" in lower_name:
                target_name = "gatos"
            elif "rabbit" in lower_name:
                target_name = "conejos"
            
            if target_name:
                source_dir = os.path.join(root, dir_name)
                target_dir = os.path.join(base_target, target_name)
                
                print(f"Copying {source_dir} to {target_dir}...")
                
                if os.path.exists(target_dir):
                    print(f"Target {target_dir} exists, merging...")
                else:
                    os.makedirs(target_dir)

                # Copy files
                count = 0
                for img in os.listdir(source_dir):
                    if img.lower().endswith(('.png', '.jpg', '.jpeg')):
                        shutil.copy2(os.path.join(source_dir, img), os.path.join(target_dir, img))
                        count += 1
                print(f"Copied {count} images to {target_name}")

    print("Dataset setup complete.")

if __name__ == "__main__":
    setup_dataset()
