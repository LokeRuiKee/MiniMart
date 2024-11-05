import os
import cv2
from preprocess import prepare

# Define input and output directories
input_dir = r"C:\Users\ptplokee\source\mini mart.v6i.yolov11\train\images"
output_dir = r"C:\Users\ptplokee\source\grayscale"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Define preprocessing configuration
preproc_config = {
    "resize": {"enabled": True, "width": 640, "height": 640, "format": "Stretch to"},
    "grayscale": {"enabled": True},
    "contrast": {"enabled": True, "type": "Histogram Equalization"}
}

# Loop through each file in the input directory
for filename in os.listdir(input_dir):
    file_path = os.path.join(input_dir, filename)
    
    # Check if the file is an image
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        # Load the image
        image = cv2.imread(file_path)
        
        # Apply preprocessing
        processed_image, _ = prepare(image, preproc_config)
        
        # Save processed image to output directory
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, processed_image)
        print(f"Processed and saved: {output_path}")

print("Preprocessing completed for all images.")
