from ultralytics import YOLO
import cv2

model = YOLO("C:\\Users\\ptplokee\\source\\repos\\MiniMart\\model\\modelv2\\weights\\best.pt")  # load the best model

item_prices = {
    'pau_chickenCurry': 3.30,
    'drinho_soya': 2.00,
    'drinho_sugarCane': 1.90,
    'pau_kaya': 2.80,
}

# Track detected items and total price
detected_items = {}
total_price = 0.0

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

        # Loop through detected items
        for class_name in class_names:
            if class_name not in detected_items:
                # First time detection, add to checkout list
                detected_items[class_name] = item_prices.get(class_name, 0.0)
                total_price += item_prices.get(class_name, 0.0)

        # Display detection on the webcam feed
        for class_name, confidence in zip(class_names, confidences):
            label = "{} ({:.2f})".format(class_name, confidence)
            # You can add bounding boxes and text to frame
            cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Show the running total and number of items on the frame
    num_items = len(detected_items)
    cv2.putText(frame, "Items: {} Total: ${:.2f}".format(num_items, total_price), (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the webcam feed with object detection
    cv2.imshow("Self Checkout", frame)

    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()