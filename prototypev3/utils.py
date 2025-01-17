# functions for extract_frames, auto_label_frames, augment_data, create_yolo_dataset, train_yolo, test_yolo

import os
import random
import cv2
import albumentations as A
from tqdm import tqdm
from glob import glob
import numpy as np
from sklearn.model_selection import train_test_split
from collections import defaultdict
import csv

# Extract frames from videos
def extract_frames(video_directory):
    video_files = glob(os.path.join(video_directory, "*.mp4"))
    for video_file in video_files:
        # Create a folder for each video
        video_name = os.path.splitext(os.path.basename(video_file))[0]
        output_folder = os.path.join(video_directory, video_name)
        os.makedirs(output_folder, exist_ok=True)

        cam = cv2.VideoCapture(video_file)
        frameno = 0
        prev_frame = None

        while True:
            ret, frame = cam.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_frame is None or np.mean(cv2.absdiff(prev_frame, gray_frame)) > 20:
                image_name = os.path.join(output_folder, f"{frameno}.jpg")
                print(f'New frame captured... {image_name}')
                cv2.imwrite(image_name, frame)
                frameno += 1
                prev_frame = gray_frame

        cam.release()
    cv2.destroyAllWindows()

# Delete excess original images if the count is above the target
def balance_original_images(class_path, image_paths):
    original_count = len(image_paths)
    if original_count > target_original_count:
        excess_count = original_count - target_original_count
        images_to_delete = random.sample(image_paths, excess_count)
        for img_path in images_to_delete:
            os.remove(img_path)
        print(f"Deleted {excess_count} excess original images in '{class_path}'")
    elif original_count < target_original_count:
        print(f"Class '{class_name}' has fewer original images ({original_count}) than target ({target_original_count}).")

# Split dataset into train, validation, and test sets
def split_dataset(class_path, images):
    train_images, temp_images = train_test_split(images, test_size=(val_ratio + test_ratio))
    val_images, test_images = train_test_split(temp_images, test_size=(test_ratio / (val_ratio + test_ratio)))

    for split in ['train', 'val', 'test']:
        split_path = os.path.join(dataset_path, split, class_name)
        os.makedirs(split_path, exist_ok=True)

    for img_path in train_images:
        os.rename(img_path, os.path.join(dataset_path, 'train', class_name, os.path.basename(img_path)))
    for img_path in val_images:
        os.rename(img_path, os.path.join(dataset_path, 'val', class_name, os.path.basename(img_path)))
    for img_path in test_images:
        os.rename(img_path, os.path.join(dataset_path, 'test', class_name, os.path.basename(img_path)))
