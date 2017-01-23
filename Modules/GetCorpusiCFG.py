import sys
sys.path.append(sys.argv[1])
import androlyze
import zipfile
import string
import re
import os
import multiprocessing as mp
import networkx as nx
import matplotlib.pyplot as plt

import BasicBlockAttrBuilder
import PScoutMapping
import Susi

from networkx.readwrite import json_graph
import json

def GetBBLabel(BasicBlock):
    '''
    Get (unique) label of a basic block

    :param DVMBasicBlock BasicBlock
    :rtype String 
    '''

    Method = BasicBlock.method
    return (Method.get_class_name(), Method.get_name(), Method.get_descriptor(), BasicBlock.name)

def GetIntraChildren(BasicBlock):
    '''
    Get labels of the basic blocks that are children of the input basic block within the method

    :param DVMBasicBlock BasicBlock
    :return Children: a list of labels of basic blocks 
    :rtype List
    '''

    Children = []
    for Child in BasicBlock.get_next():
        Children.append(GetBBLabel(Child[2]))
    return Children

def GetInterChildren(BasicBlock, dx):
    '''
    Given a basic block, find the calls to external methods and return the label of the first basic block in these methods

    :param DVMBasicBlock BasicBlock
    :param VMAnalysis dx
    :return Children: a list of labels of basic blocks 
    :rtype List
    '''

    Children = []
    for Call in BasicBlock.method.XREFto.items:
        RemoteMethod = dx.get_method(Call[0])
        #iterate over the offsets of the call instructions and check
        #if the offset is within the limits of the bb
        for Path in Call[1]:
            if (BasicBlock.get_start() <= Path.get_idx() and BasicBlock.get_end() >= Path.get_idx()):
                try:
                    RemoteBasicBlock = RemoteMethod.basic_blocks.get().next()
                    Children.append(GetBBLabel(RemoteBasicBlock))
                except StopIteration:
                    pass
    return Children


def GetiCFG(ApkPath):
    '''
    Get iCFG of an apk

    :param String ApkPath: absolute path of the apk file
    :return iCFG
    :rtype DiGraph
    '''

    iCFG = nx.DiGraph()
    try:
        a, d, dx = androlyze.AnalyzeAPK(ApkPath)
    except zipfile.BadZipfile:
        # if file is not an APK, may be a dex object
        try:
            d, dx = androlyze.AnalyzeDex(ApkPath)
        except Exception as e:
            # if file cannot be processed as an apk nor a dex object
            # it may be malformed file, then just return
            return iCFG
    except Exception as e:
        return iCFG

    #internally loads PSCOUT api-perm mapping dict
    PMap = PScoutMapping.PScoutMapping()
    #internally loads SUSI api-src & api-sink mapping dict
    SusiMap = Susi.SusiDictMaker()

    for method in d.get_methods():
        index = 0

        # get the signature list corresponding to basic blocks
        SignatureText = dx.get_method_signature(method, predef_sign = androlyze.analysis.SIGNATURE_L0_0).get_string()
        SignatureText = string.replace(SignatureText, 'B[]', 'B[NULL]')
        SignatureList = re.sub(r"B\[(.*?)\]", "\g<1> ", SignatureText).split()

        g = dx.get_method(method)
        for BasicBlock in g.get_basic_blocks().get():
            Label = GetBBLabel(BasicBlock)
            Instructions = BasicBlockAttrBuilder.GetBasicBlockDalvikCode(BasicBlock)
            Apis = BasicBlockAttrBuilder.GetInvokedAndroidApis(Instructions)
            Permissions = BasicBlockAttrBuilder.GetPermissions(Apis, PMap)
            Sources, Sinks = BasicBlockAttrBuilder.GetSusiSrcsSinks(Apis, SusiMap)

            iCFG.add_node(Label, Sign = SignatureList[index])
            iCFG.node[Label]['Instructions in BB'] = Instructions
            iCFG.node[Label]['APIs'] = Apis
            iCFG.node[Label]['Permissions'] = Permissions
            iCFG.node[Label]['Sources & Sinks'] = (Sources, Sinks)
            
            index = index + 1

            IntraChildren = GetIntraChildren(BasicBlock)
            # specify the edges as "Intra"
            iCFG.add_edges_from([(Label, Child) for Child in IntraChildren], Location='Intra')

            InterChildren = GetInterChildren(BasicBlock, dx)
            if (len(InterChildren) > 0):
                # specify the calling node as "Call"
                iCFG.node[Label]['Call'] = True
                for Child in InterChildren:
                    # specify the edges as "Inter" and the called nodes as "Called"
                    iCFG.add_edge(Label, Child, Location='Inter')
                    iCFG.node[Child]['Called'] = True

    return iCFG

