from multiprocessing import freeze_support
from GetApkData import GetApkData
from RandomClassification import RandomClassification
from HoldoutClassification import HoldoutClassification
import psutil

def main(MalwareDirectory, GoodwareDirectory, TestMal, TestGood, NCpuCores, TestSize, Option):
    '''
    Main function for malware detection classification

    :param String MalwareDirectory: name of the TRAINING malware directory in ApkDatasetDir (containing the apk or .data files).
    :param String GoodwareDirectory: name of the TRAINING goodware directory in ApkDatasetDir (containing the apk or .data files).
    :param String TestMal: name of the TESTING malware directory in ApkDatasetDir (containing the apk or .data files).
    :param String TestGood: name of the TESTING goodware directory in ApkDatasetDir (containing the apk or .data files).
    :param int/String NCpuCores: number of processes scheduled for data file creation.
    :param String Option: set this parameter for automatically execution.
    '''

    if Option=="1":
        OptionForGetApkData = raw_input("Do you want to regenerate missing Apk Data Files? [Y/N]").lower()
        if OptionForGetApkData == "y":
            GetApkData(NCpuCores, MalwareDirectory, GoodwareDirectory)
        RandomClassification(MalwareDirectory, GoodwareDirectory, TestSize, True)
    if Option=="2":
        if(TestMal== "")or(TestGood== ""):
            print "Some parameters are missing, hence exiting."
            return
        OptionForGetApkData = raw_input("Do you want to regenerate missing Apk Data Files? [Y/N]:").lower()
        if OptionForGetApkData == "y":
            GetApkData(NCpuCores, MalwareDirectory, GoodwareDirectory, TestMal, TestGood)
        HoldoutClassification(MalwareDirectory, GoodwareDirectory, TestMal, TestGood, True)

def GetCpuCoreCounts ():
    print "Set the number of cores to be used for DREBIN process (for using all CPU cores, just hit ENTER):"
    NCpuCores = raw_input()
    if not NCpuCores:
        NCpuCores = str(psutil.cpu_count())
    print 'Gonna deploy {} cpu cores'.format(NCpuCores)
    return NCpuCores

def GetTestingSize ():
    print "Set the testing size (must be in the range (0.0, 1.0):",
    TestingSize = raw_input()
    if not TestingSize:
        TestingSize = 0.3
    print 'Using a test size of {}'.format(TestingSize)
    return TestingSize

if __name__ == "__main__":
    freeze_support()
    print "Choose your option:"
    print "1: Random Split classification"
    print "2: Hold-out test set"
    print "Enter your option:",
    Option = raw_input()
    while Option != "1" and Option != "2":
        print "Error. Choose your option again (1 or 2):",
        Option = raw_input()
    if Option == "1":
        print "Input your Malware Directory, Goodware Directory (split by space), if you want to use default data, just hit ENTER:",
        DirNames = raw_input()
        if not DirNames:
            MalwareDirectory = '../data/apks/malware'
            GoodwareDirectory = '../data/apks/goodware'
            print 'Using default malware & goodware directories: {} and {}'.format(MalwareDirectory, GoodwareDirectory)
        else:
            MalwareDirectory, GoodwareDirectory = DirNames.split()
        NCpuCores = GetCpuCoreCounts()
        TestSize = GetTestingSize()
        main(MalwareDirectory, GoodwareDirectory, "", "", NCpuCores, TestSize, "1")
    if Option == "2":
        print "Input your Training Malware Directory, Training Goodware Directory, Testing Malware Directory, Testing Goodware Directory (split by space), if you want to use default data, just hit ENTER:",
        DirNames = raw_input()
        if not DirNames:
            TrainMalDir = '../data/small_proto_apks/malware'
            TrainGoodDir = '../data/small_proto_apks/goodware'
            TestMalDir = '../data/apks/malware'
            TestGoodDir = '../data/apks/goodware'
            print 'Using default training malware, training goodware, testing malware & testing goodware directories: {}, {}, {} & {}'\
                .format(TrainMalDir, TrainGoodDir, TestMalDir, TestGoodDir)
        else:
            TrainMalDir, TrainGoodDir, TestMalDir, TestGoodDir = DirNames.split()
        NCpuCores = GetCpuCoreCounts ()
        main(TrainMalDir, TrainGoodDir, TestMalDir, TestGoodDir, NCpuCores, "", "2")
