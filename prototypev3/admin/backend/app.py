from flask import Flask, jsonify, request, render_template, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import cv2
import os
from ultralytics import YOLO
from flask_cors import CORS
import numpy as np
import pyodbc


app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'server': 'PTPNTE818',
    'database': 'miniMart',
    'driver': '{SQL Server}',
    'trusted_connection': 'yes'
}

@app.route('/database_video', methods=['GET'])
def get_video_from_database():
    try:
        # Create database connection
        conn = pyodbc.connect(
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        )
        cursor = conn.cursor()

        # Query the database
        cursor.execute("SELECT * FROM [miniMart].[dbo].[videos]")
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Return results as JSON
        return jsonify(results)

    except Exception as e:
        print("Error executing query:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        # Close the connection
        if 'conn' in locals():
            conn.close()

# Directories for saving recordings and frames
RECORDINGS_DIR = "/admin/backend/recorded_videos/"
FRAMES_DIR = "admin/ai_model/datasets/train/"

os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

# Global variables for recording
recording = False
video_writer = None
video_file_path = None
capture = cv2.VideoCapture(0)  # Change device index if using a different camera


# Save the video file path to the database
def save_to_database(video_path):
    session = Session()
    created_at = datetime.now()
    session.execute(f"INSERT INTO dbo.videos (file_path, created_at) VALUES ('{video_path}', '{created_at}')")
    session.commit()
    session.close()


# Process the video: Extract frames and train the model
def process_video(video_path):
    frames_dir = preprocess_video(video_path)
    train_model(frames_dir)


# Preprocess video by extracting frames
def preprocess_video(video_path):
    cap = cv2.VideoCapture(video_path)
    count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(FRAMES_DIR, f"frame_{count}.jpg")
        cv2.imwrite(frame_path, frame)
        count += 1

    cap.release()
    return FRAMES_DIR


## Train YOLO model
#def train_model(frames_dir):
#    model = YOLO("admin/ai_model/yolo11n.pt")
#    data_path = os.path.abspath("admin/ai_model/datasets/train")
#    model.train(data=data_path, epochs=50, imgsz=640)
#    model.export(format="torchscript")  # Save model for deployment

# Serve the HTML file
@app.route('/admin')
def home():
    return render_template('admin_index.html')

# Start recording video
@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording, video_writer, video_file_path
    if not recording:
        video_file_path = os.path.join(RECORDINGS_DIR, f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        video_writer = cv2.VideoWriter(video_file_path, fourcc, 20.0, (640, 480))
        recording = True
        return jsonify({"message": "Recording started."})
    return jsonify({"message": "Recording is already in progress."})


# Pause video recording
@app.route('/pause_recording', methods=['POST'])
def pause_recording():
    global recording
    if recording:
        recording = False
        return jsonify({"message": "Recording paused."})
    return jsonify({"message": "Recording is not active."})


# Resume video recording
@app.route('/resume_recording', methods=['POST'])
def resume_recording():
    global recording
    if not recording:
        recording = True
        return jsonify({"message": "Recording resumed."})
    return jsonify({"message": "Recording is already active."})


# Stop video recording
@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording, video_writer, video_file_path
    if recording:
        recording = False
        if video_writer:
            if video_file_path:
                process_video(video_file_path)
                save_to_database(video_file_path)
                video_writer.release()
                return jsonify({"message": "Recording stopped, video saved, and training initiated."})
    return jsonify({"message": "No recording in progress."})


## Perform detection
#@app.route('/detect', methods=['POST'])
#def detect():
#    image_path = request.json.get("image_path", "frontend/uploads/sample_image.jpg")
#    if not os.path.exists(image_path):
#        return jsonify({"error": "Image file not found."}), 400

#    model = YOLO("admin/ai_model/trained_model.pt")  # Load the trained YOLO model
#    results = model.predict(image_path)
#    detections = results.pandas().xyxy[0].to_dict(orient="records")
#    return jsonify({"detections": detections})


# Capture frames during recording
def record_video():
    global recording, video_writer, capture
    while True:
        if recording:
            ret, frame = capture.read()
            if ret:
                video_writer.write(frame)

@app.route('/video_feed_admin')
def video_feed():
    return Response(generate_video_feed_admin(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_video_feed_admin():
    """Generate the video feed with detections and annotations."""
    while True:
        ret, frame = capture.read()

        if not ret:
            break

        # Encode the frame as JPEG for display
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    app.run()
