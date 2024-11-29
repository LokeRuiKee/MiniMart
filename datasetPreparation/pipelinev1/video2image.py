import cv2
import os
import glob
import numpy as np
import data_config as dconfig

# Path to the directory containing video files
video_directory = dconfig.INPUT_DATA_DIRECTORY
# Get all mp4 files in the directory
video_files = glob.glob(os.path.join(video_directory, "*.mp4"))
target_count = 355

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

#def balance_original_images(class_path, image_paths):
#    original_count = len(image_paths)
#    if original_count > target_original_count:
#        # Delete excess original images
#        excess_count = original_count - target_original_count
#        images_to_delete = random.sample(image_paths, excess_count)
#        for img_path in images_to_delete:
#            os.remove(img_path)
#        print(f"Deleted {excess_count} excess original images in '{class_path}'")
#    elif original_count < target_original_count:
#        print(f"Class '{class_name}' has fewer original images ({original_count}) than target ({target_original_count}).")

#if target_count < frameno:
#        print(f"Warning: Class '{class_name}' still has fewer original images ({original_count}) than target ({target_original_count}).")
#else:
#    balance_original_images(output_folder, image_name)

cv2.destroyAllWindows()
