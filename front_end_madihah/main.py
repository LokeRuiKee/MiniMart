from ultralytics import YOLO
import cv2
import json
import time

model = YOLO("C:\\Users\\ptpmaahm\\Source\\Repos\\MiniMart\\model\\martModelv2\\weights\\best.pt")

# Track detected items
detected_items = {}
last_logged_times = {}
logging_interval = 5 # seconds
confidence_threshold = 0.7

# Initialize the webcam
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Use the model to predict objects in the frame
    results = model.predict(frame)
    current_time = time.time()  # Current timestamp for comparison

    # Prepare data for JSON output
    detected_data = []  # List to store detected items for JSON

    # Loop through detected results
    for result in results:
        boxes = result.boxes
        class_ids = boxes.cls.cpu().numpy()
        confidences = boxes.conf.cpu().numpy()

        # Get the class names for the detected items
        class_names = [model.names[int(cls_id)] for cls_id in class_ids]
        class_id = int(class_ids[0]) if class_ids.size > 0 else None

        # Display detection on the webcam feed
        for class_name, confidence, class_ids in zip(class_names, confidences, class_ids):
            if confidence >= confidence_threshold:
                label = "{} {} ({:.2f})".format(class_id, class_name, confidence)
                cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                last_logged_time = last_logged_times.get(class_name, 0)

                if current_time - last_logged_time >= logging_interval:

                    # Append each detected item to the data list
                    detected_data = {
                        "class_id_roboflow": class_id,
                        "class_id": class_name,
                        "confidence": round(float(confidence), 2)
                    }

                    f = open("C:\\Users\\ptpmaahm\\Source\\Repos\\MiniMart\\front_end_madihah\\detected_item.json", "w")
                    json.dump(detected_data, f, indent=4)
                    f.close()
                    cv2.putText(frame, "data saved", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    last_logged_times[class_name] = current_time

    # Display the webcam feed with object detection
    cv2.imshow("Self Checkout", frame)

    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()