def GetiCFGString(ApkPath, OutputPath, Direct, Degree):
    '''
    Get the iCFG string of an apk and write to a txt file

    :param String ApkPath: absolute path of the apk file
    :param String OutputPath: absolute path of the txt file
    :param String/boolean Direct: whether to treat iCFG as direct or indirected graph
    :param String/int Degree: Degree of neighbors to condider for calling and called node
    '''

    # preprocess parameter Direct and Degree
    if (type(Direct) == str):
        if (Direct == 'True'):
            Direct = True
        elif (Direct == 'False'):
            Direct = False
        else:
            print "Paramater Direct should be True or False"
            return

    if (type(Degree) == str):
        Degree = int(Degree)
    if (Degree < 0):
        print "Paramater Degree should be great or equal to zero"
        return

    # if iCFG is an empty graph, return 
    iCFG = GetiCFG(ApkPath)
    if(len(iCFG.nodes()) == 0):
        return

    else:
        # if Direct is false, convert the iCFG to undirect graph
        if(not Direct):
            iCFG = nx.Graph(iCFG)

        Output = open(OutputPath, 'w+')
        try:
            for Node in iCFG.nodes():
                # 0-degree neighbor
                SignatureString = iCFG.node[Node]['Sign']

                # 1-degree neighbor
                if (Degree >= 1):
                    NeighborList = iCFG.neighbors(Node)
                    NeighborSignList = [iCFG.node[Neighbor]['Sign'] for Neighbor in NeighborList]
                    if (len(NeighborSignList) > 0):
                        NeighborSignList.sort()
                        SignatureString = SignatureString + " " + iCFG.node[Node]['Sign'] + ","
                        SignatureString = SignatureString + ";".join(NeighborSignList) + ";"

                        # multi-degree neighbor (>=2), only for calling nodes or called nodes
                        if('Called' in iCFG.node[Node] or 'Call' in iCFG.node[Node]):
                            while (Degree >= 2):
                                MDNeighborList = []
                                for Neighbor in NeighborList:
                                    MDNeighborList.extend(iCFG.neighbors(Neighbor))
                                
                                MDNeighborSignList = [iCFG.node[Neighbor]['Sign'] for Neighbor in MDNeighborList]
                                if (len(MDNeighborSignList) > 0):
                                    MDNeighborSignList.sort()
                                    SignatureString = SignatureString + " " + iCFG.node[Node]['Sign'] + ","
                                    SignatureString = SignatureString + ";".join(MDNeighborSignList) + ";"

                                NeighborList = MDNeighborList
                                Degree = Degree - 1

                print >> Output, SignatureString
        except Exception as e:
            print e
        finally:
            Output.close()

def GetDataSet(SourceRootDir, DestinationRootDir, ProcessNo, Direct, Degree):
    '''
    Construct a collection of corpuses whose structure is: 
    DestinationRootDir/corpus catelogies (malware and goodware)/txt files containing CFG strings of each apk in the catelogy
    The structure of SourceRootDir is also two-level
    SourceRootDir/corpus catelogies (malware and goodware)/apks in the catelogy

    :param String SourceRootDir: absolute path of the root directory of different catelogies of apks
    :param String DestinationRootDir: absolute path of the dataset
    :param int/String ProcessNo: number of processes scheduled
    :param String/boolean Direct: whether to treat iCFG as direct or indirected graph
    :param String/int Degree: Degree of neighbors to condider for calling and called node
    '''

    # preprocess parameter ProcessNo
    if(type(ProcessNo) == str):
        ProcessNo = int(ProcessNo)

    print "=========== Extracting iCFG string ============="

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
                    pool.apply_async(GetiCFGString, args = (os.path.join(SourceSubDirAbs,Apk), Output, Direct, Degree, ))
    pool.close()
    pool.join()
    print "=========== iCFG string Done ============="

if __name__ == "__main__":
    GetDataSet(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
