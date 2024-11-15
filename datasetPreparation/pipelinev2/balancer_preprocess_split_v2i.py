import os
import random
import cv2
import albumentations as A
from tqdm import tqdm
from glob import glob
import numpy as np
from sklearn.model_selection import train_test_split
from preprocess import prepare
import data_config as dconfig

# Configurations
dataset_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\raw"
target_original_count = 200  # Target number of original images per class
target_augmented_count = 400  # Total target count (original + augmented images)
augmentation_prefix = "aug_"  # Prefix for augmented images
train_ratio, val_ratio, test_ratio = 0.7, 0.2, 0.1

# Define preprocessing configuration
preproc_config = {
    "resize": {"enabled": True, "width": 640, "height": 640, "format": "Stretch to"},
    "grayscale": {"enabled": True},
    "contrast": {"enabled": True, "type": "Histogram Equalization"}
}

# Define augmentation pipeline
augment = A.Compose([
    A.CLAHE(),
    A.RandomRotate90(),
    A.Transpose(),
    A.Blur(blur_limit=3),
    A.HueSaturationValue(),
    A.Affine(scale=(0.9, 0.7), rotate=(-15,15), shear=(-25,25), keep_ratio=True, balanced_scale=True)
])

# Extract frames from videos
def extract_frames_from_videos(video_directory):
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

# Step 1: Extract frames from videos
extract_frames_from_videos(dconfig.INPUT_DATA_DIRECTORY)

# Step 2: Process classes after frame extraction
classes = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]

for class_name in classes:
    class_path = os.path.join(dataset_path, class_name)
    
    # Step 3: Balance original images
    original_images = [img for img in glob(os.path.join(class_path, "*.jpg")) if augmentation_prefix not in img]
    
    # Preprocess each original image
    for img_path in original_images:
        image = cv2.imread(img_path)
        image, _ = prepare(image, preproc_config)
        cv2.imwrite(img_path, image)

    balance_original_images(class_path, original_images)
    
    # Re-check original images after deletion and preprocessing
    original_images = [img for img in glob(os.path.join(class_path, "*.jpg")) if augmentation_prefix not in img]
    original_count = len(original_images)

    # Step 4: Calculate number of augmentations needed
    current_total = len(glob(os.path.join(class_path, "*.jpg")))
    augment_needed = max(0, target_augmented_count - current_total)

    if augment_needed > 0:
        print(f"Generating {augment_needed} augmentations for class '{class_name}' to reach {target_augmented_count} total images.")

        for i in tqdm(range(augment_needed), desc=f"Augmenting {class_name}"):
            img_path = random.choice(original_images)
            image = cv2.imread(img_path)
            augmented = augment(image=image)['image']
            new_image_path = os.path.join(class_path, f"{class_name}_{augmentation_prefix}{i}.jpg")
            cv2.imwrite(new_image_path, augmented)
    else:
        print(f"Class '{class_name}' already meets the target total count ({target_augmented_count}).")

    # Step 5: Split into train, validation, and test sets
    all_images = glob(os.path.join(class_path, "*.jpg"))
    split_dataset(class_path, all_images)

print("Dataset extraction, balancing, preprocessing, augmentation, and splitting complete.")
