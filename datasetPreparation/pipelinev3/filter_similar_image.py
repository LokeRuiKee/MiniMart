import os
import shutil
from PIL import Image
import imagehash
from tqdm import tqdm
from collections import defaultdict

# Paths
dataset_dir = "C:\\Users\\ptplokee\\source\\hot-storage\\miniMartDataset\\annotationModel_dataset\\preprocessed\\testFilter\\raw_img"
filtered_dir = os.path.join(dataset_dir, "filtered_images")

def filter_similar_images_by_class(input_dir, output_dir, hash_size=8, similarity_threshold=5):
    """
    Filters out similar images for each class based on perceptual hashing and summarizes the dataset.
    
    Args:
        input_dir (str): Directory containing subfolders for each class with the original images.
        output_dir (str): Directory to save filtered images in subfolders.
        hash_size (int): Hash size for perceptual hashing.
        similarity_threshold (int): Maximum Hamming distance for considering images similar.
    """
    os.makedirs(output_dir, exist_ok=True)
    class_summary = defaultdict(int)  # To keep track of image counts per class

    for class_folder in tqdm(os.listdir(input_dir), desc="Processing Classes"):
        class_path = os.path.join(input_dir, class_folder)
        if not os.path.isdir(class_path):
            continue

        # Create corresponding folder in the filtered output directory
        filtered_class_dir = os.path.join(output_dir, class_folder)
        os.makedirs(filtered_class_dir, exist_ok=True)

        # Initialize hash storage for this class
        image_hashes = {}
        duplicates = 0

        for img_file in os.listdir(class_path):
            if not (img_file.endswith(".jpg") or img_file.endswith(".png")):
                continue

            img_path = os.path.join(class_path, img_file)
            try:
                # Compute perceptual hash
                img = Image.open(img_path)
                img_hash = imagehash.average_hash(img, hash_size=hash_size)
            except Exception as e:
                print(f"Error processing {img_file}: {e}")
                continue

            # Check for similar images
            is_duplicate = False
            for existing_hash in image_hashes:
                if abs(img_hash - existing_hash) <= similarity_threshold:
                    is_duplicate = True
                    duplicates += 1
                    break

            if not is_duplicate:
                image_hashes[img_hash] = img_file
                shutil.copy(img_path, os.path.join(filtered_class_dir, img_file))
                class_summary[class_folder] += 1

        print(f"Class '{class_folder}': {duplicates} similar images removed.")

    return class_summary

def summarize_dataset(dataset_summary):
    """
    Prints a summary of the dataset showing the number of images available for each class.
    
    Args:
        dataset_summary (dict): A dictionary with class names as keys and image counts as values.
    """
    print("\nDataset Summary After Filtering:")
    print("=" * 40)
    total_images = 0
    for class_name, count in dataset_summary.items():
        print(f"{class_name}: {count} images")
        total_images += count
    print("=" * 40)
    print(f"Total Images: {total_images} images")

# Run filtering and summarization
dataset_summary = filter_similar_images_by_class(
    input_dir=dataset_dir,
    output_dir=filtered_dir,
    hash_size=8,
    similarity_threshold=5
)

summarize_dataset(dataset_summary)
