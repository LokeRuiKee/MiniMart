import os
import cv2
import numpy as np
from glob import glob
from tqdm import tqdm

# Set the path to your dataset and output directories
dataset_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\raw_difference20"
output_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\filtered_for_annotation"
target_count = 24  # Target number of images to select per class
diff_threshold = 50  # Minimum difference threshold for selecting images

def get_classes(dataset_path):
    """Get list of all classes (subdirectories) in the dataset."""
    return [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]

def filter_images_for_annotation(input_path, output_path, target_count, diff_threshold):
    """
    Filter images based on a difference threshold and save the top target_count images.
    """
    os.makedirs(output_path, exist_ok=True)
    image_paths = sorted(glob(os.path.join(input_path, "*.jpg")))  # Ensure images are sorted by name

    selected_images = []  # To store (image_path, difference_score)
    prev_image = None

    for image_path in image_paths:
        # Read the image and convert it to grayscale
        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Compare images only if prev_image is not None
        if prev_image is not None:
            # Resize gray_image to the size of prev_image
            gray_image_resized = cv2.resize(gray_image, (prev_image.shape[1], prev_image.shape[0]))

            # Compute difference from the previous image
            diff_score = np.mean(cv2.absdiff(prev_image, gray_image_resized))
            if diff_score > diff_threshold:
                selected_images.append((image_path, diff_score))
        else:
            # First image, no comparison
            selected_images.append((image_path, float('inf')))  # Assign a high score to the first image

        prev_image = gray_image  # Update the previous image for the next iteration

    # Sort selected images by difference score in descending order
    selected_images = sorted(selected_images, key=lambda x: x[1], reverse=True)[:target_count]

    # Save the selected images in order of their original sequence
    for i, (img_path, _) in enumerate(selected_images):
        image = cv2.imread(img_path)
        output_img_path = os.path.join(output_path, f"{i}.jpg")
        cv2.imwrite(output_img_path, image)
        print(f"Saved {img_path} as {output_img_path}")

def process_classes(dataset_path, output_path, target_count, diff_threshold):
    """
    Process each class by filtering images for annotation based on the threshold.
    """
    # Get list of all classes
    classes = get_classes(dataset_path)

    for class_name in classes:
        class_path = os.path.join(dataset_path, class_name)

        # Step 1: Filter and select images based on the difference threshold
        class_output_path = os.path.join(output_path, class_name)
        filter_images_for_annotation(class_path, class_output_path, target_count, diff_threshold)

    print("Dataset filtering complete.")

# Run the processing
process_classes(dataset_path, output_path, target_count, diff_threshold)
