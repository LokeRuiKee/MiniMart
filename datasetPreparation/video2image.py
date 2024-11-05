import cv2
import os
import glob
import numpy as np

# Path to the directory containing video files
video_directory = "./dataset/"
# Get all mp4 files in the directory
video_files = glob.glob(os.path.join(video_directory, "*.mp4"))

for video_file in video_files:
    # Create a folder for the current video
    video_name = os.path.splitext(os.path.basename(video_file))[0]
    output_folder = os.path.join(video_directory, video_name)
    os.makedirs(output_folder, exist_ok=True)

    # Capture video
    cam = cv2.VideoCapture(video_file)
    frameno = 0
    prev_frame = None  # To store the previous frame for comparison

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        # Convert frame to grayscale for simpler comparison
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Only save the frame if it's significantly different from the previous one
        if prev_frame is None or np.mean(cv2.absdiff(prev_frame, gray_frame)) > 20:  # Threshold can be adjusted
            # Save the frame as an image in the output folder
            image_name = os.path.join(output_folder, "{}.jpg".format(frameno))
            print('New frame captured... {}'.format(image_name))
            cv2.imwrite(image_name, frame)
            frameno += 1
            prev_frame = gray_frame  # Update previous frame

    cam.release()

cv2.destroyAllWindows()
