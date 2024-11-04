from ultralytics import YOLO
import cv2
import json
import os
import time
import config  # Import the config file

# Initialize model and video capture using values from config
model = YOLO(config.MODEL_PATH)
cap = cv2.VideoCapture(0)

# Counters and configurations
detected_items = {}
last_logged_times = {}

def generate_video_feed():
    """ Generate the video feed with YOLO detections. """
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame)
        current_time = time.time()

        for result in results:
            boxes = result.boxes
            class_ids = boxes.cls.cpu().numpy()
            confidences = boxes.conf.cpu().numpy()
            class_names = [model.names[int(cls_id)] for cls_id in class_ids]

            for class_name, confidence, class_id in zip(class_names, confidences, class_ids):
                if confidence >= config.CONFIDENCE_THRESHOLD:
                    label = "{} ({:.2f})".format(class_name, confidence)
                    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    if current_time - last_logged_times.get(class_name, 0) >= config.LOGGING_INTERVAL:
                        log_detection(class_name, class_id, confidence, current_time)

        # Encode the frame as a JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        
        yield ('--frame\r\n'
               'Content-Type: image/jpeg\r\n\r\n').encode() + frame + '\r\n'.encode()

def log_detection(class_name, class_id, confidence, current_time):
    """ Log detection to JSON file with a specified interval. """
    detected_data = {
        "class_id_roboflow": int(class_id),
        "class_id": class_name,
        "confidence": round(float(confidence), 2)
    }
    last_logged_times[class_name] = current_time

    with open(os.path.join(config.JSON_DIRECTORY, config.JSON_FILE_NAME), "w") as f:
        json.dump(detected_data, f, indent=4)

def get_detected_json():
    """ Fetch the most recent detection JSON data. """
    json_path = os.path.join(config.JSON_DIRECTORY, config.JSON_FILE_NAME)
    with open(json_path, "r") as f:
        data = json.load(f)
    return data
