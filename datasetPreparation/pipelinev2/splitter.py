import os
from glob import glob
import cv2
from sklearn.model_selection import train_test_split

# Define paths and ratios
dataset_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\raw_balancer_split"
train_ratio, val_ratio, test_ratio = 0.7, 0.2, 0.1

# Function to split images and display counts
def split_and_count_images(class_path, class_name):
    # Gather all images in the current class subdirectory
    all_images = glob(os.path.join(class_path, "*.jpg"))
    if not all_images:
        print(f"No images found in {class_name}")
        return 0, 0, 0  # Return 0 counts if no images are found
    
    # Split images into train, validation, and test sets
    train_images, temp_images = train_test_split(all_images, test_size=(val_ratio + test_ratio))
    val_images, test_images = train_test_split(temp_images, test_size=(test_ratio / (val_ratio + test_ratio)))
    
    # Create directories if they don't exist and move images
    for split, images in zip(['train', 'val', 'test'], [train_images, val_images, test_images]):
        split_path = os.path.join(dataset_path, split, class_name)
        os.makedirs(split_path, exist_ok=True)
        for img_path in images:
            os.rename(img_path, os.path.join(split_path, os.path.basename(img_path)))
    
    # Print class-wise counts
    print(f"{class_name}: Train={len(train_images)}, Val={len(val_images)}, Test={len(test_images)}")
    return len(train_images), len(val_images), len(test_images)

# Initialize total counters
total_train, total_val, total_test = 0, 0, 0

# Get list of all classes and split images
classes = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
for class_name in classes:
    class_path = os.path.join(dataset_path, class_name)
    train_count, val_count, test_count = split_and_count_images(class_path, class_name)
    total_train += train_count
    total_val += val_count
    total_test += test_count

# Print total counts
print("\nTotal Counts:")
print(f"Train: {total_train}, Validation: {total_val}, Test: {total_test}")
