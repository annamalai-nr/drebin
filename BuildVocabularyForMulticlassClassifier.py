import os
import CommonModules as CM
import shutil
from BuildVocabulary import BuildVocabulary

def BuildVocabularyForMulticlassClassifier(VocabularyDirectory, MalwareFamilyFolders, GoodwareDirectory, TestBad, TestGood):
    '''
    Produce Vocabulary for MulticlassClassifier. Remove the Malware Family with less or equal to 30 samples.

    :param String VocabularyDirectory: absolute path of directory you want to store the Vocabulary in
    :param List MalwareFamilyFolders: list of Malware Family folders
    :param String GoodwareDirectory: absolute path of Goodware directory
    :param String TestBad: absolute path of Malware directory for test set
    :param String TestGood: absolute path of Goodware directory for test set

    :return OrderedDict(String:Int)  TotalFeatureDict: Dictionary that stores all features
    '''
    TempFolderForVocabularyCreation = os.path.join(VocabularyDirectory, "TempFolderForVocabularyCreation")
    if(os.path.isdir(TempFolderForVocabularyCreation) == False):
        os.mkdir(TempFolderForVocabularyCreation)
    for Folder in MalwareFamilyFolders:
        DataFilePaths = CM.ListFiles(Folder, ".data")
        if(len(DataFilePaths) <= 30):
            shutil.move(Folder, TempFolderForVocabularyCreation)
            continue
        for DataFilePath in DataFilePaths:
            shutil.copy(DataFilePath, TempFolderForVocabularyCreation)
    TotalFeatureDict = BuildVocabulary(VocabularyDirectory, TempFolderForVocabularyCreation, GoodwareDirectory, TestBad, TestGood)
    os.rmdir(TempFolderForVocabularyCreation)
    return TotalFeatureDict