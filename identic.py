import argparse
import os
import hashlib

parser = argparse.ArgumentParser()

# python args.py --foo --bar --baz
parser.add_argument('-f', action='store_true')
parser.add_argument('-d', action='store_true')
parser.add_argument('-c', action='store_true')
parser.add_argument('-n', action='store_true')
parser.add_argument('-cn', action='store_true')
parser.add_argument('-s', action='store_true')
parser.add_argument("***",nargs = "*")
args = vars(parser.parse_args())
print(args)

lookFiles = args.get('f')
lookDirs = args.get('d')
lookContents = args.get('c')
lookNames = args.get('n')
lookContentsAndNames = args.get('cn')
lookSizes = args.get('s') and not (lookNames or lookContentsAndNames)
dirList = args.get('***') if args.get('***') else ['.']

filePathAndFileSize = dict()
filePathAndFileContentHash = dict()
filePathAndFileNameHash = dict()
dirPathAndDirContentHash = dict()
dirPathAndDirNameHash = dict()




def getAllDirs():
    allDirs = list()
    for dir in dirList:
        for root, dirs, files in os.walk(dir, topdown=True):
            allDirs.append(root)
    return allDirs

def getHashValue(file,isFile):
    hashValue = hashlib.sha256()
    if isFile:
        with open(file, "rb") as file:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: file.read(4096), b""):
                hashValue.update(byte_block)
    else:
        if(not type(file) == list):
            hashValue.update(file.encode("utf-8"))
        else:
            for i in file[::-1]:
                hashValue.update(i.encode("utf-8"))

    return hashValue.hexdigest()

def getAllHashValuesFromDict():
    print("filePathAndFileSize : " , filePathAndFileSize)
    print("filePathAndFileContentHash : " , filePathAndFileContentHash)
    print("filePathAndFileNameHash : " , filePathAndFileNameHash)
    print("dirPathAndDirContentHash : " , dirPathAndDirContentHash)
    print("dirPathAndDirNameHash : " , dirPathAndDirNameHash)

def fileSizesInsideDir(dir):
    print("LOOK FOR : " , dir)
    global filePathAndFileSize,filePathAndFileHash,hashValue,dirPathAndDirNameHash,dirPathAndDirContentHash
    files = os.listdir(dir)
    dirName = os.path.basename(dir)
    fileNameHashes = list()
    fileContentHashes = list()
    path = ""
    for file in files:
        filePath = os.path.join(dir, file)
        if not os.path.isdir(filePath):
            filePathAndFileSize[filePath] = os.path.getsize(filePath)
            filePathAndFileContentHash[filePath] = getHashValue(filePath,True)
            filePathAndFileNameHash[filePath] = getHashValue(os.path.dirname(filePath),False)
            fileContentHashes.append(filePathAndFileContentHash[filePath])
            fileNameHashes.append(filePathAndFileNameHash[filePath])

    fileContentHashes.sort()
    fileNameHashes.sort()
    fileNameHashes.insert(0, getHashValue(dirName, False))
    dirPathAndDirNameHash[dir] = getHashValue(fileNameHashes,False)
    dirPathAndDirContentHash[dir] = getHashValue(fileContentHashes,False)


allDirs = getAllDirs()
for dir in allDirs:
    fileSizesInsideDir(dir)
getAllHashValuesFromDict()
print("filePathAndFileSize", filePathAndFileSize)
