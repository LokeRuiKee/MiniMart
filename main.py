from ultralytics import YOLO
import cv2
import json


model = YOLO("C:\\Users\\ptpmaahm\\MiniMart\\model\\martModelv2\\weights\\best.pt")  # load the best model

# Track detected items
detected_items = {}

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Use the model to predict objects in the frame
    results = model(frame)

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
            label = "{} {} ({:.2f})".format(class_id, class_name, confidence)

            # You can add bounding boxes and text to frame
            cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Append each detected item to the data list
            detected_data = {
                "class_id": class_id,
                "class_name": class_name,
                "confidence": round(float(confidence), 2)
            }

    # Open the file, write the JSON, and close it manually
    f = open("predictedData.json", "w")
    json.dump(detected_data, f, indent=4)  # Write JSON with indentation for readability
    f.close()  # Close the file

    # Display the webcam feed with object detection
    cv2.imshow("Self Checkout", frame)

    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()