from ultralytics import YOLO
import cv2
import json
import os
import time
import config

# Initialize model and video capture
model = YOLO(config.MODEL_PATH)
cap = cv2.VideoCapture(0)

# Counters and session tracking
last_logged_times = {}
session_items = {}  # Tracks item quantities in the current session

def generate_video_feed():
    """ Generate the video feed with YOLO detections. """
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, agnostic_nms=True)
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

                    # Log detection with session item counting
                    if current_time - last_logged_times.get(class_name, 0) >= config.LOGGING_INTERVAL:
                        log_detection(class_name, class_id, confidence, current_time)

        # Encode the frame as a JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        
        yield ('--frame\r\n'
               'Content-Type: image/jpeg\r\n\r\n').encode() + frame + '\r\n'.encode()

def log_detection(class_name, class_id, confidence, current_time):
    """ Log detection and update quantity for detected items in the session. """
    # Update last logged time for the item
    last_logged_times[class_name] = current_time
    
    # Check if the item already exists in the session log
    if class_name in session_items:
        # Increment the quantity if the item has been detected before
        session_items[class_name]['quantity'] += 1
    else:
        # Initialize item data if it's the first detection in the session
        session_items[class_name] = {
            "class_id_roboflow": int(class_id),
            "class_name": class_name,
            "confidence": round(float(confidence), 2),
            "quantity": 1
        }

    # Save session data to JSON for front-end or post-session processing
    with open(os.path.join(config.JSON_DIRECTORY, config.JSON_FILE_NAME), "w") as f:
        json.dump(session_items, f, indent=4)

def get_detected_json():
    """ Fetch the most recent detection JSON data. """
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    return data

def finalize_session():
    """ Finalizes the session and clears session data after checkout. """
    # Save or process session data as needed, e.g., store in a database or display to the user
    with open(os.path.join(config.JSON_DIRECTORY, "final_session.json"), "w") as f:
        json.dump(session_items, f, indent=4)

    # Clear session items for the next checkout session
    session_items.clear()
