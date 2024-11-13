import os
from glob import glob
import shutil
from sklearn.model_selection import train_test_split

# Define source paths for images and labels
images_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\backup\\images"
labels_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\backup\\labels"

# Define the base output directory
output_base_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1"
train_ratio, val_ratio, test_ratio = 0.7, 0.2, 0.1

# Create train, val, test directories for images and labels
for split in ['train', 'val', 'test']:
    os.makedirs(os.path.join(output_base_path, split, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_base_path, split, "labels"), exist_ok=True)

# Gather all images
all_images = glob(os.path.join(images_path, "*.jpg"))

# Split images into train, validation, and test sets
train_images, temp_images = train_test_split(all_images, test_size=(val_ratio + test_ratio))
val_images, test_images = train_test_split(temp_images, test_size=(test_ratio / (val_ratio + test_ratio)))

# Function to move images and labels
def move_files(image_paths, split):
    for img_path in image_paths:
        # Define the destination paths for images and labels
        dest_image_path = os.path.join(output_base_path, split, "images", os.path.basename(img_path))
        dest_label_path = os.path.join(output_base_path, split, "labels", os.path.basename(img_path).replace(".jpg", ".txt"))
        
        # Move the image
        shutil.move(img_path, dest_image_path)
        
        # Check for the corresponding label and move it if it exists
        label_path = os.path.join(labels_path, os.path.basename(img_path).replace(".jpg", ".txt"))
        if os.path.exists(label_path):
            shutil.move(label_path, dest_label_path)

# Move the files into the respective directories
move_files(train_images, "train")
move_files(val_images, "val")
move_files(test_images, "test")

# Print completion message
print("Data split and organization into train, val, test completed successfully.")
