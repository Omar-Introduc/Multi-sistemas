import kagglehub
import shutil
import os

def setup_dataset():
    print("Downloading dataset from Kaggle...")
    # Download latest version
    path = kagglehub.dataset_download("alessiocorrado99/animals10")
    print("Path to dataset files:", path)

    # Target directory
    base_target = "datasets"
    if not os.path.exists(base_target):
        os.makedirs(base_target)

    # The dataset structure usually is:
    # path/
    #   raw-img/
    #     cat/
    #     dog/
    #     ...
    # We will walk and find the animal folders and move them.

    print("Organizing files...")

    # Map source folder names to our target names (Spanish)
    # Adjust based on actual dataset folder names.
    mappings = {
        "cane": "perro",
        "gatto": "gato",
        "ragno": "araña",
        "gallina": "pollo",
        "scoiattolo": "ardilla",
        "pecora": "oveja",
        "cavallo": "caballo",
        "mucca": "vaca",
        "elefante": "elefante",
        "farfalla": "mariposa"
    }

    # The images are in a subfolder called "raw-img"
    source_base_dir = os.path.join(path, "raw-img")

    for dir_name in os.listdir(source_base_dir):
        lower_name = dir_name.lower()

        # some folders are not animals
        if lower_name in mappings:
            target_name = mappings[lower_name]

            source_dir = os.path.join(source_base_dir, dir_name)
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
