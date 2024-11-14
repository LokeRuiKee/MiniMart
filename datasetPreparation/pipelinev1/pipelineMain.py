import os
import cv2
from preprocess import prepare
import data_config as dconfig
import augmentation
from pathlib import Path

# Define input and output directories
input_folder = Path(dconfig.INPUT_DATA_DIRECTORY)
preprocessed_output_folder = Path(dconfig.PREPROCESSED_OUTPUT_DIRECTORY)
augmented_prepro_output_folder = Path(dconfig.AUGMENTED_PREPRO_OUTPUT_DIRECTORY)
#augmented_raw_output_folder = Path(dconfig.AUGMENTED_RAW_OUTPUT_DIRECTORY)

# Ensure output directories exist
preprocessed_output_folder.mkdir(parents=True, exist_ok=True)
augmented_prepro_output_folder.mkdir(parents=True, exist_ok=True)
#augmented_raw_output_folder.mkdir(parents=True, exist_ok=True)

# Define preprocessing configuration
preproc_config = {
    "resize": {"enabled": True, "width": 640, "height": 640, "format": "Stretch to"},
    "grayscale": {"enabled": True},
    "contrast": {"enabled": True, "type": "Histogram Equalization"}
}

# Loop through each file in the input directory
for image_path in input_folder.rglob('*.[pj][np]g'):
    # Read the image
    raw_image = cv2.imread(str(image_path))
    if raw_image is None:
        print(f"Warning: Couldn't open {image_path}. Skipping...")
        continue
    image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)  

    # Apply preprocessing
    processed_image, _ = prepare(image, preproc_config)
    
    # Determine preprocessed image path and save
    relative_path = image_path.relative_to(input_folder)
    preprocessed_image_path = preprocessed_output_folder / relative_path.parent / f"preprocessed_{image_path.stem}.jpg"
    preprocessed_image_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(preprocessed_image_path), cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR))
    print(f"Preprocessed and saved: {preprocessed_image_path}")

    # Apply augmentation to the preprocessed image
    augmented_image = augmentation.transform(image=processed_image)['image']
    
    # Determine augmented image path and save
    augmented_image_path = augmented_prepro_output_folder / relative_path.parent / f"augmented_preprocessed_{image_path.stem}.jpg"
    augmented_image_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(augmented_image_path), cv2.cvtColor(augmented_image, cv2.COLOR_RGB2BGR))
    print(f"Augmented and saved: {augmented_image_path}")

    ## Apply augmentation to the raw image
    #augmented_raw_image = augmentation.transform(image=image)['image']
    
    ## Determine augmented image path and save
    #augmented_raw_image_path = augmented_raw_output_folder / relative_path.parent / f"augmented_raw_{image_path.stem}.jpg"
    #augmented_raw_image_path.parent.mkdir(parents=True, exist_ok=True)
    #cv2.imwrite(str(augmented_raw_image_path), cv2.cvtColor(augmented_raw_image, cv2.COLOR_BGR2RGB)  )
    #print(f"Augmented the raw and saved: {augmented_raw_image_path}")


print("Preprocessing and augmentation completed for all images.")
