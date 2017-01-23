import sys
#sys.path.append(sys.argv[1])
import androlyze
import zipfile
import string
import re
import os
import multiprocessing as mp
import networkx as nx

import BasicBlockAttrBuilder
import PScoutMapping
import Susi

from networkx.readwrite import json_graph
import json

def GetCFGs(ApkPath):
    '''
    Get the collection of CFGs of an apk

    :param String ApkPath: absolute path of the apk file
    '''

    CFGList = []

    try:
        a, d, dx = androlyze.AnalyzeAPK(ApkPath)
    except zipfile.BadZipfile:
        # if file is not an APK, may be a dex object
        try:
            d, dx = androlyze.AnalyzeDex(ApkPath)
        except Exception as e:
            # if file cannot be processed as an apk nor a dex object
            # it may be malformed file, then just return
            return CFGList
    except Exception as e:
        return CFGList

    #internally loads PSCOUT api-perm mapping dict
    PMap = PScoutMapping.PScoutMapping()
    #internally loads SUSI api-src & api-sink mapping dict
    SusiMap = Susi.SusiDictMaker()

    for method in d.get_methods():
        CFG = nx.DiGraph()
        index = 0

        SignatureText = dx.get_method_signature(method, predef_sign = androlyze.analysis.SIGNATURE_L0_0).get_string()
        SignatureText = string.replace(SignatureText, 'B[]', 'B[NULL]')
        SignatureList = re.sub(r"B\[(.*?)\]", "\g<1> ", SignatureText).split()

        g = dx.get_method(method)
        for BasicBlock in g.get_basic_blocks().get():
            Instructions = BasicBlockAttrBuilder.GetBasicBlockDalvikCode(BasicBlock)
            Apis, SuspiciousApiSet = BasicBlockAttrBuilder.GetInvokedAndroidApis(Instructions)
            Permissions = BasicBlockAttrBuilder.GetPermissions(Apis, PMap)
            Sources, Sinks = BasicBlockAttrBuilder.GetSusiSrcsSinks(Apis, SusiMap)

            CFG.add_node(BasicBlock.name, Sign = SignatureList[index])
            CFG.node[BasicBlock.name]['Instructions in BB'] = Instructions
            CFG.node[BasicBlock.name]['APIs'] = Apis
            CFG.node[BasicBlock.name]['Permissions'] = Permissions
            CFG.node[BasicBlock.name]['Sources & Sinks'] = (Sources, Sinks)
            index = index + 1

        for BasicBlock in g.get_basic_blocks().get():
            for Neighbor in BasicBlock.get_next():
                CFG.add_edge(BasicBlock.name, Neighbor[2].get_name())
        CFGList.append(CFG)

    return CFGList

def GetCFGString(ApkPath, OutputPath):
    '''
    Get the CFG string of an apk and write to a txt file

    :param String ApkPath: absolute path of the apk file
    :param String OutputPath: absolute path of the txt file
    '''

    CFGList = GetCFGs(ApkPath)

    if(len(CFGList) == 0):
        return
    else:
        Output = open(OutputPath, 'w+')
        try:
            for CFG in CFGList:
                SignatureString = ""

                SignatureDic = nx.get_node_attributes(CFG, 'Sign')
                for Node in CFG.nodes():

                    if (Node in SignatureDic):
                        SignatureString = SignatureString + SignatureDic[Node] + " "
                    
                    NeighborSignList = []
                    for Neighbor in nx.all_neighbors(CFG, Node):
                        if (Neighbor in SignatureDic):
                            NeighborSignList.append(SignatureDic[Neighbor])
                    if (len(NeighborSignList) > 0):
                        NeighborSignList.sort()
                        NeighborString = SignatureDic[Node] + "," + ";".join(NeighborSignList) + ";"
                        SignatureString = SignatureString + NeighborString + " "

                print >> Output, SignatureString

        finally:
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
            if Apk.endswith(".apk"):
                Output = os.path.join(DestinationSubDirAbs, Apk.replace('.apk','.txt'))
                if not os.path.exists(Output):
                    pool.apply_async(GetCFGString, args = (os.path.join(SourceSubDirAbs,Apk), Output, ))
    pool.close()
    pool.join()
    print "=========== CFG string Done ============="

if __name__ == "__main__":
    GetDataSet(sys.argv[2], sys.argv[3], sys.argv[4])

