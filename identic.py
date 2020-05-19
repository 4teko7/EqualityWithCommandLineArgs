import argparse
import os
import hashlib
import collections

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
lookSizes = args.get('s') and not lookNames
dirList = args.get('***') if args.get('***') else ['.']



if(not lookFiles and not lookDirs):
    lookFiles = True

if(lookNames):
    lookSizes = False

if(lookContentsAndNames):
    lookNames = False
    lookContents = False
    lookContentsAndNames = True

if(lookNames and lookContents):
    lookNames = False
    lookContents = False
    lookContentsAndNames = True



if(not lookNames and not lookContentsAndNames):
    lookContents = True




fileAndDirPathAndSize = dict()
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
            for i in file:
                hashValue.update(i.encode("utf-8"))

    return hashValue.hexdigest()

def fileSizesInsideDir(dir):
    global fileAndDirPathAndSize,filePathAndFileContentHash,filePathAndFileNameHash,dirPathAndDirContentHash,dirPathAndDirNameHash
    files = os.listdir(dir)
    dirName = os.path.basename(dir)
    allNameHashes = list()
    allContentHashes = list()
    sumOfSizes = 0
    if(len(files) == 0):
        dirPathAndDirContentHash[dir] = getHashValue("",False)
        dirPathAndDirNameHash[dir] = getHashValue("",False)

    for file in files:
        filePath = os.path.join(dir, file)
        if os.path.isfile(filePath):
            sumOfSizes +=  os.path.getsize(filePath)
            fileAndDirPathAndSize[filePath] = os.path.getsize(filePath)
            filePathAndFileContentHash[filePath] = getHashValue(filePath,True)
            filePathAndFileNameHash[filePath] = getHashValue(os.path.basename(filePath),False)
            allContentHashes.append(filePathAndFileContentHash.get(filePath))
            allNameHashes.append(filePathAndFileNameHash.get(filePath))
        else:
            if(not dirPathAndDirContentHash.get(filePath) == None):
                sumOfSizes += fileAndDirPathAndSize.get(filePath)
                allContentHashes.append(dirPathAndDirContentHash.get(filePath))
                allNameHashes.append(dirPathAndDirNameHash.get(filePath))

    allContentHashes.sort()
    allNameHashes.sort()

    allNameHashes.insert(0, getHashValue(dirName, False))
    fileAndDirPathAndSize[dir] = sumOfSizes
    dirPathAndDirNameHash[dir] = getHashValue(allNameHashes, False)
    dirPathAndDirContentHash[dir] = getHashValue(allContentHashes,False)


def findAllSameValuesOfDictionary(myDict):
    tempSameValues = dict()
    sameValues = dict()

    for key,value in myDict.items():
        if tempSameValues.get(value) == None:
            tempSameValues[value] = [key]
        else:
            tempSameValues[value].append(key)

    for key , value in tempSameValues.items():
        if(len(value) > 1):
            value.sort()
            sameValues[key] = value
            

    allSortedDictValues = sameValues
    if(not lookSizes):
        allSortedDictValues = collections.OrderedDict(sorted(sameValues.items(), key=lambda x: x[1]))


    return allSortedDictValues



def returnStringFromDictOfSameValues(dict1):
    string = str()
    if(lookSizes and not lookNames):
        for key, value in dict1.items():
            for v in value:
                string += os.path.realpath(v) + "\t" + key.split(" ",1)[0] + "\n"
            string += "\n"
    else:
        for value in dict1.values():
            for v in value:
                string += os.path.realpath(v) + "\n"
            string += "\n"
    return string


def returnSameNamesWithSameContents(dictWithList):
    pathHashDict = dict()
    if(lookDirs):
        pathHashDict = dirPathAndDirNameHash
    else:
        pathHashDict = filePathAndFileNameHash

    sameContentAndNameLastOne = dict()
    for hash , pathList in dictWithList.items():
        sameNameAndContent = dict()
        for path in pathList:
            hashOfPath = pathHashDict.get(path)
            if sameNameAndContent.get(hashOfPath) == None:
                sameNameAndContent[hashOfPath] = [path]
            else:
                sameNameAndContent[hashOfPath].append(path)
        sameContentAndNameLastOne[hash] = sameNameAndContent.values()

    sameValues = dict()
    count = 0
    for valueList in sameContentAndNameLastOne.values():
        for values in valueList:
            if(len(values) > 1):
                values.sort()
                sameValues[count] = values
                count += 1

    allSortedDictValues = sameValues
    if(not lookSizes):
        allSortedDictValues = collections.OrderedDict(sorted(sameValues.items(), key=lambda x: x[1]))


    return allSortedDictValues
    


