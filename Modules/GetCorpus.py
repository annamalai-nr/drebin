import sys
sys.path.append(sys.argv[1])
import androlyze
import zipfile
import string
import re
import os
import multiprocessing as mp
import time

def GetCFGString(ApkPath, OutputPath):
    '''
    Get the CFG string of an apk and write to a txt file

    :param String ApkPath: absolute path of the apk file
    :param String OutputPath: absolute path of the txt file
    '''
    try:
             StartTime=time.time()
             a, d, dx = androlyze.AnalyzeAPK(ApkPath)
    except zipfile.BadZipfile:
        # if file is not an APK, may be a dex object
        try:
            d, dx = androlyze.AnalyzeDex(ApkPath)
        except Exception as e:
            # if file cannot be processed as an apk nor a dex object
            # it may be malformed file, then just return
            return
    except Exception as e:
        return
            
    Output = open(OutputPath, 'w+')
    try:
        for method in d.get_methods():
            SignatureText = dx.get_method_signature(method, predef_sign = androlyze.analysis.SIGNATURE_L0_0).get_string()
            SignatureText = string.replace(SignatureText, 'B[]', 'B[NULL]')
            ProcessedText = re.sub(r"B\[(.*?)\]", "\g<1> ", SignatureText)
            print >> Output, ProcessedText

    finally:
            EndTime=time.time()
            TimeOutputPath = open("time.txt", 'a')
            TimeOutputPath.write("GetCFGString for" + ApkPath + " Running Time: "+str(EndTime-StartTime)+' seconds\n')
            TimeOutputPath.close()
            Output.close()
    
def GetDataSet(SourceRootDir, DestinationRootDir, ProcessNo):
    '''
    Construct a collection of corpuses whose structure is: 
    DestinationRootDir/corpus catelogies (malware and goodware)/txt files containing CFG strings of each apk in the catelogy
    The structure of SourceRootDir is also two-level
    SourceRootDir/corpus catelogies (malware and goodware)/apks in the catelogy

    :param String SourceRootDir: absolute path of the root directory of different catelogies of apks
    :param String DestinationRootDir: absolute path of the dataset
    :param int/String ProcessNo: number of processes scheduled
    '''

    # preprocess parameter ProcessNo
    if(type(ProcessNo) == str):
        ProcessNo = int(ProcessNo)

    print "=========== Extracting CFG string ============="
    pool = mp.Pool(ProcessNo)
    for SubDir in os.listdir(SourceRootDir):
        SourceSubDirAbs = os.path.join(SourceRootDir, SubDir)
        DestinationSubDirAbs = os.path.join(DestinationRootDir, SubDir)
        if not os.path.exists(DestinationSubDirAbs):
            os.makedirs(DestinationSubDirAbs)
        for Apk in os.listdir(SourceSubDirAbs):
            if True:
                    Output = os.path.join(DestinationSubDirAbs, Apk.replace('.apk','.txt'))
                    if not os.path.exists(Output):
                        pool.apply_async(GetCFGString, args = (os.path.join(SourceSubDirAbs,Apk), Output, ))
    pool.close()
    pool.join()
    print "=========== CFG string Done ============="        


if __name__ == "__main__":
    GetDataSet(sys.argv[2], sys.argv[3], sys.argv[4])