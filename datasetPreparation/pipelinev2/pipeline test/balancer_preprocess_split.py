import os
import random
import cv2
import albumentations as A
from tqdm import tqdm
from glob import glob
from sklearn.model_selection import train_test_split
from preprocess import prepare

# Set the path to your dataset
dataset_path = "C:\\Users\\ptplokee\\source\\miniMartDataset\\difference20"
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

# Function to delete excess original images if the count is above the target
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

# Function to split images into train, validation, and test sets
def split_dataset(class_path, images):
    # Splitting images into train, validation, and test sets
    train_images, temp_images = train_test_split(images, test_size=(val_ratio + test_ratio))
    val_images, test_images = train_test_split(temp_images, test_size=(test_ratio / (val_ratio + test_ratio)))

    # Creating directories for train, val, test splits if they don't exist
    for split in ['train', 'val', 'test']:
        split_path = os.path.join(dataset_path, split, class_name)
        os.makedirs(split_path, exist_ok=True)

    # Move files to the appropriate directories
    for img_path in train_images:
        os.rename(img_path, os.path.join(dataset_path, 'train', class_name, os.path.basename(img_path)))
    for img_path in val_images:
        os.rename(img_path, os.path.join(dataset_path, 'val', class_name, os.path.basename(img_path)))
    for img_path in test_images:
        os.rename(img_path, os.path.join(dataset_path, 'test', class_name, os.path.basename(img_path)))

# Get list of all classes
classes = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]

for class_name in classes:
    class_path = os.path.join(dataset_path, class_name)
    
    # Step 1: Balance original images
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

    # Step 2: Calculate number of augmentations needed
    current_total = len(glob(os.path.join(class_path, "*.jpg")))
    augment_needed = max(0, target_augmented_count - current_total)

    if augment_needed > 0:
        print(f"Generating {augment_needed} augmentations for class '{class_name}' to reach {target_augmented_count} total images.")

        # Augment images to reach the target count
        for i in tqdm(range(augment_needed), desc=f"Augmenting {class_name}"):
            img_path = random.choice(original_images)
            image = cv2.imread(img_path)
            augmented = augment(image=image)['image']

            # Save augmented image with a unique name
            new_image_path = os.path.join(class_path, f"{class_name}_{augmentation_prefix}{i}.jpg")
            cv2.imwrite(new_image_path, augmented)
    else:
        print(f"Class '{class_name}' already meets the target total count ({target_augmented_count}).")

    # Step 3: Split into train, validation, and test sets
    all_images = glob(os.path.join(class_path, "*.jpg"))
    split_dataset(class_path, all_images)

print("Dataset balancing, preprocessing, and splitting complete.")
