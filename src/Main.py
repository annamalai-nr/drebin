from GetApkData import GetApkData
from RandomClassification import RandomClassification
from HoldoutClassification import HoldoutClassification
import psutil, argparse, logging

logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger('main.stdout')

def main(Args, FeatureOption):
    '''
    Main function for malware and goodware classification
    :param args: arguments acquired from command lines(refer to ParseArgs() for list of args)
    :param FeatureOption: False
    '''

    MalDir= Args.maldir
    GoodDir= Args.gooddir
    NCpuCores= Args.ncpucores
    Model= Args.model
    NumFeatForExp = Args.numfeatforexp

    if Args.holdout == 0:
        #Perform Random Classification
        TestSize= Args.testsize
        Logger.debug("MalDir: {}, GoodDir: {}, NCpuCores: {}, TestSize: {}, FeatureOption: {}, NumFeatForExp: {}"
                     .format(MalDir, GoodDir, NCpuCores, TestSize, FeatureOption, NumFeatForExp))
        GetApkData(NCpuCores, MalDir, GoodDir)
        RandomClassification(MalDir, GoodDir, TestSize, FeatureOption, Model, NumFeatForExp)
    else:
        TestMalDir= Args.testmaldir
        TestGoodDir= Args.testgooddir
        Logger.debug("MalDir: {}, GoodDir: {}, TestMalDir: {}, TestGoodDir: {} NCpuCores: {}, FeatureOption: {}, NumFeatForExp: {}"
                     .format(MalDir, GoodDir, TestMalDir, TestGoodDir, NCpuCores,  FeatureOption, NumFeatForExp))
        GetApkData(NCpuCores, MalDir, GoodDir, TestMalDir, TestGoodDir)
        HoldoutClassification(MalDir, GoodDir, TestMalDir, TestGoodDir, FeatureOption, Model, NumFeatForExp)

def ParseArgs():
    Args =  argparse.ArgumentParser(description="Classification of Android Applications")
    Args.add_argument("--holdout", type= int, default= 0,
                      help="Type of Classification to be performed (0 for Random Classification and 1 for Holdout Classification")
    Args.add_argument("--maldir", default= "../data/small_proto_apks/malware",
                      help= "Absolute path to directory containing malware apks")
    Args.add_argument("--gooddir", default= "../data/small_proto_apks/goodware",
                      help= "Absolute path to directory containing benign apks")
    Args.add_argument("--testmaldir", default= "../data/apks/malware",
                      help= "Absolute path to directory containing malware apks for testing when performing Holdout Classification")
    Args.add_argument("--testgooddir", default="../data/apks/goodware",
                      help= "Absolute path to directory containing goodware apks for testing when performing Holdout Classification")
    Args.add_argument("--ncpucores", type= int, default= psutil.cpu_count(),
                      help= "Number of CPUs that will be used for processing")
    Args.add_argument("--testsize", type= float, default= 0.3,
                      help= "Size of the test set when split by Scikit Learn's Train Test Split module")
    Args.add_argument("--model",
                      help= "Absolute path to the saved model file(.pkl extension)")
    Args.add_argument("--numfeatforexp", type= int, default = 30,
                      help= "Number of top features to show for each test sample")
    return Args.parse_args()

if __name__ == "__main__":
    main(ParseArgs(), True)
