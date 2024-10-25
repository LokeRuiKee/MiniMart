from ultralytics import YOLO
import cv2
import json


model = YOLO("C:\\Users\\ptplokee\\source\\repos\\MiniMart\\model\\modelv2\\weights\\best.pt")  # load the best model

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

            # for writing to json
            data = [{'class_id': class_id, 'class_name': class_name}]

            # Serializing json
            json_object = json.dumps(data, indent=4)
 
            # Writing to sample.json
            f = open("predictedData.json", "w")
            f.write(json_object)
    
    # Show the running total and number of items on the frame
    num_items = len(detected_items)
    cv2.putText(frame, "Items: {}".format(num_items), (10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the webcam feed with object detection
    cv2.imshow("Self Checkout", frame)

    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()