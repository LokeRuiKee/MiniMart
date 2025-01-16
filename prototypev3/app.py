from flask import Flask, Response, send_from_directory, jsonify, render_template
from flask_cors import CORS
from main import generate_video_feed
import config
import pyodbc
import os
import cv2
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_json')
def get_json():
    return send_from_directory(config.JSON_DIRECTORY, config.JSON_FILE_NAME)

# Database configuration
DB_CONFIG = {
    'server': 'PTPNTE818',
    'database': 'miniMart',
    'driver': '{SQL Server}',
    'trusted_connection': 'yes'
}

@app.route('/item_details', methods=['GET'])
def get_item_details():
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
        cursor.execute("SELECT * FROM [miniMart].[dbo].[item_list]")
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

# admin
# Directories for saving recordings and frames
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
RECORDINGS_DIR = os.path.join(BASE_DIR, "adminDataset", "0.recorded_videos")
FRAMES_DIR = os.path.join(BASE_DIR, "adminDataset", "1.recorded_frames")

os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

# Serve the HTML file
@app.route('/admin')
def adminHome():
    return render_template('admin_index.html')

@app.route('/checkout')
def checkoutHome():
    return render_template('checkout_index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording, video_writer, video_file_path
    if not recording:
        video_file_path = os.path.join(RECORDINGS_DIR, f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_file_path, fourcc, 20.0, (640, 480))
            if not video_writer.isOpened():
                raise IOError("VideoWriter failed to open.")
            
            recording = True
            print(f"Recording started. Saving to {video_file_path}")
            return jsonify({"message": "Recording started."})
        except Exception as e:
            print(f"Error starting recording: {e}")
            return jsonify({"error": str(e)}), 500
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

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording, video_writer, video_file_path
    if recording:
        recording = False
        if video_writer:
            video_writer.release()
            video_writer = None
        try:
            if video_file_path:
                save_video_to_database(video_file_path)
                frames_dir = extract_frame(video_file_path)
                print(f"Frames saved to {frames_dir}")
                return jsonify({"message": "Recording stopped, video saved, and frames extracted."})
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"message": "No recording in progress."})

# Capture frames during recording
def record_video():
    global recording, video_writer, capture
    while True:
        if recording:
            ret, frame = capture.read()
            if ret:
                video_writer.write(frame)

@app.route('/video_feed_admin')
def video_feed_admin():
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

# Global variables for recording
recording = False
video_writer = None
video_file_path = None
capture = cv2.VideoCapture(0)  # Change device index if using a different camera

def save_video_to_database(video_path):
    try:
        # Create database connection
        conn = pyodbc.connect(
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        )
        cursor = conn.cursor()

        # Insert video file path into the database
        created_at = datetime.now()
        cursor.execute(
            "INSERT INTO dbo.videos (file_path, created_at) VALUES (?, ?)",
            (video_path, created_at)
        )
        conn.commit()

    except Exception as e:
        print(f"Error saving video {video_path} to database:", str(e))

    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/save_frame', methods=['POST'])
def save_frame_to_database(frame_path):
    try:
        # Create database connection
        conn = pyodbc.connect(
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
        )
        cursor = conn.cursor()

        # Insert frame path into the database
        created_at = datetime.now()
        cursor.execute(
            "INSERT INTO dbo.frames (file_path, created_at) VALUES (?, ?)",
            (frame_path, created_at)
        )
        conn.commit()

    except Exception as e:
        print(f"Error saving frame {frame_path} to database:", str(e))

    finally:
        if 'conn' in locals():
            conn.close()

def extract_frame(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Failed to open video: {video_path}")

        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_path = os.path.join(FRAMES_DIR, f"frame_{count:04d}.jpg")
            cv2.imwrite(frame_path, frame)

            if not os.path.exists(frame_path):
                raise IOError(f"Failed to save frame at {frame_path}")

            save_frame_to_database(frame_path)
            count += 1

        cap.release()
        print(f"Extracted {count} frames from {video_path} to {FRAMES_DIR}")
        return FRAMES_DIR

    except Exception as e:
        print(f"Error extracting frames: {e}")
        return None

if __name__ == '__main__':
    app.run()
