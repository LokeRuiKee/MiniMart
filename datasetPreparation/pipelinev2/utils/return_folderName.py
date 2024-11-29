#from os import listdir

## Define the directory
#directory = "C:\\Users\\ptplokee\\source\\hot-storage\\miniMartDataset\\annotationModel_dataset\\raw\\raw_img"

## List all files in the directory
#files_dir = listdir(directory)

## Create a sorted list of class names as strings
#class_names = sorted([name for name in files_dir])

## Format the list to match the required output format and write to file
#with open("itemLabels.txt", "w") as f:
#    f.write(f"{class_names}")


from os import listdir

# Define the directory
directory = "C:\\Users\\ptplokee\\source\\hot-storage\\miniMartDataset\\annotationModel_dataset\\raw\\raw_img"

# List all files in the directory
files_dir = listdir(directory)

# Create a sorted list of class names as strings
class_names = sorted([name for name in files_dir])

# Write the class names to a file, each on a new line
with open("itemLabels.txt", "w") as f:
    f.writelines(f"{name}\n" for name in class_names)
