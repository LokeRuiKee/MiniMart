from ultralytics import YOLO
import supervision as sv

model = YOLO("C:\\Users\\ptplokee\\Source\\Repos\\MiniMart\\model\\martModelv2\\weights\\best.pt")  # load the best model


results=model.track(source=0, show=True)

#json_results = results.pandas().xyxy[0].to_json(orient="records")  # Convert results to JSON
#print(json_results)