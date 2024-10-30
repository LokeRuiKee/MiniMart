import cv2
import os
import glob

# Path to the directory containing video files
video_directory = "C:\\Users\\ptplokee\\source\\repos\\MiniMart\\videoDataset\\"
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

    while True:
        ret, frame = cam.read()
        if ret:
            # Save the frame as an image in the output folder
            image_name = os.path.join(output_folder, "{}.jpg".format(frameno))
            print('New frame captured... {}'.format(image_name))
            cv2.imwrite(image_name, frame)
            frameno += 1
        else:
            break

    cam.release()

cv2.destroyAllWindows()