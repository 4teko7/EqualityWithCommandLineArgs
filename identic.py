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
# print(args)

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
        with open(file, "rb") as myFile:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: myFile.read(4096), b""):
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
    global filePathAndFileSize,filePathAndFileHash,hashValue,dirPathAndDirNameHash,dirPathAndDirContentHash
    files = os.listdir(dir)
    dirName = os.path.basename(dir)
    allNameHashes = list()
    allContentHashes = list()
    if(len(files) == 0):
        dirPathAndDirContentHash[dir] = getHashValue("",False)
        dirPathAndDirNameHash[dir] = getHashValue("",False)

    for file in files:
        filePath = os.path.join(dir, file)
        if os.path.isfile(filePath):
            filePathAndFileSize[filePath] = os.path.getsize(filePath)
            filePathAndFileContentHash[filePath] = getHashValue(filePath,True)
            filePathAndFileNameHash[filePath] = getHashValue(os.path.basename(filePath),False)
            allContentHashes.append(filePathAndFileContentHash.get(filePath))
            allNameHashes.append(filePathAndFileNameHash.get(filePath))
        else:
            if(not dirPathAndDirContentHash.get(filePath) == None):
                allContentHashes.append(dirPathAndDirContentHash.get(filePath))
                allNameHashes.append(dirPathAndDirNameHash.get(filePath))

    allContentHashes.sort()
    allNameHashes.sort()

    allNameHashes.insert(0, getHashValue(dirName, False))
    dirPathAndDirNameHash[dir] = getHashValue(allNameHashes, False)
    dirPathAndDirContentHash[dir] = getHashValue(allContentHashes,False)
    # print(dirPathAndDirContentHash[dir])


def findAllSameValuesOfDictionary(myDict):
    tempSameValues = dict()
    sameValues = dict()

    for key,value in myDict.items():
        if tempSameValues.get(value) == None:
            tempSameValues[value] = set([key])
        else:
            tempSameValues[value].update([key])

    for key , value in tempSameValues.items():
        if(len(value) > 1):
            sameValues[key] = value

    return sameValues



def returnStringFromDictOfSameValues(dict1):
    string = str()
    for value in dict1.values():
        for v in value:
            string += v + "\n"
        string += "\n"
    return string

def writeToFile():
    sameDirContent = findAllSameValuesOfDictionary(dirPathAndDirContentHash)
    sameDirName = findAllSameValuesOfDictionary(dirPathAndDirNameHash)
    sameFileName = findAllSameValuesOfDictionary(filePathAndFileNameHash)
    sameFileContent = findAllSameValuesOfDictionary(filePathAndFileContentHash)
    stringOfSameDirContent = returnStringFromDictOfSameValues(sameDirContent)
    stringOfSameDirName = returnStringFromDictOfSameValues(sameDirName)
    stringOfSameFileName = returnStringFromDictOfSameValues(sameFileName)
    stringOfSameFileContent = returnStringFromDictOfSameValues(sameFileContent)
    with open('sameContentsAndNames.txt','w') as myFile:

        myFile.write("SAME DIR CONTENT : \n*********************************************************************************************************************************************************************************************\n{}".format(stringOfSameDirContent))
        myFile.write("SAME DIR NAME : \n*********************************************************************************************************************************************************************************************\n{}".format(stringOfSameDirName))
        myFile.write("SAME FILE NAME : \n*********************************************************************************************************************************************************************************************\n{}".format(stringOfSameFileName))
        myFile.write("SAME FILE CONTENT : \n*********************************************************************************************************************************************************************************************\n{}".format(stringOfSameFileContent))


allDirs = getAllDirs()
for dir in allDirs[::-1]:
    fileSizesInsideDir(dir)

writeToFile()

# getAllHashValuesFromDict()



# print("filePathAndFileSize", filePathAndFileSize)
