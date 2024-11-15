import os
import json
import uuid

def yolo_to_label_studio(yolo_file, image_path, image_width, image_height, model_version="one", score=0.5):
    label_studio_data = {
        "data": {
            "image": image_path
        },
        "predictions": [
            {
                "model_version": model_version,
                "score": score,
                "result": []
            }
        ]
    }
    
    # Read YOLO annotations
    with open(yolo_file, 'r') as file:
        for line in file:
            # Parse the YOLO format line
            class_id, x_center, y_center, box_width, box_height = map(float, line.strip().split())
            
            # Convert YOLO coordinates to Label Studio format
            x = (x_center - box_width / 2) * 100  # top-left x in percentage
            y = (y_center - box_height / 2) * 100  # top-left y in percentage
            width = box_width * 100
            height = box_height * 100
            
            # Create the bounding box entry for Label Studio
            label_studio_data["predictions"][0]["result"].append({
                "original_width": image_width,
                "original_height": image_height,
                "image_rotation": 0,
                "value": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "rotation": 0
                },
                "id": str(uuid.uuid4())[:8],
                "from_name": "rect",
                "to_name": "image",
                "type": "rectangle"
            })
    
    return label_studio_data

def convert_directory(yolo_dir, image_dir, output_json_path, image_width, image_height):
    # Collect all YOLO txt files
    yolo_files = [f for f in os.listdir(yolo_dir) if f.endswith('.txt')]
    all_annotations = []

    for yolo_file in yolo_files:
        image_file = os.path.splitext(yolo_file)[0] + ".jpg"  # Assuming images are .jpg
        image_path = os.path.join("/static/samples", image_file)  # Path for Label Studio JSON
        
        # Convert YOLO to Label Studio format
        annotation = yolo_to_label_studio(
            yolo_file=os.path.join(yolo_dir, yolo_file),
            image_path=image_path,
            image_width=image_width,
            image_height=image_height
        )
        
        all_annotations.append(annotation)

    # Save all annotations to a JSON file
    with open(output_json_path, 'w') as out_file:
        json.dump(all_annotations, out_file, indent=2)

# Usage
yolo_dir = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\train\\labels"
image_dir = "C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\train\\images"
output_json_path = "./datasetPreparation/label-studio/output_annotations.json"
image_width = 640  # Set your image width here
image_height = 640  # Set your image height here

convert_directory(yolo_dir, image_dir, output_json_path, image_width, image_height)
