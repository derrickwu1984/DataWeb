import  os

def gci(filepath):
    fileList=[]
    #遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath)
    for fi in files:
        fi_d = os.path.join(filepath,fi)
        if os.path.isdir(fi_d):
            gci(fi_d)
        else:
            fileList.append(fi)
    return fileList

def find_files():
    list=['sh','sz','cy']
    filesList=[]
    for i in range(len(list)):
        filesList.append(gci(list[i]))
    return filesList
# filesList=find_files()
# for i in range(3):
#     for j in range(len(filesList[i])):
#         print (filesList[i][j])