from os import listdir

# Define the directory
directory = "C:\\Users\\ptplokee\\source\\miniMartDataset\\raw_200"

# List all files in the directory
files_dir = listdir(directory)

# Create a sorted list of class names as strings
class_names = sorted([name for name in files_dir])

# Format the list to match the required output format and write to file
with open("itemLabels.txt", "w") as f:
    f.write(f"names: {class_names}")
