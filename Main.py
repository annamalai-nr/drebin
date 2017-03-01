from multiprocessing import freeze_support
from GetApkData import GetApkData
from BuildVocabulary import BuildVocabulary
from RandomClassification import RandomClassification
from HoldoutClassification import HoldoutClassification

def main(MalwareDirectory, GoodwareDirectory, TestBad, TestGood, ProcessNumber, Option):
    '''
    Main function for malware detection classification

    :param String MalwareDirectory: name of the TRAINING malware directory in ApkDatasetDir (containing the apk or .data files).
    :param String GoodwareDirectory: name of the TRAINING goodware directory in ApkDatasetDir (containing the apk or .data files).
    :param String TestBad: name of the TESTING malware directory in ApkDatasetDir (containing the apk or .data files).
    :param String TestGood: name of the TESTING goodware directory in ApkDatasetDir (containing the apk or .data files).
    :param int/String ProcessNumber: number of processes scheduled for data file creation.
    :param String Option: set this parameter for automatically execution.
    '''

    if Option=="1":
        OptionForGetApkData = raw_input("Do you want to regenerate missing Apk Data Files? [Y/N]")
        if OptionForGetApkData=="Y" or OptionForGetApkData == "y":
            GetApkData(ProcessNumber, MalwareDirectory, GoodwareDirectory)
        TotalFeatureDict = BuildVocabulary(MalwareDirectory, GoodwareDirectory, TestBad, TestGood)
        RandomClassification(MalwareDirectory, GoodwareDirectory, TotalFeatureDict, "binary")
    if Option=="2":
        if(TestBad=="")or(TestGood==""):
            print "There are some parameters not given, exit."
            return
        OptionForGetApkData = raw_input("Do you want to regenerate missing Apk Data Files? [Y/N]:")
        if OptionForGetApkData=="Y" or OptionForGetApkData == "y":
            GetApkData(ProcessNumber, MalwareDirectory, GoodwareDirectory, TestBad, TestGood)
        TotalFeatureDict = BuildVocabulary(MalwareDirectory, GoodwareDirectory, TestBad, TestGood)
        HoldoutClassification(MalwareDirectory, GoodwareDirectory, TestBad , TestGood, TotalFeatureDict, "binary")


if __name__ == "__main__":
    freeze_support()
    print "Choose your option:"
    print "1: Random Split classification"
    print "2: Hold-out test set"
    print "Enter you option:",
    Option = raw_input()
    while Option != "1" and Option != "2":
        print "Error. Choose your option again (1 or 2):",
        Option = raw_input()
    if Option == "1":
        print "Input your Malware Directory, Goodware Directory (split by space):",
        MalwareDirectory, GoodwareDirectory = raw_input().split()
        print "Set the number of processes scheduled for data file creation:",
        ProcessingNumber = raw_input()
        main(MalwareDirectory, GoodwareDirectory, "", "", ProcessingNumber, "1")
    if Option == "2":
        print "Input your Training Malware, Training Goodware, Testing Malware, Testing Goodware (split by space):",
        TrainBad, TrainGood, TestBad, TestGood = raw_input().split()
        print "Set the number of processes scheduled for data file creation:",
        ProcessingNumber = raw_input()
        main(TrainBad, TrainGood, TestBad, TestGood, ProcessingNumber, "2")
