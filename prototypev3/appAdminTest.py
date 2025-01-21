from flask import Flask, request, jsonify, render_template, send_from_directory, session
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import random

app = Flask(__name__)
app.secret_key = 'asdqwezxc123'

# Paths and Directories
UPLOAD_FOLDER = './prototypev3/uploads'  # Change this path as needed
DATASET_DIR = os.path.join(UPLOAD_FOLDER, 'dataset')
IMAGES_DIR = os.path.join(DATASET_DIR, 'images')
LABELS_DIR = os.path.join(DATASET_DIR, 'labels')
USER_LABELLED_DATASET_DIR = os.path.join(UPLOAD_FOLDER, 'user-labelled-dataset')
USER_IMAGES_DIR = os.path.join(USER_LABELLED_DATASET_DIR, 'images')
USER_LABELS_DIR = os.path.join(USER_LABELLED_DATASET_DIR, 'labels')

for directory in [UPLOAD_FOLDER, DATASET_DIR, IMAGES_DIR, LABELS_DIR]:
    os.makedirs(directory, exist_ok=True)
# Create the directories if they don't exist
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
        save_frames_and_annotations(file_path, normalized_name)
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

def save_frames_and_annotations(video_path, product_name):
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    prev_frame = None  # For frame comparison
    temp_images_dir = os.path.join(IMAGES_DIR, 'temp')
    temp_labels_dir = os.path.join(LABELS_DIR, 'temp')
    
    # Ensure the necessary directories exist
    os.makedirs(temp_images_dir, exist_ok=True)
    os.makedirs(temp_labels_dir, exist_ok=True)
    os.makedirs(USER_IMAGES_DIR, exist_ok=True)  # Ensure user-labelled dataset folder
    os.makedirs(IMAGES_DIR, exist_ok=True)       # Ensure dataset folder exists

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
        frame_path = os.path.join(temp_images_dir, frame_name)
        cv2.imwrite(frame_path, frame)

        # Save the frame data and label file path
        all_frames.append({
            'frame_path': frame_path,
            'frame_name': frame_name
        })

        frame_idx += 1

    cap.release()

    # Now, process the frames:
    # Move the top 15 frames based on calculated differences to the user-labelled dataset
    top_frames = select_top_frames(all_frames)

    # Move top 15 frames to the user-labelled dataset
    for frame in top_frames:
        if os.path.exists(frame['frame_path']):
            target_frame_path = os.path.join(USER_IMAGES_DIR, frame['frame_name'])
            os.rename(frame['frame_path'], target_frame_path)
            label_path = os.path.join(USER_LABELS_DIR, frame['frame_name'].replace('.jpg', '.txt'))
            open(label_path, 'w').close()  # Create empty label files for the moved frames
        else:
            print(f"File {frame['frame_name']} does not exist at {frame['frame_path']}")

    # Move the remaining frames to the dataset
    for frame in all_frames:
        if frame not in top_frames:
            if os.path.exists(frame['frame_path']):
                target_frame_path = os.path.join(IMAGES_DIR, frame['frame_name'])
                os.rename(frame['frame_path'], target_frame_path)
                label_path = os.path.join(LABELS_DIR, frame['frame_name'].replace('.jpg', '.txt'))
                open(label_path, 'w').close()  # Create empty label files for the remaining frames
            else:
                print(f"File {frame['frame_name']} does not exist at {frame['frame_path']}")

    # Clean up temporary directories
    cleanup_temp(temp_images_dir, temp_labels_dir)

def select_top_frames(all_frames):
    # Sort frames by their difference (you can adjust the logic if needed)
    sorted_frames = sorted(all_frames, key=lambda x: cv2.sumElems(cv2.imread(x['frame_path']))[0], reverse=True)
    
    # Select the top 15 frames with the highest difference
    top_frames = sorted_frames[:15]

    return top_frames

def cleanup_temp(*dirs):
    for directory in dirs:
        for root, _, files in os.walk(directory):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(directory)

#def split_and_save(images_dir, labels_dir):
#    frames = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith('.jpg')]
#    labels = [os.path.join(labels_dir, f) for f in os.listdir(labels_dir) if f.endswith('.txt')]
#    combined = list(zip(frames, labels))
#    random.shuffle(combined)

#    splits = {
#        'train': combined[:int(0.7 * len(combined))],
#        'val': combined[int(0.7 * len(combined)):int(0.9 * len(combined))],
#        'test': combined[int(0.9 * len(combined)):]
#    }

#    for split_name, data in splits.items():
#        split_images_dir = os.path.join(DATASET_DIR, split_name, 'images')
#        split_labels_dir = os.path.join(DATASET_DIR, split_name, 'labels')
#        os.makedirs(split_images_dir, exist_ok=True)
#        os.makedirs(split_labels_dir, exist_ok=True)

#        for frame_path, label_path in data:
#            os.rename(frame_path, os.path.join(split_images_dir, os.path.basename(frame_path)))
#            os.rename(label_path, os.path.join(split_labels_dir, os.path.basename(label_path)))

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

if __name__ == '__main__':
    app.run()
