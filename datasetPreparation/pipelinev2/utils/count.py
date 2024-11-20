import os
import fnmatch

# count directory and subdirectory total file
#count = 0
#for root_dir, cur_dir, files in os.walk(r"C:\\Users\\ptplokee\\source\\miniMartDataset\\raw"):
#    count += len(files)
#print('file count:', count)

# count file directory
dir_path = r"C:\\Users\\ptplokee\\source\\miniMartDataset\\raw\\chipsmore_mini_doublechoc"
count = len(fnmatch.filter(os.listdir(dir_path), '*.*'))
print('File Count:', count)