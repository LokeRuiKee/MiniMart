import os
from pathlib import Path
import cv2
import albumentations as A
import data_config as dconfig

# Paths
input_folder = Path(dconfig.INPUT_DATA_DIRECTORY)
output_folder = Path(dconfig.OUTPUT_DATA_DIRECTORY)

# Define augmentation pipeline
transform = A.Compose([
    A.CLAHE(),
    A.RandomRotate90(),
    A.Transpose(),
    A.Blur(blur_limit=3),
    A.HueSaturationValue(),
    A.Affine(scale=(0.9, 0.7), rotate=(-15,15), shear=(-25,25), keep_ratio=True, balanced_scale=True)
])

## Iterate over each image in subdirectories
#for image_path in input_folder.rglob('*.[pj][np]g'):  # Adjust pattern as needed
#    # Read the image
#    image = cv2.imread(str(image_path))
#    if image is None:
#        print(f"Warning: Couldn't open {image_path}. Skipping...")
#        continue
#    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#    # Apply augmentations
#    augmented_image = transform(image=image)['image']

#    # Determine output path
#    relative_path = image_path.relative_to(input_folder)
#    output_image_path = output_folder / relative_path.parent / f"processed_{image_path.stem}.jpg"
#    output_image_path.parent.mkdir(parents=True, exist_ok=True)  # Create subdirectories if needed

#    # Save the augmented image
#    cv2.imwrite(str(output_image_path), cv2.cvtColor(augmented_image, cv2.COLOR_RGB2BGR))

#    print(f"Saved processed image to {output_image_path}")
