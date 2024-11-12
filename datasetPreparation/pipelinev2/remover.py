import os
import random
import cv2
import albumentations as A
from tqdm import tqdm
from glob import glob

# Set the path to your dataset
dataset_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\raw_200"
target_count = 200  # Target number of original images per class

# Delete excess original images if the count is above the target
def balance_original_images(class_path, image_paths):
    original_count = len(image_paths)
    if original_count > target_count:
        # Delete excess original images
        excess_count = original_count - target_count
        images_to_delete = random.sample(image_paths, excess_count)
        for img_path in images_to_delete:
            os.remove(img_path)
        print(f"Deleted {excess_count} excess original images in '{class_path}'")
    elif original_count < target_count:
        print(f"Class '{class_name}' has fewer original images ({original_count}) than target ({target_original_count}).")

# Get list of all classes
classes = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]

for class_name in classes:
    class_path = os.path.join(dataset_path, class_name)

print("Dataset balancing complete.")
