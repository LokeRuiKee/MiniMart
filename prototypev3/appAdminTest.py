from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from glob import glob
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/adminupload')
def adminUploadPage():
    return render_template('admin_upload.html')

UPLOAD_FOLDER = './prototypev3/uploads' # change this after completion
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video_file' not in request.files or 'product_name' not in request.form:
        return jsonify({"error": "Missing file or product name"}), 400

    video_file = request.files['video_file']
    product_name = request.form['product_name']

    # Save video file
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(video_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video_file.save(file_path)

    try:
        extract_frame(app.config['UPLOAD_FOLDER'])
    except Exception as e:
        return jsonify({"error": f"Failed to extract frames: {str(e)}"}), 500

    # Simulate database update
    # Here, you can replace this part with your actual database logic
    print(f"Product Name: {product_name}")
    print(f"Video saved at: {file_path}")

    return jsonify({"message": "File uploaded successfully and frames extracted successfully", "product_name": product_name}), 200


def extract_frame(video_directory):
    video_files = glob(os.path.join(video_directory, "*.mp4"))
    for video_file in video_files:
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        output_folder = os.path.join(video_directory, video_name)
        os.makedirs(output_folder, exist_ok=True)

        cam = cv2.VideoCapture(video_file)
        frameno = 0
        prev_frame = None

        while True:
            ret, frame = cam.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_frame is None or np.mean(cv2.absdiff(prev_frame, gray_frame)) > 20:
                image_name = os.path.join(output_folder, f"{frameno}.jpg")
                print(f'New frame captured... {image_name}')
                cv2.imwrite(image_name, frame)
                frameno += 1
                prev_frame = gray_frame

        cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run()
