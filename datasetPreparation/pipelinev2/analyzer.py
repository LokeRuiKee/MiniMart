import os
import json
from os import listdir

def analyze_dataset(directory_path):
    # Initialize dictionary to store item counts and list to store item names
    dataset_info = {}
    item_names = []

    # Loop through each subdirectory (each item)
    for item in listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        
        # Check if the path is a directory (each item)
        if os.path.isdir(item_path):
            # Count the number of images in the subdirectory
            image_count = sum([1 for f in listdir(item_path) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])
            
            # Add to the dataset information and item names
            dataset_info[item] = image_count
            item_names.append(item)

    # Count total items and images
    total_items = len(dataset_info)
    total_images = sum(dataset_info.values())

    # Create a report as a dictionary
    report = {
        "Total Items": total_items,
        "Total Images": total_images,
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
    print("\nClass-wise Annotations:")
    for item, count in dataset_info.items():
        print(f"{item}: {count} images")
    
    print(f"\nDetailed report saved to: {report_path}")
    print(f"Item labels saved to: {labels_path}")

# Usage example
directory_path = 'C:\\Users\\ptplokee\\source\\miniMartDataset\\raw'
analyze_dataset(directory_path)
