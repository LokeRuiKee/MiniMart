from ultralytics import YOLO

model = YOLO("C:\\Users\\ptplokee\\source\\repos\\MiniMart\\model\\modelv3\\weights\\best.pt")  # load the best model


results=model.track(source=0, show=True)


#while True:
#    ret, frame = cam.read()

#    # Display the captured frame
#    cv2.imshow('Camera', frame)

#    # Press 'q' to exit the loop
#    if cv2.waitKey(1) == ord('q'):
#        break

## Release the capture and writer objects
#cam.release()
#cv2.destroyAllWindows()