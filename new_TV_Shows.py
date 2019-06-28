import os
import sys
import re

#filesDir = '/home/matt/Documents/testing/files/'
#showsDir = '/home/matt/Documents/testing/media/TV Shows/'

filesDir = '/home25/mrrobot/files/'
showsDir = '/home25/mrrobot/media/TV Shows/'

def getList( dirToGet ):
    newList = os.listdir(dirToGet)
    newList = sorted(newList)
    return newList

def displayAndGetSelection( existList ):
    print("Select a number this list or Enter your own selection: ")
    for f in existList:
        print('{}. {}'.format(existList.index(f), f))

    searchString = input()

    if ((searchString.isnumeric()) and int(searchString) >= 0 and int(searchString) <= len(existList)-1):
        searchString = existList[int(searchString)]
        
    return searchString


def getEpisodeNumberFromNewFile( searchString, itemToCheck):
    if re.match(searchString.replace(' ', '.'), itemToCheck.replace(' ', '.'), re.I):
        fileEpisodeMatchObject = re.search(r'^.*([Ss][0-9]+)([Ee][0-9]+)', itemToCheck.replace(' ', '.'), re.I)
        if (fileEpisodeMatchObject):
            return fileEpisodeMatchObject
        else:
            fileEpisodeMatchObject = re.search(r'^.*(\d\d\d\d\.)(\d\d\.)(\d\d)\.', itemToCheck.replace(' ', '.'), re.I)
            if (fileEpisodeMatchObject):
                return fileEpisodeMatchObject
    return None

def getDestinationBasePathOrCreate( searchString, existList ):
    for e in existList:
        if re.match(searchString.replace(' ', '.'), e.replace(' ', '.'),re.I):
            return showsDir+searchString+'/'
    if not os.path.exists(showsDir+searchString):
        os.mkdir(showsDir+searchString)
        print("Created new directory: {}".format(showsDir+searchString))
        return showsDir+searchString+'/'

    print("Couldn't find folder for {}, couldn't create folder at {}".format(searchString, showsDir+searchString))
    exit(1)

def checkDestPathForExistingEpisode( destPath, fileEpisodeMatchObject ):
    for e in os.listdir(destPath):
        if ''.join(fileEpisodeMatchObject.groups()).lower() in e.lower():
            return True
    return False

def isDirectory(fileToCheck, pathToFile):
    if os.path.isdir(pathToFile+fileToCheck):
        return True
    else:
        return False

def getFinalFileFromList(filesList):
    ''' We do the loop twice to make sure we get a file before resorting to extracting a rar'''
    for f in filesList:
        if f.endswith(('.mkv', '.mp4', '.avi', '.h264')):
            return f
    for f in filesList:
        if f.endswith(('.rar')):
            return f
    return False

def getFinalFileFromFile(fileToCheck):
    ''' If the file was in the root of the files directory we come here, no looping for 1 file'''
    if fileToCheck.endswith(('.mkv', '.mp4', '.avi', '.h264', '.rar')):
        return fileToCheck
    else:
        return False

def getFinalFileToParse(showPath, searchString, currentFile):
    ''' Main logic routine. Gets current episode and compares against existing folder. gets final file depending on if in a directory or not'''
    finalFile = False
    if not getEpisodeNumberFromNewFile(searchString, currentFile) or checkDestPathForExistingEpisode(showPath, getEpisodeNumberFromNewFile(searchString, currentFile)):
        # Either there's no S02E03 pattern in the file/folder matching our searchString or one already exists in the Show's destination directory. NEXT
        return None


    if (isDirectory(currentFile, filesDir)):
        finalFile = getFinalFileFromList(getList(filesDir+currentFile))
        if (finalFile):
            finalFile=filesDir+currentFile+'/'+finalFile
        else:
            print("Couldn't find file with applicable filetype in folder {}".format(filesDir+currentFile))
            return None

    elif not isDirectory(currentFile, filesDir):
        finalFile = getFinalFileFromFile(currentFile)
        if (finalFile):
            finalFile=filesDir+finalFile
        else:
            print("The file {} is not of an applicable filetype.".format(currentFile))
            return None

    return finalFile

