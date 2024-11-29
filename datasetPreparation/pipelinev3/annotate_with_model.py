import os
from ultralytics import YOLO
import shutil

# Paths
model_path = r"C:\Users\ptplokee\Source\Repos\MiniMart\model\annotationModelv11RF\train\weights\best.pt"
dataset_dir = r"C:\Users\ptplokee\source\hot-storage\miniMartDataset\annotationModel_dataset\preprocessed\datasetv1\train\images"
output_labels_dir = r"C:\Users\ptplokee\source\hot-storage\miniMartDataset\annotationModel_dataset\preprocessed\datasetv1\train\labels"

# Load the trained YOLO model
model = YOLO(model_path)

# Create the output labels directory
os.makedirs(output_labels_dir, exist_ok=True)

# Perform inference and save annotations
for img_file in os.listdir(dataset_dir):
    if not (img_file.endswith(".jpg") or img_file.endswith(".png")):
        continue

    img_path = os.path.join(dataset_dir, img_file)
    results = model(img_path)  # Perform inference

    # Save predictions to YOLO-format labels
    for result in results:
        label_file = os.path.splitext(img_file)[0] + ".txt"
        label_path = os.path.join(output_labels_dir, label_file)
        with open(label_path, "w") as f:
            for box in result.boxes.data.tolist():
                class_id, x_center, y_center, width, height = (
                    int(box[5]),  # Class ID
                    (box[0] + box[2]) / 2,  # x_center
                    (box[1] + box[3]) / 2,  # y_center
                    box[2] - box[0],  # width
                    box[3] - box[1],  # height
                )
                # Normalize coordinates
                img_width, img_height = result.orig_shape[1], result.orig_shape[0]
                x_center /= img_width
                y_center /= img_height
                width /= img_width
                height /= img_height

                # Write to file
                f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

print("Annotation generation complete.")
