#todo: add item name as label instead of item id

from ultralytics import YOLO
import cv2
import json
import os
import config
import supervision as sv
import numpy as np

# Initialize model and tracker
model = YOLO(config.MODEL_PATH)
cap = cv2.VideoCapture(0)

# Tracker and bounding box annotator setup
tracker = sv.ByteTrack()
box_annotator = sv.BoundingBoxAnnotator()
label_annotator = sv.LabelAnnotator()
trace_annotator = sv.TraceAnnotator()
logged_tracker_ids = set() # use set cuz ensure unique

def inference(frame: np.ndarray):
    """Run inference on a frame and return detection results."""
    results = model.predict(frame, conf=config.CONFIDENCE_THRESHOLD)[0]
    return results

def extract_detection_details(results):
    """Extract details of each detection from the model results."""
    for box in results.boxes:
        class_id = int(box.cls)
        confidence = float(box.conf)
        class_name = model.names[class_id]
        yield class_name, confidence, class_id

def callback(frame: np.ndarray, _: int) -> np.ndarray:
    """Process the frame to detect, track, and annotate objects."""
    # Run inference and get results
    results = inference(frame)
    
    # Convert to sv-compatible detections for tracking
    detections = sv.Detections.from_ultralytics(results)
    detections = tracker.update_with_detections(detections)

    labels = [
        f"#{tracker_id} {results.names[class_id]}"
        for class_id, tracker_id
        in zip(detections.class_id, detections.tracker_id)
    ]

    annotated_frame = box_annotator.annotate(frame.copy(), detections=detections)

    for tracker_id, (class_name, confidence, class_id) in zip(detections.tracker_id, extract_detection_details(results)):
        if confidence >= config.CONFIDENCE_THRESHOLD:
            if tracker_id not in logged_tracker_ids:
                logged_tracker_ids.add(tracker_id)  # Mark this tracker ID as logged
                log_item(class_name, confidence, class_id)

    return label_annotator.annotate(annotated_frame, detections=detections, labels=labels)


def generate_video_feed():
    """Generate the video feed with detections and annotations."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame with the callback function
        annotated_frame = callback(frame, 0)

        # Encode the frame as JPEG for display
        _, jpeg = cv2.imencode('.jpg', annotated_frame)
        frame = jpeg.tobytes()
        
        yield ('--frame\r\n'
               'Content-Type: image/jpeg\r\n\r\n').encode() + frame + '\r\n'.encode()

def log_item(class_name, confidence, class_id):
    """Log detected item details to a JSON file."""
    detected_data = {
        "class_id": int(class_id)+1,
        "class_name": class_name,
        "confidence": round(float(confidence), 2)
    }

    with open(config.JSON_PATH, "w") as f:
        json.dump(detected_data, f, indent=4)
