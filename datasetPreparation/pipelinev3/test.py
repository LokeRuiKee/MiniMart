import os
import random
import shutil
import cv2
import albumentations as A
from albumentations.pytorch import ToTensorV2
from tqdm import tqdm
import yaml
from ultralytics import YOLO

# Paths
dataset_dir = "C:\\Users\\ptplokee\\source\\hot-storage\\miniMartDataset\\annotationModel_dataset\\preprocessed\\filtered_images"
raw_images_dir = os.path.join(dataset_dir, "raw_images")  # New folder for organized raw images
train_dir = os.path.join(dataset_dir, "train")
val_dir = os.path.join(dataset_dir, "val")
test_dir = os.path.join(dataset_dir, "test")

# Class names
class_names = [
    "biskclub_choc", "biskclub_orange", "biskclub_pineapple", "biskclub_strawberry",
    "chipsmore_mini_doublechoc", "chipsmore_mini_hazelnut", "chipsmore_mini_ori",
    "gery_cheese_crackers", "hwatai_banana", "hwatai_blueberry", "hwatai_choc",
    "hwatai_luxury_chips", "hwatai_waffler", "julies_golden", "luxury_chia",
    "luxury_ori", "malkist_bbq_crackers", "malkist_belgian", "malkist_cream_crackers",
    "malkist_sweet", "muchys_blueberry_tart", "muchys_choc_sandwhich_cookie",
    "muchys_strawberry_tart", "muchys_vanilla_sandwhich_cookie", "munchys_choc_crackers",
    "munchys_dark_cookie", "munchys_muzic", "munchys_ori_cookie", "munchys_white_crackers",
    "tiger_ori", "tiger_susu"
]

# 1. Organizing Raw Images into a Single Folder
def organize_raw_images(dataset_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for class_folder in os.listdir(dataset_dir):
        class_path = os.path.join(dataset_dir, class_folder)
        if os.path.isdir(class_path):  # Process only subfolders
            for file in os.listdir(class_path):
                if file.endswith(".jpg") or file.endswith(".png"):
                    # Handle duplicate filenames
                    base_name = os.path.splitext(file)[0]
                    ext = os.path.splitext(file)[1]
                    new_name = f"{class_folder}_{base_name}{ext}"
                    
                    dest_path = os.path.join(output_dir, new_name)
                    count = 1
                    while os.path.exists(dest_path):  # Ensure unique filename
                        new_name = f"{class_folder}_{base_name}_{count}{ext}"
                        dest_path = os.path.join(output_dir, new_name)
                        count += 1
                    
                    shutil.copy(os.path.join(class_path, file), dest_path)
    print("Raw images organized into a single folder.")

organize_raw_images(dataset_dir, raw_images_dir)

# 2. Splitting Dataset
def split_dataset(images_dir, train_ratio=0.8, val_ratio=0.1):
    all_files = [f for f in os.listdir(images_dir) if f.endswith(".jpg") or f.endswith(".png")]
    random.shuffle(all_files)
    train_split = int(len(all_files) * train_ratio)
    val_split = int(len(all_files) * (train_ratio + val_ratio))

    for phase, files in zip(["train", "val", "test"], [all_files[:train_split],
                                                      all_files[train_split:val_split],
                                                      all_files[val_split:]]):
        phase_img_dir = os.path.join(dataset_dir, phase, "images")
        os.makedirs(phase_img_dir, exist_ok=True)

        for file in files:
            shutil.copy(os.path.join(images_dir, file), os.path.join(phase_img_dir, file))

split_dataset(raw_images_dir)

# 3. Data Augmentation
def augment_images(input_dir, output_dir, augmentations):
    os.makedirs(output_dir, exist_ok=True)
    for img_file in tqdm(os.listdir(input_dir)):
        img_path = os.path.join(input_dir, img_file)
        img = cv2.imread(img_path)

        if img is None:
            continue

        # Apply augmentations
        transformed = augmentations(image=img)
        aug_img = transformed["image"]

        # Save augmented image
        cv2.imwrite(os.path.join(output_dir, img_file), aug_img)

augmentations = A.Compose([
    A.RandomRotate90(),
    A.Flip(),
    A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.1, rotate_limit=15, p=0.7),
    A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.5),
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
    A.Blur(blur_limit=3, p=0.2),
    A.ToGray(p=0.1),
    A.CLAHE(p=0.2),
    ToTensorV2()
])

augment_images(os.path.join(train_dir, "images"), os.path.join(train_dir, "augmented_images"), augmentations)

# 4. Create YAML File
def create_data_yaml(train_path, val_path, class_names, save_path="data.yaml"):
    data_yaml = {
        "path": "",
        "train": train_path,
        "val": val_path,
        "nc": len(class_names),
        "names": class_names
    }
    with open(save_path, "w") as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

create_data_yaml(os.path.join(train_dir, "images"), os.path.join(val_dir, "images"), class_names)

# 5. Train with YOLO
import torch
print("GPU Available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Using GPU:", torch.cuda.get_device_name(0))

#model = YOLO('yolov8n.pt')  # Use YOLOv11 equivalent weight
#model.train(data="data.yaml", epochs=100, imgsz=640, batch=16)

#print("Training complete.")
