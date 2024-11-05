from flask import Flask, Response, send_from_directory
from flask_cors import CORS
from main import generate_video_feed, get_detected_json  # Import functions
import config  # Import config for paths, etc.

app = Flask(__name__)
CORS(app)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_json')
def get_json():
    return send_from_directory(config.JSON_DIRECTORY, config.JSON_FILE_NAME)

if __name__ == '__main__':
    app.run()
