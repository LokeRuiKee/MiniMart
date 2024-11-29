import os
from collections import defaultdict
import csv

# Paths
dataset_dir = "C:\\Users\\ptplokee\\source\\hot-storage\\miniMartDataset\\annotationModel_dataset\\preprocessed\\filtered_images"
phases = ["train", "val", "test"]
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

def count_images_by_class(dataset_dir, phases, class_names):
    summary = {}
    for phase in phases:
        phase_path = os.path.join(dataset_dir, phase, "images")
        if not os.path.exists(phase_path):
            print(f"Warning: {phase_path} does not exist.")
            continue

        # Count images per class
        class_counts = defaultdict(int)
        for file in os.listdir(phase_path):
            if file.endswith(".jpg") or file.endswith(".png"):
                for class_name in class_names:
                    if class_name in file:  # Class is in filename
                        class_counts[class_name] += 1
                        break

        # Store summary
        summary[phase] = class_counts

    return summary

# Generate and print summary
summary = count_images_by_class(dataset_dir, phases, class_names)
with open('datasetSummary.csv', 'w', newline='') as csvfile:
    fieldnames = ['Phase', 'Class', 'Count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for phase, counts in summary.items():
        for class_name, count in counts.items():
            writer.writerow({'Phase': phase.upper(), 'Class': class_name, 'Count': count})