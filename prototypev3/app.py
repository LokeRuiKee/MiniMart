from flask import Flask, Response, send_from_directory, jsonify, render_template
from flask_cors import CORS
from main import generate_video_feed
import config
import pyodbc
import os
import cv2
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# DATABASE CONFIGURATION
DB_CONFIG = {
    'server': 'PTPNTE818',
    'database': 'miniMart',
    'driver': '{SQL Server}',
    'trusted_connection': 'yes'
}

# CUSTOMER CHECKOUT 

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_json')
def get_json():
    return send_from_directory(config.JSON_DIRECTORY, config.JSON_FILE_NAME)

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

# ADMIN

## GLOBAL VARIABLES
#video_file_path = None

# SERVING HTML PAGES
@app.route('/admin')
def adminHome():
    return render_template('admin_upload.html')

@app.route('/checkout')
def checkoutHome():
    return render_template('checkout_index.html')

# RECORDING MODES


# VIDEO FEED


# FUNCTIONS TO SAVE PATH TO DATABASE

# DIRECTORIES  for saving recordings and frames
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
RECORDINGS_DIR = os.path.join(BASE_DIR, "adminDataset", "0.recorded_videos")
FRAMES_DIR = os.path.join(BASE_DIR, "adminDataset", "1.recorded_frames")

os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

# GLOBAL VARIABLES
recording = False
frames_buffer = []
recording_end_time = None

@app.route('/start_frame_recording', methods=['POST'])
def start_frame_recording():
    global recording, frames_buffer, recording_end_time
    if not recording:
        frames_buffer = []
        recording_end_time = datetime.now() + timedelta(seconds=60)
        recording = True
        print("Frame recording started.")
        return jsonify({"message": "Frame recording started."})
    return jsonify({"message": "Recording is already in progress."})

@app.route('/pause_frame_recording', methods=['POST'])
def pause_frame_recording():
    global recording
    if recording:
        recording = False
        print("Frame recording paused.")
        return jsonify({"message": "Frame recording paused."})
    return jsonify({"message": "Recording is not active."})

@app.route('/resume_frame_recording', methods=['POST'])
def resume_frame_recording():
    global recording
    if not recording:
        recording = True
        print("Frame recording resumed.")
        return jsonify({"message": "Frame recording resumed."})
    return jsonify({"message": "Recording is already active."})

@app.route('/stop_frame_recording', methods=['POST'])
def stop_frame_recording():
    global recording, frames_buffer
    if recording or frames_buffer:
        recording = False
        # Save frames as a video and images
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_path = os.path.join(RECORDINGS_DIR, f"recording_{timestamp}.mp4")
            save_video_from_frames(frames_buffer, video_path)

            # Save each frame as an image
            frame_dir = os.path.join(FRAMES_DIR, f"frames_{timestamp}")
            os.makedirs(frame_dir, exist_ok=True)
            for i, frame in enumerate(frames_buffer):
                frame_path = os.path.join(frame_dir, f"frame_{i:04d}.jpg")
                cv2.imwrite(frame_path, frame)
                save_frame_path_to_database(frame_path)

            save_video_path_to_database(video_path)
            frames_buffer = []
            print(f"Frame recording stopped. Video saved to {video_path}.")
            return jsonify({"message": "Recording stopped, video and frames saved."})
        except Exception as e:
            print(f"Error stopping frame recording: {e}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"message": "No recording in progress."})

# Capture frames from the video feed
def generate_video_feed_admin():
    global recording, frames_buffer, recording_end_time
    while True:
        ret, frame = capture.read()
        if not ret:
            break

        # If recording is active and within the 60-second limit
        if recording and datetime.now() < recording_end_time:
            frames_buffer.append(frame)

        # Encode the frame for live streaming
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Save frames as a video
def save_video_from_frames(frames, video_path, fps=20.0, frame_size=(640, 480)):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(video_path, fourcc, fps, frame_size)
    for frame in frames:
        video_writer.write(frame)
    video_writer.release()

if __name__ == '__main__':
    app.run()
