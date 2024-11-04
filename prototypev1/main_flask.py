from flask import Flask, Response, jsonify, send_from_directory
from ultralytics import YOLO
import cv2
import json
import time
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app)

model = YOLO("../model/martModelv2/weights/best.pt")
cap = cv2.VideoCapture(0)

detected_items = {}
last_logged_times = {}
logging_interval = 5  # seconds
confidence_threshold = 0.7
json_directory = "C:\\Users\\ptplokee\\Source\\Repos\\MiniMart\\prototypev1\\static\\"

def generate():
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
                if confidence >= confidence_threshold:
                    label = "{} ({:.2f})".format(class_name, confidence)
                    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    if current_time - last_logged_times.get(class_name, 0) >= logging_interval:
                        detected_data = {
                            "class_id_roboflow": int(class_id),
                            "class_id": class_name,
                            "confidence": round(float(confidence), 2)
                        }
                        last_logged_times[class_name] = current_time

                        f = open(os.path.join(json_directory, "flask_detect.json"), "w")
                        json.dump(detected_data, f, indent=4)
                        f.close()

        # Encode the frame as a JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        
        yield ('--frame\r\n'
               'Content-Type: image/jpeg\r\n\r\n').encode() + frame + '\r\n'.encode()

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_json')
def get_json():
    return send_from_directory(json_directory, 'flask_detect.json')

if __name__ == '__main__':
    app.run()