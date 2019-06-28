import os
import sys
import re

filesDir = '/home25/mrrobot/files/'
moviesDir = '/home25/mrrobot/media/Movies/'
#filesDir = '/home/matt/.bin/seedbox_scripts/files/'
#moviesDir = '/home/matt/.bin/seedbox_scripts/movies/'

def getmovieName():
    if len(sys.argv) > 1:
        movieName = sys.argv[1]
    else:
        movieName = input("Enter Search Terms for your movie: ")

    return movieName

def listFiles(dirToList):
    try:
        files_list = [f for f in os.listdir(dirToList)]
        return files_list
    except FileNotFoundError:
        print("Could not find the folder: {}".format(dirToList))
        exit(1)

def matchMovie(movieName, filesList):
    for f in filesList:
        count = 0
        for word in movieName.split():
            if not (re.search(word, f, flags=re.I)):
                break
            elif (re.search(word, f, flags=re.I)):
                count = count + 1
                if count == len(movieName.split()):
                    return f
    return None

def checkExisingOrGetNewFile():
    '''Make sure file hasnt already been extracted. If not, get the file to extract'''

    if (matchMovie(movieName, existList)):
        print("The file \"{}\" alright exists in {}".format(movieName, moviesDir))
        exit(0)

    elif (matchMovie(movieName, filesList)):
        fileToParse = matchMovie(movieName, filesList)
        fileToParse = (os.path.join(filesDir, fileToParse))
        return fileToParse

    else:
        print("The movie {} could not be found.".format(movieName))
        exit(0)

def isDirectory(fileToParse):
    if (os.path.isdir(fileToParse)):
        return True
    elif (os.path.isfile(fileToParse)):
        return False
    else:
        print("{} is not a directory or a file. Exiting.".format(fileToParse))
        exit(0)

def walkDirAndGetFile(fileToParse):
    for root, dirs, files in os.walk(fileToParse):
        for name in files:
            if (name.lower().endswith(('.mkv', '.mp4', '.avi', '.h264'))):
                linkFile(os.path.join(root, name))
                exit (0)
            elif (name.lower().endswith(('.rar'))):
                return os.path.join(root, name)
    print("No applicable filetype found in {}. Exiting".format(os.path.join(root, name)))
    exit(1)

def linkFile(fileToParse):
    # If the file doesn't come inside a folder
    if (fileToParse.lower().endswith(('.mkv', '.mp4', '.avi', '.h264'))):
        if not has_own_directory(fileToParse):
            file, ext = os.path.splitext(os.path.basename(fileToParse))
            dir_path = os.path.join(moviesDir, file)
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)
            link_path = os.path.join(dir_path, os.path.basename(fileToParse))
            os.link(fileToParse, link_path)
            print("Linked {} to moviesDir".format(fileToParse))
            return

    # If the file is normal and comes inside a folder
        dir_path = os.path.join(moviesDir, os.path.basename(os.path.dirname(fileToParse)))
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        link_path = os.path.join(dir_path, os.path.basename(fileToParse))
        os.link(fileToParse, link_path)
        print("Linked {} to moviesDir".format(fileToParse))
        return
            
    else:
        print("This file {} isn't an mkv, mp4, avi, or h264".format(fileToParse))
        exit(1)
    return


def has_own_directory(fileToParse):
    """Check if containing folder is the files directory"""
    files_basename = os.path.basename(os.path.dirname(filesDir))
    movie_basename = os.path.basename(os.path.dirname(fileToParse))
    if files_basename == movie_basename:
        return False
    return True

def unrarFile(fileToUnrar):
    tmp_log_file='./tmp_log_file'
    extractPath = (os.path.join(moviesDir, os.path.basename(os.path.dirname(fileToUnrar))))
    if not (os.path.isdir(extractPath)):
        os.mkdir(extractPath)
    cmd = '7z x -y "{}" -o"{}" 2>&1 | tee {}'.format(fileToUnrar, extractPath, tmp_log_file)
    os.system( cmd )
    exit (0)

movieName = getmovieName()
filesList = listFiles(filesDir)
existList = listFiles(moviesDir)
fileToParse = checkExisingOrGetNewFile()

if isDirectory(fileToParse):
    fileToUnrar = walkDirAndGetFile(fileToParse)
    unrarFile(fileToUnrar)

else:
    linkFile(fileToParse)
    exit(0)











