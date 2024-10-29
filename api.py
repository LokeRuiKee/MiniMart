from flask import Flask, jsonify, request
from ultralytics import YOLO
import cv2
import time
import threading

app = Flask(__name__)
model = YOLO("C:\\Users\\ptplokee\\Source\\Repos\\MiniMart\\model\\martModelv2\\weights\\best.pt")
cap = cv2.VideoCapture(0)

# Detection control flags and variables
is_detecting = False
pause_flag = False
last_detection_time = time.time()
confidence_threshold = 0.5
pause_duration = 3  # seconds

# Thread function to run YOLO
def run_yolo():
    global is_detecting, pause_flag, last_detection_time

    while is_detecting:
        ret, frame = cap.read()
        if not ret:
            break

        # Skip detection if paused
        if pause_flag and (time.time() - last_detection_time < pause_duration):
            continue
        else:
            pause_flag = False

        # YOLO detection
        results = model.predict(frame)
        detected_data = []

        for result in results:
            boxes = result.boxes
            class_ids = boxes.cls.cpu().numpy()
            confidences = boxes.conf.cpu().numpy()
            class_names = [model.names[int(cls_id)] for cls_id in class_ids]

            for class_name, confidence, class_id, box in zip(class_names, confidences, class_ids, boxes.xyxy):
                if confidence >= confidence_threshold:
                    x1, y1, x2, y2 = map(int, box)
                    detected_data.append({
                        "class_id": int(class_id),
                        "class_name": class_name,
                        "confidence": float(confidence)
                    })
                    # Set pause flag
                    pause_flag = True
                    last_detection_time = time.time()

        # Send detection data to frontend
        yield detected_data  # Yield data for live updates

# API route to start detection
@app.route('/start_detection', methods=['POST'])
def start_detection():
    global is_detecting
    if not is_detecting:
        is_detecting = True
        threading.Thread(target=run_yolo).start()
    return jsonify({"status": "Detection started"})

# API route to stop detection
@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global is_detecting
    is_detecting = False
    return jsonify({"status": "Detection stopped"})

# API route to retrieve detection data
@app.route('/get_detection', methods=['GET'])
def get_detection():
    detection_data = next(run_yolo())  # Get latest data
    return jsonify(detection_data)

if __name__ == "__main__":
    app.run()
