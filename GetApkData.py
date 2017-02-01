import sys
reload(sys)
sys.path.append("Modules")
sys.path.append("Androguard")
sys.setdefaultencoding("utf-8")

import os
import multiprocessing as mp

import CommonModules as CM
import PScoutMapping as PScoutMapping
from ProcessingDataForGetApkData import ProcessingDataForGetApkData

def GetApkData(ProcessNumber, *ApkDirectoryPaths):
    '''
    Get Apk data dictionary for all Apk files under ApkDirectoryPath and store them in ApkDirectoryPath
    Used for next step's classification

    :param Tuple<string> *ApkDirectoryPaths: absolute path of the directories contained Apk files
    '''
    ApkFileList = []
    for ApkDirectoryPath in ApkDirectoryPaths:
        ApkFileList.extend(CM.ListApkFiles(ApkDirectoryPath))
        ApkFileList.extend(CM.ListFiles(ApkDirectoryPath, ""))
    #Because some apk files may not have extension....
    original_cwd = os.getcwd()
    os.chdir(os.path.join(original_cwd, "Modules"))
    ''' Change current working directory to import the mapping '''
    PMap = PScoutMapping.PScoutMapping()
    os.chdir(original_cwd)
    pool = mp.Pool(int(ProcessNumber))
    ProcessingResults = []
    ScheduledTasks = []
    ProgressBar = CM.ProgressBar()
    for ApkFile in ApkFileList:
        if CM.FileExist(os.path.splitext(ApkFile)[0]+".data"):
            pass
        else:
            #ProcessingDataForGetApkData(ApkDirectoryPath, ApkFile, PMap)
            ApkDirectoryPath = os.path.split(ApkFile)[0]
            ScheduledTasks.append(ApkFile)
            ProcessingResults = pool.apply_async(ProcessingDataForGetApkData, args = (ApkDirectoryPath, ApkFile, PMap),callback=ProgressBar.CallbackForProgressBar)
    pool.close()
    if(ProcessingResults):
        ProgressBar.DisplayProgressBar(ProcessingResults, len(ScheduledTasks), type="hour")
    pool.join()

    return