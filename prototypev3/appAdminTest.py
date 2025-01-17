from flask import Flask, request, jsonify, render_template
import os
import cv2
import uuid
from werkzeug.utils import secure_filename
from yolo_utils import extract_frames, auto_label_frames, augment_data, create_yolo_dataset, train_yolo, test_yolo

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
FRAMES_FOLDER = './frames'
LABELS_FOLDER = './labels'
AUGMENT_FOLDER = './augmented'
DATASET_FOLDER = './datasets'
MODELS_FOLDER = './models'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRAMES_FOLDER, exist_ok=True)
os.makedirs(LABELS_FOLDER, exist_ok=True)
os.makedirs(AUGMENT_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    product_name = request.form.get('product_name')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract frames from video
        frames = extract_frames(file_path, FRAMES_FOLDER, frame_count=400)

        # Auto-label frames if possible
        if auto_label_frames(frames, product_name, LABELS_FOLDER):
            return jsonify({'status': 'Frames auto-labeled', 'frames': frames}), 200
        else:
            return jsonify({'status': 'Manual labeling required', 'frames': frames}), 200

@app.route('/label', methods=['POST'])
def label_frames():
    label_data = request.json
    for frame, bbox in label_data['bboxes'].items():
        save_labels(frame, bbox, LABELS_FOLDER)

    return jsonify({'status': 'Labels saved'}), 200

@app.route('/review', methods=['GET'])
def review_labels():
    frames = list_files(FRAMES_FOLDER)
    labels = load_labels(LABELS_FOLDER)
    return jsonify({'frames': frames, 'labels': labels}), 200

@app.route('/augment', methods=['POST'])
def augment():
    augment_data(FRAMES_FOLDER, LABELS_FOLDER, AUGMENT_FOLDER)
    return jsonify({'status': 'Data augmented'}), 200

@app.route('/dataset', methods=['POST'])
def create_dataset():
    version = uuid.uuid4().hex[:6]
    dataset_path = os.path.join(DATASET_FOLDER, f'dataset_v{version}')
    create_yolo_dataset(AUGMENT_FOLDER, dataset_path)
    return jsonify({'status': 'Dataset created', 'version': version}), 200

@app.route('/train', methods=['POST'])
def train():
    dataset_version = request.json['dataset_version']
    dataset_path = os.path.join(DATASET_FOLDER, f'dataset_v{dataset_version}')
    model_path = os.path.join(MODELS_FOLDER, f'yolov11_v{dataset_version}.pt')
    train_yolo(dataset_path, model_path)
    return jsonify({'status': 'Model trained', 'model_version': dataset_version}), 200

@app.route('/test', methods=['POST'])
def test_model():
    model_version = request.json['model_version']
    model_path = os.path.join(MODELS_FOLDER, f'yolov11_v{model_version}.pt')
    results = test_yolo(model_path)
    return jsonify({'status': 'Model tested', 'results': results}), 200

@app.route('/update', methods=['POST'])
def update_model():
    model_version = request.json['model_version']
    config_file = './checkout_config.yaml'
    update_config(config_file, model_version)
    return jsonify({'status': 'Model updated in checkout config'}), 200

def save_labels(frame, bbox, folder):
    # Save bounding box labels to file
    label_path = os.path.join(folder, f'{frame}.txt')
    with open(label_path, 'w') as f:
        for box in bbox:
            f.write(' '.join(map(str, box)) + '\n')

def list_files(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def load_labels(folder):
    labels = {}
    for label_file in os.listdir(folder):
        with open(os.path.join(folder, label_file), 'r') as f:
            labels[label_file] = f.readlines()
    return labels

if __name__ == '__main__':
    app.run(debug=True)
