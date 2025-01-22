from flask import Flask, request, jsonify, render_template, send_from_directory, session
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import random
import yaml  # For writing YAML files
import shutil
import random

app = Flask(__name__)
app.secret_key = 'asdqwezxc123'

# Paths and Directories
UPLOAD_FOLDER = './prototypev3/uploads'
DATASET_DIR = os.path.join(UPLOAD_FOLDER, 'dataset')
IMAGES_DIR = os.path.join(DATASET_DIR, 'images')
LABELS_DIR = os.path.join(DATASET_DIR, 'labels')
USER_LABELLED_DATASET_DIR = os.path.join(UPLOAD_FOLDER, 'user-labelled-dataset')
USER_IMAGES_DIR = os.path.join(USER_LABELLED_DATASET_DIR, 'images')
USER_LABELS_DIR = os.path.join(USER_LABELLED_DATASET_DIR, 'labels')

for directory in [UPLOAD_FOLDER, DATASET_DIR, IMAGES_DIR, LABELS_DIR]:
    os.makedirs(directory, exist_ok=True)
for directory in [USER_LABELLED_DATASET_DIR, USER_IMAGES_DIR, USER_LABELS_DIR]:
    os.makedirs(directory, exist_ok=True)
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/adminupload')
def admin_upload_page():
    return render_template('admin_upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video_file' not in request.files or 'product_name' not in request.form:
        return jsonify({"error": "Missing file or product name"}), 400

    video_file = request.files['video_file']
    product_name = request.form['product_name']

    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    normalized_name = product_name.replace(' ', '-').lower()
    filename = secure_filename(video_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video_file.save(file_path)

    session['product_name'] = normalized_name

    try:
        all_frames = extract_frames(file_path, normalized_name)
        selected_frames = select_frames(all_frames)
        move_frames(all_frames, selected_frames)
    except Exception as e:
        return jsonify({"error": f"Error processing video: {str(e)}"}), 500

    return jsonify({"message": f"Video uploaded and frames saved for {normalized_name}"}), 200

@app.route('/annotate')
def annotate_page():
    return render_template('admin_annotate.html')

@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    uploads_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads_dir, filename)

@app.route('/dataset/<path:filename>')
def serve_dataset(filename):
    dataset_dir = os.path.abspath(DATASET_DIR)
    return send_from_directory(dataset_dir, filename)

def extract_frames(video_path, product_name):
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    prev_frame = None  # For frame comparison
    
    # Ensure the necessary directories exist
    os.makedirs(USER_IMAGES_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    all_frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Filter: Calculate frame difference
        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, frame)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            non_zero_count = cv2.countNonZero(gray_diff)
            threshold = 50000
            if non_zero_count < threshold:
                print(f"Frame {frame_idx} skipped due to low difference.")
                continue

        prev_frame = frame  # Update previous frame for comparison

        # Save the frame temporarily
        frame_name = f"{product_name}_{frame_idx}.jpg"
        frame_path = os.path.join(IMAGES_DIR, frame_name)
        cv2.imwrite(frame_path, frame)

        # Save the frame data and label file path
        all_frames.append({
            'frame_path': frame_path,
            'frame_name': frame_name
        })

        frame_idx += 1

    cap.release()

    print(f"Frame extraction completed. Total frames: {len(all_frames)}")
    return all_frames

def select_frames(all_frames):
    sorted_frames = sorted(all_frames, key=lambda x: cv2.sumElems(cv2.imread(x['frame_path']))[0], reverse=True)
    selected_frames = sorted_frames[:15]

    print(f"15 frames with highest differences have been selected.")
    return selected_frames

def move_frames(all_frames, selected_frames):
    for frame in selected_frames:
        if os.path.exists(frame['frame_path']):
            target_frame_path = os.path.join(USER_IMAGES_DIR, frame['frame_name'])
            os.rename(frame['frame_path'], target_frame_path)
            print(f"Selected frames moved to dataset")
        else:
            print(f"File {frame['frame_name']} does not exist at {frame['frame_path']}")

    print(f"All frames moved to respective datasets.")

@app.route('/get_frames', methods=['GET'])
def get_frames():
    images_dir = os.path.join('prototypev3', 'uploads', 'dataset', 'images')
    
    # Fetch all valid image files
    image_files = sorted(
        [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith('.jpg')]
    )
    
    if len(image_files) < 2:
        return jsonify({"error": f"Not enough frames found in {images_dir}/images for comparison."}), 404

    # Read images and calculate differences
    frame_differences = []
    prev_frame = None
    
    for idx, file_path in enumerate(image_files):
        frame = cv2.imread(file_path)
        
        if frame is None:
            print(f"Skipping unreadable or invalid file: {file_path}")
            continue
        
        if prev_frame is not None:
            # Calculate the difference between current and previous frames
            diff = cv2.absdiff(prev_frame, frame)
            diff_score = np.sum(diff)  # Sum of absolute differences
            
            # Store the file path and its score
            frame_differences.append((file_path, diff_score))
        
        prev_frame = frame  # Update the previous frame

    if not frame_differences:
        return jsonify({"error": "No valid frames with measurable differences found."}), 404

    # Sort frames by difference score in descending order
    frame_differences.sort(key=lambda x: x[1], reverse=True)
    
    # Select top 15 frames
    top_frames = [f"/dataset/images/{os.path.basename(frame[0])}" for frame in frame_differences[:15]]

    return jsonify(top_frames)

@app.route('/submit_annotations', methods=['POST'])
def submit_annotations():
    annotations = request.json
    if not annotations:
        return jsonify({"error": "No annotations provided"}), 400

    print(f"Received annotations: {annotations}")

    # Preprocess annotations
    annotations = preprocess_annotations(annotations)

    labels_dir = USER_LABELS_DIR
    os.makedirs(labels_dir, exist_ok=True)

    try:
        save_annotations_yolo(annotations, labels_dir)
        split_dataset(labels_dir)
        generate_data_yaml(labels_dir, normalized_name)
        return jsonify({"message": "Annotations saved successfully!"})
    except Exception as e:
        print(f"Error while saving annotations: {str(e)}")
        return jsonify({"error": f"Failed to save annotations: {str(e)}"}), 500

def preprocess_annotations(annotations):
    processed = []
    for annotation in annotations:
        frame = annotation.get("frame")
        if not frame:
            continue

        # Normalize to YOLO format (you may need to adjust this logic)
        width = annotation["width"]
        height = annotation["height"]
        x_center = annotation["x"] + width / 2
        y_center = annotation["y"] + height / 2

        processed.append({
            "frame": frame,
            "bboxes": [
                {
                    "class": "default_class",
                    "x_center": x_center / 640,  # Normalize based on image width
                    "y_center": y_center / 480,  # Normalize based on image height
                    "width": width / 640,
                    "height": height / 480,
                }
            ],
            "class_names": {
                "default_class": 0
            }
        })
    return processed

def save_annotations_yolo(annotations, labels_dir):
    os.makedirs(labels_dir, exist_ok=True)

    for annotation in annotations:
        frame_path = annotation.get('frame')  # Frame path from input JSON
        bboxes = annotation.get('bboxes', [])  # List of bounding boxes
        class_names = annotation.get('class_names', {})  # Class-name-to-ID mapping

        if not frame_path or not bboxes:
            print(f"Skipping annotation with invalid data: {annotation}")
            continue  # Skip invalid or empty annotations

        # Derive .txt filename from the frame filename
        label_filename = os.path.splitext(os.path.basename(frame_path))[0] + '.txt'
        label_file_path = os.path.join(labels_dir, label_filename).replace("\\", "/")  # Ensure forward slashes

        # Write annotations to the file
        with open(label_file_path, 'w') as label_file:
            for bbox in bboxes:
                class_name = bbox.get('class')
                class_id = class_names.get(class_name, -1)  # Retrieve class ID or default to -1
                x_center = bbox.get('x_center')
                y_center = bbox.get('y_center')
                width = bbox.get('width')
                height = bbox.get('height')

                if class_id == -1 or None in [x_center, y_center, width, height]:
                    print(f"Skipping invalid bounding box: {bbox}")
                    continue  # Skip invalid bounding boxes

                # YOLO format: class_id x_center y_center width height
                label_file.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

        # Log the absolute path of the saved file
        absolute_path = os.path.abspath(label_file_path)
        print(f"Annotations saved to (absolute path): {absolute_path}")

def split_dataset(dataset_dir, split_ratios=None, output_dir=None):
    if split_ratios is None:
        split_ratios = {"train": 0.7, "val": 0.2, "test": 0.1}
    
    if abs(sum(split_ratios.values()) - 1.0) > 1e-6:
        raise ValueError("Split ratios must sum to 1.0")
    
    # Default output directory
    if output_dir is None:
        output_dir = dataset_dir
    
    # Paths to images and labels directories
    images_dir = os.path.join(dataset_dir, "images")
    labels_dir = os.path.join(dataset_dir, "labels")
    
    if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
        raise ValueError("Dataset directory must contain 'images' and 'labels' subdirectories.")
    
    # Get all image and label file pairs
    images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    labels = [f.replace(os.path.splitext(f)[1], ".txt") for f in images]  # Match labels to images
    
    if not all(os.path.exists(os.path.join(labels_dir, label)) for label in labels):
        raise ValueError("Some images are missing corresponding label files.")
    
    # Combine and shuffle
    combined = list(zip(images, labels))
    random.shuffle(combined)
    
    # Calculate split indices
    total_count = len(combined)
    train_count = int(split_ratios["train"] * total_count)
    val_count = int(split_ratios["val"] * total_count)
    test_count = total_count - train_count - val_count
    
    splits = {
        "train": combined[:train_count],
        "val": combined[train_count:train_count + val_count],
        "test": combined[train_count + val_count:]
    }
    
    # Create output directories
    for split_name in splits:
        split_images_dir = os.path.join(output_dir, split_name, "images")
        split_labels_dir = os.path.join(output_dir, split_name, "labels")
        os.makedirs(split_images_dir, exist_ok=True)
        os.makedirs(split_labels_dir, exist_ok=True)

        # Copy files into their respective split directories
        for image_file, label_file in splits[split_name]:
            src_image = os.path.join(images_dir, image_file)
            dest_image = os.path.join(split_images_dir, image_file)
            shutil.copy(src_image, dest_image)

            src_label = os.path.join(labels_dir, label_file)
            dest_label = os.path.join(split_labels_dir, label_file)
            shutil.copy(src_label, dest_label)
    
    print(f"Dataset successfully split into train, val, and test sets.")


def generate_data_yaml(dataset_dir, class_names, output_path="data.yaml"):
    # Define paths for train, val, and test splits
    train_path = os.path.join(dataset_dir, "train", "images")
    val_path = os.path.join(dataset_dir, "val", "images")
    test_path = os.path.join(dataset_dir, "test", "images")

    # Check if the directories exist
    if not os.path.exists(train_path) or not os.path.exists(val_path):
        raise FileNotFoundError("Train or validation directories are missing.")

    # Construct the YAML data
    data = {
        "train": train_path,
        "val": val_path,
        "nc": len(class_names),  # Number of classes
        "names": class_names
    }

    # Add test path if it exists
    if os.path.exists(test_path):
        data["test"] = test_path

    # Save the YAML file
    with open(output_path, "w") as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)

    print(f"data.yaml file created at {output_path}")

# Helper Function: Train Model
def train_model(data_yaml_path, output_dir="./annotate_model_outputs"):
    print(f"Starting training with {data_yaml_path}")
    annotate_model = YOLO("yolo11n.pt")
    results = annotate_model.train(data=data_yaml_path, epochs=10)
    print("Model training completed")

## Helper Function: Auto-Annotate
#def auto_annotate(model_path, dataset_dir):
#    print("Starting auto-annotation")
#    images_dir = os.path.join(dataset_dir, "images")
#    labels_dir = os.path.join(dataset_dir, "labels")

#    for image_name in os.listdir(images_dir):
#        image_path = os.path.join(images_dir, image_name)
#        label_path = os.path.join(labels_dir, image_name.replace('.jpg', '.txt'))

#        # Replace this with the actual YOLOv11 inference command
#        # This example writes dummy annotations
#        with open(label_path, "w") as f:
#            f.write("0 0.5 0.5 0.2 0.2\n")

#    print("Auto-annotation completed")

if __name__ == '__main__':
    app.run()
