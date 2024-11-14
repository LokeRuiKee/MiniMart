import os
import cv2
import yaml

# Define paths for images and labels
images_dir = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\train\\images"
labels_dir = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\train\\labels"

# Load the data.yaml file to retrieve class names
data_yaml_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\data.yaml"
with open(data_yaml_path, 'r') as file:
    data_yaml = yaml.safe_load(file)
class_dict = {i: name for i, name in enumerate(data_yaml['names'])}

# Load a list of images
image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(".jpg")])

# Function to load YOLO annotations
def load_annotations(label_path, img_width, img_height):
    boxes = []
    if not os.path.exists(label_path):
        print(f"Label file {label_path} not found, skipping annotations for this image.")
        return boxes  # Return an empty list if label file does not exist
    
    with open(label_path, 'r') as f:
        for line in f:
            class_id, x_center, y_center, width, height = map(float, line.strip().split())
            x1 = int((x_center - width / 2) * img_width)
            y1 = int((y_center - height / 2) * img_height)
            x2 = int((x_center + width / 2) * img_width)
            y2 = int((y_center + height / 2) * img_height)
            boxes.append((class_id, x1, y1, x2, y2))
    return boxes

# Function to save YOLO annotations
def save_annotations(label_path, boxes, img_width, img_height):
    with open(label_path, 'w') as f:
        for box in boxes:
            class_id, x1, y1, x2, y2 = box
            x_center = ((x1 + x2) / 2) / img_width
            y_center = ((y1 + y2) / 2) / img_height
            width = (x2 - x1) / img_width
            height = (y2 - y1) / img_height
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

# Function to display image with bounding boxes
def display_image_with_boxes(img, boxes):
    for box in boxes:
        class_id, x1, y1, x2, y2 = box
        class_name = class_dict.get(int(class_id), "Unknown")
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"{class_id}: {class_name}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Main loop to go through images
for image_file in image_files:
    img_path = os.path.join(images_dir, image_file)
    label_path = os.path.join(labels_dir, image_file.replace(".jpg", ".txt"))

    # Load image and annotations
    img = cv2.imread(img_path)
    img_height, img_width = img.shape[:2]
    boxes = load_annotations(label_path, img_width, img_height)

    print(f"\nLoaded image: {image_file}")
    print("Class ID and Name mappings:")
    for class_id, class_name in class_dict.items():
        print(f"{class_id}: {class_name}")

    while True:
        display_img = img.copy()
        display_image_with_boxes(display_img, boxes)

        # Display the image
        cv2.imshow("Annotation Tool", display_img)
        
        # Key bindings for actions
        key = cv2.waitKey(0)
        
        if key == ord('n'):  # Go to next image
            break
        elif key == ord('d'):  # Delete a box
            if boxes:
                print("Press '1' to delete the last box, or select a specific box ID")
                boxes.pop()  # Delete the last box
        elif key == ord('m'):  # Modify class ID of a bounding box
            for i, box in enumerate(boxes):
                class_id, x1, y1, x2, y2 = box
                print(f"{i}: Class ID={int(class_id)}, Coordinates=({x1}, {y1}), ({x2}, {y2})")
            index = int(input("Enter box index to modify: "))
            new_class_id = int(input("Enter new class ID: "))
            if 0 <= index < len(boxes):
                boxes[index] = (new_class_id, *boxes[index][1:])
                print(f"Updated box {index} with new class ID: {new_class_id}")
        elif key == ord('s'):  # Save annotations
            save_annotations(label_path, boxes, img_width, img_height)
            print(f"Annotations saved for {image_file}")

    if key == 27:  # Exit on ESC
        break

cv2.destroyAllWindows()