# Burada Hata var ayni size lari siliyor. guzelce append et.
def addSizeOfEntries(tempDict):
    sizedDict = dict()

    for key,value in tempDict.items():
        if(len(value) > 0):
            sizedDict[str(fileAndDirPathAndSize.get(value[0]))+ " " + value[0]] = value


    sizedDictionary = collections.OrderedDict(sorted(sizedDict.items(),key=lambda x: x[0].split(" ",1)[1], reverse=False))        
    sizedDictionary = collections.OrderedDict(sorted(sizedDictionary.items(),key=lambda x: int(x[0].split(" ",1)[0]), reverse=True))


    return sizedDictionary
# '/home/teko/Desktop/path', '-s','-cn','-d'
def writeResult(**kargs):
    if(lookDirs and lookContents):
        print(kargs.get("stringOfSameDirContent"))
    if(lookDirs and lookNames):
        print(kargs.get("stringOfSameDirName"))
    if(not lookDirs and lookNames):
        print(kargs.get("stringOfSameFileName"))
    if(not lookDirs and lookContents):
        print(kargs.get("stringOfSameFileContent"))
    if(lookDirs and lookContentsAndNames):
        print(kargs.get("stringOfSameNameAndContent"))
    if(not lookDirs and lookContentsAndNames):
        print(kargs.get("stringOfSameNameAndContent"))


def LastStep():
    sameDirContent = dict()
    sameDirName = dict()
    sameFileName = dict()
    sameFileContent = dict()
    sameNameAndContent = dict()

    if(lookSizes):
        sizedSameDirContent = dict()
        sizedSameFileContent = dict()
        sizedSameNameAndContent = dict() 

    if(lookContents and lookDirs):
        sameDirContent = findAllSameValuesOfDictionary(dirPathAndDirContentHash)
        if(lookSizes):
           sizedSameDirContent = addSizeOfEntries(sameDirContent)
    if(lookNames and lookDirs):
        sameDirName = findAllSameValuesOfDictionary(dirPathAndDirNameHash)
    if(lookNames and not lookDirs):
        sameFileName = findAllSameValuesOfDictionary(filePathAndFileNameHash)
    if(lookContents and not lookDirs):
        sameFileContent = findAllSameValuesOfDictionary(filePathAndFileContentHash)
        if(lookSizes):
           sizedSameFileContent = addSizeOfEntries(sameFileContent)
    if(lookContentsAndNames and lookDirs):
        sameDirContent = findAllSameValuesOfDictionary(dirPathAndDirContentHash)
        sameNameAndContent =  returnSameNamesWithSameContents(sameDirContent)
        if(lookSizes):
           sizedSameNameAndContent = addSizeOfEntries(sameNameAndContent)
    if(lookContentsAndNames and not lookDirs):
        sameFileContent = findAllSameValuesOfDictionary(filePathAndFileContentHash)
        sameNameAndContent =  returnSameNamesWithSameContents(sameFileContent)
        if(lookSizes):
           sizedSameNameAndContent = addSizeOfEntries(sameNameAndContent)

    


    if(lookSizes):
        stringOfSameDirContent = returnStringFromDictOfSameValues(sizedSameDirContent)
        stringOfSameFileContent = returnStringFromDictOfSameValues(sizedSameFileContent)
        stringOfSameNameAndContent = returnStringFromDictOfSameValues(sizedSameNameAndContent)
        writeResult(stringOfSameDirContent = stringOfSameDirContent,stringOfSameFileContent = stringOfSameFileContent,stringOfSameNameAndContent = stringOfSameNameAndContent)
    else:
        stringOfSameDirContent = returnStringFromDictOfSameValues(sameDirContent)
        stringOfSameDirName = returnStringFromDictOfSameValues(sameDirName)
        stringOfSameFileName = returnStringFromDictOfSameValues(sameFileName)
        stringOfSameFileContent = returnStringFromDictOfSameValues(sameFileContent)
        stringOfSameNameAndContent = returnStringFromDictOfSameValues(sameNameAndContent)
        writeResult(stringOfSameDirContent = stringOfSameDirContent,stringOfSameFileContent = stringOfSameFileContent,stringOfSameNameAndContent = stringOfSameNameAndContent,stringOfSameDirName = stringOfSameDirName,stringOfSameFileName = stringOfSameFileName)

    
    

allDirs = getAllDirs()
for dir in allDirs[::-1]:
    fileSizesInsideDir(dir)

LastStep()