def getFinalDestinationPath(showPath, finalFilenameWithPath):
    ''' if the dirname is the same as the files root then we name our new folder the name of the file in root. OTherwise we name it the folder that contains the new file'''
    dirname = os.path.dirname(finalFilenameWithPath)
    if (dirname == filesDir[:-1]):
        dirname = showPath + os.path.basename(finalFilenameWithPath)
        dirname = os.path.splitext(dirname)[0]
        if not os.path.exists(dirname):
            os.mkdir(dirname)
    else:
        dirname = showPath + os.path.basename(dirname)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
    return dirname 

def unrar(destPath, finalFilenameWithPath):
    '''Call 7zip to do some extracting for us'''
    print("Extracting {} to {}".format(finalFilenameWithPath, destPath))
    cmd = '7z x -y "{}" -o"{}" 2>&1 | tee --append {}'.format(finalFilenameWithPath, destPath, './7z_log_file')
    os.system( cmd )
    return

def hardlink(destPath, finalFilenameWithPath):
    '''The built-in didn't work for making a hardlink so we use the systems own command'''
    print("Creating link for {} in {}".format(finalFilenameWithPath, destPath))
    cmd = 'ln "{}" "{}"'.format(finalFilenameWithPath, destPath)
    os.system( cmd )
    return

def fullSeason(searchString, showsDir):
    existList = getList(showsDir)
    if searchString not in existList:
        os.mkdir(os.path.join(showsDir, searchString))
    baseShow = os.path.join(showsDir, searchString)
    existList = getList(baseShow)

    for currentFile in getList(filesDir):
        if (re.search(r'^.*([Ss]\d+)\.', currentFile)) and (re.match(searchString.replace(' ', '.'), currentFile.replace(' ', '.'),re.I)):
            print(currentFile)
            if currentFile not in existList:
                os.mkdir(os.path.join(showsDir, baseShow, currentFile))
            if os.path.isdir(os.path.join(filesDir, currentFile)):
                for root, dirs, files in os.walk(os.path.join(filesDir, currentFile)):
                    for name in files:
                        if name.endswith(('.mkv', '.h264', '.avi')):
                            if name not in getList(os.path.join(showsDir, baseShow, currentFile)):
                                hardlink(os.path.join(showsDir, baseShow, currentFile), os.path.join(root, name))
                    for name in files:
                        if name.endswith((".rar")):
                            if os.path.splitext(os.path.basename(name))[0] not in getList(os.path.join(showsDir, baseShow, currentFile)):
                                os.mkdir(os.path.join(showsDir, baseShow, currentFile, os.path.splitext(os.path.basename(name))[0]))
                                unrar(os.path.join(showsDir, baseShow, currentFile, os.path.splitext(os.path.basename(name))[0]), os.path.join(root, name))

def mainRoutine(showname):

    existingFoldersList = getList(showsDir)
    filesAndFoldersList = getList(filesDir)
    searchString = showname

    showPath = getDestinationBasePathOrCreate(searchString, existingFoldersList)

    for currentFile in filesAndFoldersList:
        finalFilenameWithPath = getFinalFileToParse(showPath, searchString, currentFile)

        if(finalFilenameWithPath):
            destPath = getFinalDestinationPath(showPath, finalFilenameWithPath)

            if (finalFilenameWithPath.lower().endswith('.rar')):
                unrar(destPath, finalFilenameWithPath)
            else:
                hardlink(destPath, finalFilenameWithPath)


if len(sys.argv) > 1:
    if sys.argv[1] == "fullseason":
        fullSeason(displayAndGetSelection(getList(showsDir)), showsDir)

    elif sys.argv[1] == "update" or sys.argv[1] == "auto":
        for showname in getList(showsDir):
            mainRoutine(showname)

    elif sys.argv[1] == "new":
            mainRoutine(displayAndGetSelection(getList(showsDir)))
    else:
        print("You can either give the argument 'fullseason', 'update', 'auto' or 'new'")

else:
        print("You can either give the argument 'fullseason', 'update' or 'new'")

