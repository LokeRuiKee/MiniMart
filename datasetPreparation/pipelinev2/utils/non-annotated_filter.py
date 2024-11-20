import os
import shutil

# Define paths for images, labels, and the destination for images without labels
images_dir = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\images"
labels_dir = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\labels"
unlabeled_images_dir = "C:\\Users\\ptplokee\\source\\miniMartDataset\\unlabeled_images"

# Ensure the destination directory exists
os.makedirs(unlabeled_images_dir, exist_ok=True)

# Count of images moved
moved_count = 0

# Scan images directory
for image_file in os.listdir(images_dir):
    if image_file.endswith(".jpg"):
        # Check for corresponding .txt file in labels directory
        label_file = image_file.replace(".jpg", ".txt")
        label_path = os.path.join(labels_dir, label_file)
        
        # If label file does not exist, move image to the unlabeled_images_dir
        if not os.path.exists(label_path):
            image_path = os.path.join(images_dir, image_file)
            dest_path = os.path.join(unlabeled_images_dir, image_file)
            shutil.move(image_path, dest_path)
            moved_count += 1
            print(f"Moved {image_file} to {unlabeled_images_dir}")

print(f"\nTotal images moved for manual annotation: {moved_count}")
