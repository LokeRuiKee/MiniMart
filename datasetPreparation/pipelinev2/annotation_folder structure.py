import os
import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import data_configv2 as dconfig

# Define input and output directories for images and annotations
input_folder = Path(dconfig.INPUT_ANNOTATION_DATA_DIRECTORY)
output_base_folder = Path(dconfig.OUTPUT_ANNOTATION_DATA_DIRECTORY) / "dataset"
images_folder = output_base_folder / "images"
labels_folder = output_base_folder / "labels"
images_folder.mkdir(parents=True, exist_ok=True)
labels_folder.mkdir(parents=True, exist_ok=True)

# Load the trained YOLOv8 model
model = YOLO(dconfig.MODEL_PATH)

# Define confidence threshold for detections
CONFIDENCE_THRESHOLD = dconfig.CONFIDENCE_THRESHOLD

def run_inference_on_image(image: np.ndarray):
    """Run inference on an image and return detection results."""
    return model.predict(image, conf=CONFIDENCE_THRESHOLD)[0]

def save_yolo_annotation(label_path, class_id, x_center, y_center, width, height):
    """Save a single detection in YOLO annotation format."""
    with open(label_path, 'a') as f:
        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def process_image_for_annotations(image_path: Path):
    """Process a single image to generate YOLO annotations."""
    # Read the image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Warning: Couldn't open {image_path}. Skipping...")
        return

    # Run inference on the image
    results = run_inference_on_image(image)

    # Copy the image to the images folder
    output_image_path = images_folder / image_path.name
    cv2.imwrite(str(output_image_path), image)

    # Prepare output path for annotations
    label_path = labels_folder / f"{image_path.stem}.txt"
    if label_path.exists():
        os.remove(label_path)  # Clear previous annotations

    # Process each detection and save as YOLO annotations
    img_height, img_width = image.shape[:2]
    for box in results.boxes:
        class_id = int(box.cls)
        confidence = float(box.conf)

        if confidence >= CONFIDENCE_THRESHOLD:
            # Use `xyxy` to get bounding box in [x1, y1, x2, y2] format
            x1, y1, x2, y2 = box.xyxy[0]

            # Calculate YOLO format (normalized) coordinates
            x_center = ((x1 + x2) / 2) / img_width
            y_center = ((y1 + y2) / 2) / img_height
            width = (x2 - x1) / img_width
            height = (y2 - y1) / img_height

            # Save the annotation
            save_yolo_annotation(label_path, class_id, x_center, y_center, width, height)

    print(f"Processed and saved annotations for: {image_path.name}")

# Loop through each image in the input directory
for image_path in input_folder.rglob('*.[pj][np]g'):
    process_image_for_annotations(image_path)

print("Annotation generation completed for all images.")
