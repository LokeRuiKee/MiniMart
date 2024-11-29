import os
import json
import uuid

def yolo_to_label_studio(yolo_file, image_path, image_width, image_height, class_map, model_version="one", score=0.5):
    """
    Convert YOLO format annotations to Label Studio format.
    
    Args:
    - yolo_file: Path to the YOLO annotation file.
    - image_path: Path to the corresponding image (for Label Studio).
    - image_width: Width of the image in pixels.
    - image_height: Height of the image in pixels.
    - class_map: A dictionary mapping class IDs to their names.
    - model_version: Version of the model producing the predictions.
    - score: Confidence score for the predictions.
    
    Returns:
    - Dictionary in Label Studio format.
    """
    label_studio_data = {
        "data": {
            "image": image_path
        },
        "predictions": [
            {
                "model_version": model_version,
                "score": score,
                "result": [],
            }
        ]
    }

    # Read YOLO annotations
    with open(yolo_file, 'r') as file:
        for line in file:
            # Parse the YOLO format line
            class_id, x_center, y_center, box_width, box_height = map(float, line.strip().split())
            
            # Convert YOLO coordinates to pixel values
            x_min = (x_center - box_width / 2) * image_width
            y_min = (y_center - box_height / 2) * image_height
            width = box_width * image_width
            height = box_height * image_height
            
            # Convert coordinates to percentage for Label Studio
            x = (x_min / image_width) * 100
            y = (y_min / image_height) * 100
            width_percent = (width / image_width) * 100
            height_percent = (height / image_height) * 100
            
            # Add the bounding box to the result
            label_studio_data["predictions"][0]["result"].append({
                "original_width": image_width,
                "original_height": image_height,
                "image_rotation": 0,
                "value": {
                    "x": x,
                    "y": y,
                    "width": width_percent,
                    "height": height_percent,
                    "rotation": 0,
                    "rectanglelabels": [class_map[int(class_id)]]
                },
                "id": str(uuid.uuid4())[:8],
                "from_name": "label",
                "to_name": "image",
                "type": "rectanglelabels",
            })
    
    return label_studio_data

def convert_directory(yolo_dir, image_dir, output_json_path, image_width, image_height, class_map):
    """
    Convert all YOLO annotations in a directory to Label Studio format.
    
    Args:
    - yolo_dir: Path to the directory containing YOLO label files.
    - image_dir: Path to the directory containing images.
    - output_json_path: Path to save the Label Studio annotations JSON.
    - image_width: Width of the images in pixels.
    - image_height: Height of the images in pixels.
    - class_map: A dictionary mapping class IDs to their names.
    """
    yolo_files = [f for f in os.listdir(yolo_dir) if f.endswith('.txt')]
    all_annotations = []

    for yolo_file in yolo_files:
        image_file = os.path.splitext(yolo_file)[0] + ".jpg"  # Assuming images are .jpg
        image_path = f"http://localhost:8081/{image_file}"  # Image URL for Label Studio
        
        annotation = yolo_to_label_studio(
            yolo_file=os.path.join(yolo_dir, yolo_file),
            image_path=image_path,
            image_width=image_width,
            image_height=image_height,
            class_map=class_map
        )
        all_annotations.append(annotation)

    # Save all annotations to a JSON file
    with open(output_json_path, 'w') as out_file:
        json.dump(all_annotations, out_file, indent=2)

# Define the class map matching your label interface
class_map = {
    0: "biskclub_choc",
    1: "biskclub_orange",
    2: "biskclub_pineapple",
    3: "biskclub_strawberry",
    4: "chipsmore_mini_doublechoc",
    5: "chipsmore_mini_hazelnut",
    6: "chipsmore_mini_ori",
    7: "gery_cheese_crackers",
    8: "hwatai_banana",
    9: "hwatai_blueberry",
    10: "hwatai_choc",
    11: "hwatai_luxury_chips",
    12: "hwatai_waffler",
    13: "julies_golden",
    14: "luxury_chia",
    15: "luxury_ori",
    16: "malkist_bbq_crackers",
    17: "malkist_belgian",
    18: "malkist_cream_crackers",
    19: "malkist_sweet",
    20: "muchys_blueberry_tart",
    21: "muchys_choc_sandwhich_cookie",
    22: "muchys_strawberry_tart",
    23: "muchys_vanilla_sandwhich_cookie",
    24: "munchys_choc_crackers",
    25: "munchys_dark_cookie",
    26: "munchys_muzic",
    27: "munchys_ori_cookie",
    28: "munchys_white_crackers",
    29: "tiger_ori",
    30: "tiger_susu"
}

# Paths and parameters
yolo_dir = "C:/Users/ptplokee/source/hot-storage/miniMartDataset/annotationModel_dataset/preprocessed/datasetv1/train/labels"
image_dir = "C:/Users/ptplokee/source/hot-storage/miniMartDataset/annotationModel_dataset/preprocessed/datasetv1/train/images"
output_json_path = "./datasetPreparation/label-studio/output_annotations.json"
image_width = 640  # Width of your images

image_height = 640  # Height of your images

convert_directory(yolo_dir, image_dir, output_json_path, image_width, image_height, class_map)
