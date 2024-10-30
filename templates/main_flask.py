from flask import Flask, Response, jsonify
from ultralytics import YOLO
import cv2
import json
import time

app = Flask(__name__)

model = YOLO("C:\\Users\\ptplokee\\Source\\Repos\\MiniMart\\model\\martModelv2\\weights\\best.pt")
cap = cv2.VideoCapture(0)

detected_items = {}
last_logged_times = {}
logging_interval = 5  # seconds
confidence_threshold = 0.7

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
                            "class_id": int(class_id),
                            "class_name": class_name,
                            "confidence": round(float(confidence), 2)
                        }
                        last_logged_times[class_name] = current_time

                        f = open("C:\\Users\\ptplokee\\Source\\Repos\\MiniMart\\templates\\flask_detect.json", "w")
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

if __name__ == '__main__':
    app.run()
