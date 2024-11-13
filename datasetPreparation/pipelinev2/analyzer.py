import os
import json
from os import listdir

def analyze_dataset(directory_path, labels_dir):
    # Initialize dictionaries to store item counts and a list to store item names
    dataset_info = {}
    item_names = []
    unlabeled_images_count = 0
    labeled_images_count = 0

    # Loop through each subdirectory (each item)
    for item in listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        
        # Check if the path is a directory (each item)
        if os.path.isdir(item_path):
            image_count = 0
            unlabeled_count = 0
            labeled_count = 0
            
            # Count the number of images and check for corresponding labels
            for f in listdir(item_path):
                if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    image_count += 1
                    image_name = os.path.splitext(f)[0]
                    label_file = os.path.join(labels_dir, item, image_name + ".txt")
                    
                    # Check if label file exists; count as unlabeled if it does not
                    if os.path.exists(label_file):
                        labeled_count += 1
                    else:
                        unlabeled_count += 1
            
            # Add to the dataset information and item names
            dataset_info[item] = {
                "Total Images": image_count,
                "Labeled Images": labeled_count,
                "Unlabeled Images": unlabeled_count
            }
            item_names.append(item)
            labeled_images_count += labeled_count
            unlabeled_images_count += unlabeled_count

    # Count total items and images
    total_items = len(dataset_info)
    total_images = sum(item["Total Images"] for item in dataset_info.values())

    # Create a report as a dictionary
    report = {
        "Total Items": total_items,
        "Total Images": total_images,
        "Total Labeled Images": labeled_images_count,
        "Total Unlabeled Images": unlabeled_images_count,
        "Item Breakdown": dataset_info
    }

    # Save the report as a JSON file
    report_path = os.path.join(directory_path, "dataset_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)

    # Save the item names to a text file for ease of labeling
    labels_path = os.path.join(directory_path, "itemLabels.txt")
    with open(labels_path, "w") as f:
        for item in item_names:
            f.write(f"{item}\n")

    # Print summary
    print("\n--- Dataset Overview ---")
    print(f"Total Items (Classes): {total_items}")
    print(f"Total Images (Annotations): {total_images}")
    print(f"Total Labeled Images: {labeled_images_count}")
    print(f"Total Unlabeled Images: {unlabeled_images_count}")
    print("\nClass-wise Annotations:")
    for item, info in dataset_info.items():
        print(f"{item}: {info['Total Images']} images, {info['Labeled Images']} labeled, {info['Unlabeled Images']} unlabeled")

    print(f"\nDetailed report saved to: {report_path}")
    print(f"Item labels saved to: {labels_path}")

# Usage example
directory_path = 'C:\\Users\\ptplokee\\source\\miniMartDataset\\raw'
labels_dir = 'C:\\Users\\ptplokee\\source\\miniMartDataset\\annotationAIv1\\labels'
analyze_dataset(directory_path, labels_dir)
