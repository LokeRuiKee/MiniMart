from os import listdir

directory = "C:\\Users\\ptplokee\\source\\miniMartDataset\\raw"
files_dir =  listdir(directory)
newlist = []
for names in files_dir:
    newlist.append(names)
print (newlist)

f = open("itemLabels.txt", "w")
for list in newlist:
    f.write(f"{list}\n")
f.close()