# -*- coding: utf-8 -*-
""" Some common modules for this project."""
import os
import sys
import json
import time
import itertools
import collections
import pickle
import shutil

import numpy as np
import scipy.sparse
import scipy.io
import networkx as nx
from networkx.readwrite import json_graph

import logging
logging.basicConfig(level=logging.INFO,filename="LogFile.log",filemode="a",
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')
ErrorHandler = logging.StreamHandler()
ErrorHandler.setLevel(logging.ERROR)
ErrorHandler.setFormatter(logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s'))
logger = logging.getLogger()
logger.addHandler(ErrorHandler)


import Modules.progressbar.progressbar as progressbar
import Modules.progressbar.widgets as progressbar_widgets

class ProgressBar(object):
    def __init__(self):
        self.TotalResults = []
        self.NumberOfFinishedResults = 0
 
    def Update(self):
        self.ProgressBar.update(self.NumberOfFinishedResults)
        return 

    def CallbackForProgressBar(self, res = ''):        
        """
    Callback function for pool.async if the progress bar needs to be displayed.
    Must use with DisplayProgressBar function.

    :param multiprocessing.pool.AsyncResult res: Result got from callback function in pool.async.
        """
        self.NumberOfFinishedResults += 1
        self.TotalResults.append(res)
        return

    def DisplayProgressBar(self, ProcessingResults, ExpectedResultsSize, CheckInterval = 1, type = "minute"):
        '''
    Display a progress bar for multiprocessing. This function should be used after pool.close(No need to use pool.join anymore). 
    The call back function for pool.async should be set as CallbackForProgressBar.

    :param multiprocessing.pool.AsyncResult ProcessingResults: Processing results returned by pool.async.
    :param int ExpectedResultsSize: How many result you will reveive, i.e. the total length of progress bar.
    :param float CheckInterval: How many seconds will the progress bar be updated. When it's too large, the main program may hang there.
    :param String type: Three types: "minute", "hour", "second"; corresponds displaying iters/minute iters/hour and iters/second.
        '''
        self.ProcessingResults = ProcessingResults
        ProgressBarWidgets = [progressbar_widgets.Percentage(),
               ' ', progressbar_widgets.Bar(),
               ' ', progressbar_widgets.SimpleProgress(),
               ' ', progressbar_widgets.Timer(),
               ' ', progressbar_widgets.AdaptiveETA()]
        self.ProgressBar = progressbar.ProgressBar(ExpectedResultsSize, ProgressBarWidgets)
        self.StartTime = time.time()
        PreviousNumberOfResults = 0
        self.ProgressBar.start()
        while self.ProcessingResults.ready()==False:
            self.Update()
            time.sleep(CheckInterval)
        time.sleep(CheckInterval)
        self.Update()
        self.ProgressBar.finish()
        self.EndTime = time.time()
        print "Processing finished."
        #print "Processing results: ", self.TotalResults
        print "Time Elapsed: %.2fs, or %.2fmins, or %.2fhours" % ((self.EndTime-self.StartTime),(self.EndTime-self.StartTime)/60,(self.EndTime-self.StartTime)/3600)
        logger.info("Processing finished.")
        logger.info("Processing results: "+ str(self.TotalResults))
        logger.info("Time Elapsed: %.2fs, or %.2fmins, or %.2fhours" % ((self.EndTime-self.StartTime),(self.EndTime-self.StartTime)/60,(self.EndTime-self.StartTime)/3600))
        return 
        #for i in progressbar.tqdm(range(ExpectedResultsSize),type=type):#Three types: iters/minute iters/hour and iters/second
        #while ProcessingResults.ready()==False:#While processing doesn't finish.
            #if self.NumberOfFinishedResults>PreviousNumberOfResults:
            #    PreviousNumberOfResults += 1
            #    break   
            #else:
        #    time.sleep(CheckInterval)#Define how many seconds between each check.
        
class DefaultOrderedDict(collections.OrderedDict):
    # Source: http://stackoverflow.com/a/6190500/562769
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
           not isinstance(default_factory, collections.Callable)):
            raise TypeError('first argument must be callable')
        collections.OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return collections.OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               collections.OrderedDict.__repr__(self))

def ListApkFiles(ApkDirectory):
    '''
Get the Apk file names for an ApkDirectory in a sorted order. Rerurn an empty list if ApkDirectory=="".

:param String ApkDirectory: absolute path of a apk file directory
:return ListOfApkFiles: The list of absolute paths of Apks under ApkDirectory
:rtype List[String]
    '''
    ListOfApkFiles=[]
    if(ApkDirectory==""):
        raise ValueError('Directory is empty!')
    filenames = os.listdir(ApkDirectory)
    for filename in filenames:
        #list filenames 
        #get the absolute path for the files
        AbsolutePath=os.path.abspath(os.path.join(ApkDirectory, filename))
        #get the absolute path for the files
        if os.path.splitext(filename)[1]==".apk":
            if os.path.isfile(AbsolutePath):
                ListOfApkFiles.append(AbsolutePath)
    return sorted(ListOfApkFiles)

def ListFiles(Directory, Extension):
    '''
    Given an extension, get the file names for a Directory in a sorted order. Rerurn an empty list if Directory == "".

    :param String Directory: absolute path of a file directory
    :param String Extension: Extension of the files you want. Better include "." in the Extension
    :return ListOfFiles: The list of absolute paths of the files you want under Directory
    :rtype List[String]
    '''
    ListOfFiles=[]
    if(Directory == "" or Directory == []):
        return []
    if(type(Directory) != list and os.path.isdir(Directory) == False):
        raise ValueError(Directory, 'Directory is not a directory!')
    if(type(Extension)!=str):
        raise ValueError(Extension, 'Extension is not a string!')
    if(Extension):
        if(Extension[0] != "."):
            Extension = "." + Extension[0]
    if type(Directory) == list:
        Directories = Directory
        for Directory in Directories:
                filenames = os.listdir(Directory)
                for filename in filenames:
                    #list filenames 
                    #get the absolute path for the files
                    AbsolutePath=os.path.abspath(os.path.join(Directory, filename))
                    #get the absolute path for the files
                    if os.path.splitext(filename)[1]==Extension:
                        if os.path.isfile(AbsolutePath):
                            ListOfFiles.append(AbsolutePath)
    else:
        filenames = os.listdir(Directory)
        for filename in filenames:
            #list filenames 
            #get the absolute path for the files
            AbsolutePath=os.path.abspath(os.path.join(Directory, filename))
            #get the absolute path for the files
            if os.path.splitext(filename)[1]==Extension:
                if os.path.isfile(AbsolutePath):
                    ListOfFiles.append(AbsolutePath)
    return sorted(ListOfFiles)

def ListAllFiles(Directory, Extension):
    '''
    Given an extension, get the file names for a Directory and all its sub-directories in a sorted order. Rerurn an empty list if Directory == "".

    :param String Directory: absolute path of a file directory
    :param String Extension: Extension of the files you want. Better include "." in the Extension
    :return ListOfFiles: The list of absolute paths of the files you want under Directory
    :rtype List[String]
    '''
    ListOfFiles=[]
    if(Directory == ""):
        raise ValueError(Directory, 'Directory is empty!')
    if(os.path.isdir(Directory) == False):
        raise ValueError(Directory, 'Directory is not a directory!')
    if(type(Extension)!=str):
        raise ValueError(Extension, 'Extension is not a string!')
    if(Extension):
        if(Extension[0] != "."):
            Extension = "." + Extension[0]
    for root, dirs, files in os.walk(Directory):
        for filename in files:
            #list filenames 
            #get the absolute path for the files
            AbsolutePath = os.path.join(root, filename)
            #get the absolute path for the files
            if os.path.splitext(filename)[1] == Extension:
                if os.path.isfile(AbsolutePath):
                    ListOfFiles.append(AbsolutePath)
    return sorted(ListOfFiles)

def ListDirs(Directory):
    '''
    Get all sub-directory paths for a Directory in a sorted order. Rerurn an empty list if Directory == "". Modified from ListFiles(which means variable names remain the same...)

    :param String Directory: absolute path of a file directory
    :return ListOfFiles: The list of absolute paths of the sub-directories you want under the Directory
    :rtype List[String]
    '''
    ListOfFiles=[]
    if(Directory == ""):
        raise ValueError(Directory, 'Directory is empty!')
    if(os.path.isdir(Directory) == False):
        raise ValueError(Directory, 'Directory is not a directory!')
    filenames = os.listdir(Directory)
    for filename in filenames:
        #list filenames 
        #get the absolute path for the files
        AbsolutePath=os.path.abspath(os.path.join(Directory, filename))
        #get the absolute path for the files
        if os.path.isdir(AbsolutePath):
            ListOfFiles.append(AbsolutePath)
    return sorted(ListOfFiles)
    
    
def FileExist(FilePath):
    '''
    Given file path, determine a file exist or not.

    :param String FilePath: absolute path of a file or directory
    :rtype Boolean
    '''
    if os.path.exists(FilePath)==True:
        return True
    else:
        #if os.path.isdir(ApkFilePath)==False:
        #    if(os.path.basename(ApkFilePath)) in os.listdir(os.getcwd()):
        #        return True
        return False

def RemoveDirectory(Folder):
    '''
    Given Folder path, remove this folder(include all content inside).

    :param String Folder: absolute path of a directory
    :rtype Boolean
    '''
    if(FileExist(Folder) == False):
        raise IOError("Directory not found!")
    else:
        shutil.rmtree(Folder)


def ExportToJson(AbsolutePath, Content):
    '''
    Export something to json file. 
    Will automatic convert Set content into List.

    :param String AbsolutePath: absolute path to store the json file
    :param Variant Content: something you want to export
    '''
    try:
        if(isinstance(Content,set)):
            Content = list(Content)
        #if(isinstance(Content, collections.defaultdict)):
        #    Content = dict(Content)
        f=open(AbsolutePath,"wb")
        # json.dump(Content, f, indent=4)
        for Key,Val in Content.items():
            for V in Val:
                print >>f, str(Key)+'_'+str(V)

    except Exception as e:
        print "Json data writing Failed."
        logger.error(e)
        logger.error("Json data writing Failed.")
        if "f" in dir():
            f.close()
        #sys.exit("Json data writing Failed.")
    else:
        logger.info("Json data of "+AbsolutePath+" written successfully.")     
        f.close()


def ExportToPkl(AbsolutePath,Content):
    '''
    Export something to pickle file. 
    Will automatic convert Set content into List.

    :param String AbsolutePath: absolute path to store the json file
    :param Variant Content: something you want to export
    '''
    try:
        if(isinstance(Content, set)):
            Content = list(Content)
        #if(isinstance(Content, collections.defaultdict)):
        #    Content = dict(Content)
        f=open(AbsolutePath, "wb")
        pickle.dump(Content, f)
    except:
        print "Pickle data writing Failed."
        logger.error("Pickle data writing Failed.")
        if "f" in dir():
            f.close()
        #sys.exit("Json data writing Failed.")
    else:
        logger.info("Pickle data of " + AbsolutePath + " written successfully.")     
        f.close()

def ImportFromPkl(AbsolutePath):
    '''
    Import something from pickle file. 

    :param String AbsolutePath: absolute path of the pickle file
    :return Content: Content in the pickle file
    :rtype Variant
    '''    
    try:
        File = open(AbsolutePath,"rb")
        Content = pickle.load(File)
    except:
        logger.error("Pickle data loading Failed.")
        if "File" in dir():
            File.close()
        #sys.exit("Json data loading Failed.")    
    else:
        logger.info("Pickle data of "+AbsolutePath+" loaded successfully.")
        File.close()
        return Content


def ExportToJsonNodeLinkData(AbsolutePath,GraphContent):
    '''
    Export graph node link date to json file. 

    :param String AbsolutePath: absolute path to store the json file
    :param nxGraph GraphContent: some graph you want to export
    '''    
    try:
        f=open(AbsolutePath,"wb")
        Content=json_graph.node_link_data(GraphContent)
        json.dump(Content,f,indent=4)
    except Exception as e:
        print e
        logger.error("JsonNodeLinkData writing Failed.")
        if "f" in dir():
            f.close()
        #sys.exit("JsonNodeLinkData writing Failed.")
    else:
        logger.info("JsonNodeLinkData of "+AbsolutePath+" written successfully.")
        f.close()

def ExportToGML(AbsolutePath, GraphContent):
    '''
    Export graph node link date to json file. 

    :param String AbsolutePath: absolute path to store the json file
    :param nxGraph GraphContent: some graph you want to export
    '''    
    try:
        nx.write_gml(GraphContent, AbsolutePath)
    except:
        logger.error("JsonNodeLinkData writing Failed.")
        #sys.exit("JsonNodeLinkData writing Failed.")
    else:
        logger.info("JsonNodeLinkData of "+AbsolutePath+" written successfully.")


def ImportFromJsonNodeLinkData(AbsolutePath):
    '''
Import graph node link date from json file.

:param String AbsolutePath: absolute path of the json file
:return GraphContent: Graph content in the json file
:rtype nxGraph
    '''    
    try:
        f=open(AbsolutePath,"rb")
        Content=json.load(f)
        GraphContent=json_graph.node_link_graph(Content)
    except:
        logger.error("JsonNodeLinkData writing Failed.")
        if "f" in dir():
            f.close()
        #sys.exit("JsonNodeLinkData writing Failed.")
    else:
        logger.info("JsonNodeLinkData of "+AbsolutePath+" loaded successfully.")
        f.close()
        return GraphContent

def ImportFromJson(AbsolutePath):
    '''
    Import something from json file. 

    :param String AbsolutePath: absolute path of the json file
    :return Content: Content in the json file
    :rtype Variant
    '''    
    try:
        File=open(AbsolutePath,"rb")
        Content=json.load(File, encoding = "utf-8")
    except Exception as e:
        logger.error(e)
        logger.error("Json data loading Failed.")
        if "File" in dir():
            File.close()
        #sys.exit("Json data loading Failed.")    
    else:
        logger.info("Json data of "+AbsolutePath+" loaded successfully.")
        File.close()
        return Content

def FlattenList(List):
    '''
    Flatten a list using itertools no matter how many nest it has. 
    E.g. [['foo', 'baz'], ['gg']] or [[['foo', 'baz'], ['gg']]] to ['foo', 'baz', 'gg'].

    :param List[Variant]: The list you want to flatten
    :return List: Flattened list
    :rtype List[Variant]
    '''
    for Element in List:
        if type(Element)==list:
            List = list(itertools.chain(*List))
            return FlattenList(List)
    return list(List)

def CombineSparseMatricesRowWise(MainMatrix, AddedMatrix):
    '''
    Stack two scipy sparse matrices vertically (row wise). Will initialize the main matrix to be two dimensional csr_matrix with all zero elements if the main matrix is empty.
    
    :param SparseMatrix MainMatrix: The main matrix that you want to add the AddedMatrix.
    :param SparseMatrix AddedMatrix: The matrix added followed by the main matrix.
    :return SparseMatrix Result: The result of Stack sparse matrices vertically (row wise).
    :rtype SparseMatrix
    '''
    if MainMatrix.size == 0:
        MainMatrix = scipy.sparse.csr_matrix([np.zeros(AddedMatrix.shape[1], dtype = int)])
    Result = scipy.sparse.vstack([MainMatrix, AddedMatrix])

    return Result

def DeleteLilMatrixRow(mat, i):
    '''
    Delete a row in a scipy.sparse.lil_matrix.

    :param scipy.sparse.lil_matrix mat: The scipy.sparse.lil_matrix you want to operate on.
    :param Int i: The row number that you want to delete
    :return SparseMatrix mat: The result of deleted sparse matrix.
    :rtype SparseMatrix
    '''

    if not isinstance(mat, scipy.sparse.lil.lil_matrix):
        #print mat.__class__
        raise ValueError("works only for LIL format -- use .tolil() first")
    mat.rows = np.delete(mat.rows, i)
    mat.data = np.delete(mat.data, i)
    mat._shape = (mat._shape[0] - 1, mat._shape[1])

    return mat

def DeleteCsrMatrixRow(mat, i):
    '''
    Delete a row in a scipy.sparse.csr_matrix.

    :param scipy.sparse.csr_matrix mat: The scipy.sparse.csr_matrix you want to operate on.
    :param Int i: The row number that you want to delete
    :return SparseMatrix mat: The result of deleted sparse matrix.
    :rtype SparseMatrix
    '''
    if not isinstance(mat, scipy.sparse.csr_matrix):
        try:
            print "Warning: works only for CSR format -- use .tocsr() first"
            mat = mat.tocsr()
        except:
            raise ValueError("cannot convert mat to CSR format")
        #raise ValueError("works only for CSR format -- use .tocsr() first")
    n = mat.indptr[i+1] - mat.indptr[i]
    if n > 0:
        mat.data[mat.indptr[i]:-n] = mat.data[mat.indptr[i+1]:]
        mat.data = mat.data[:-n]
        mat.indices[mat.indptr[i]:-n] = mat.indices[mat.indptr[i+1]:]
        mat.indices = mat.indices[:-n]
    mat.indptr[i:-1] = mat.indptr[i+1:]
    mat.indptr[i:] -= n
    mat.indptr = mat.indptr[:-1]
    mat._shape = (mat._shape[0]-1, mat._shape[1])

    return mat


def ExportNpArray(AbsolutePath, NpArray, Format = "%f"):
    '''
    Export a Numpy array to a file.
    
    :param String AbsolutePath: The stored file location.
    :param numpy.array NpArray: The Numpy array you want to store.
    :param String Format: How to print each element, e.g. %i, %10.5f
    '''
    try:
        with open(AbsolutePath, "w+") as File:
            np.savetxt(File, NpArray, fmt = Format)
    except:
        logger.error("NpArray saving Failed.")

def ImportNpArray(AbsolutePath, DataType, ndmin = 0):
    '''
    Import a Numpy array from a file.
    
    :param String AbsolutePath: The stored file location.
    :param data-type DataType: How to match each element, e.g. int, float
    :param int ndmin: How many dimensions of array at least you will have.
    :return NpArray: NpArray in the file
    :rtype NpArray
    '''
    try:
        NpArray = np.loadtxt(AbsolutePath, dtype = DataType, ndmin = ndmin)
        return NpArray
    except Exception as e:
        logger.error(e)
        logger.error("NpArray loading Failed.")

def ExportSparseMatrix(AbsolutePath, SparseMatrix):
    '''
    Export a scipy sparse matrix to a file using matrix market format.
    Please refer to http://math.nist.gov/MatrixMarket/formats.html for more information about this format.
    
    :param String AbsolutePath: The stored file location.
    :param scipy sparse matrix SparseMatrix: The scipy sparse matrix you want to store.
    '''
    try:
        with open(AbsolutePath, "w+") as File:
            scipy.io.mmwrite(File, SparseMatrix)
    except Exception as e:
        logger.error(e)
        logger.error("SparseMatrix saving Failed.")

def ImportSparseMatrix(AbsolutePath):
    '''
    Import a scipy sparse matrix from a file using matrix market format.
    
    :param String AbsolutePath: The stored file location.
    :return SparseMatrix: (converted) scipy csr_matrix in the file
    :rtype Scipy Sparse Matrix
    '''
    try:
        SparseMatrix = scipy.io.mmread(AbsolutePath)
        SparseMatrix = SparseMatrix.tocsr()
        return SparseMatrix
    except Exception as e:
        logger.error(e)
        logger.error("SparseMatrix loading Failed.")

def IfTwoSparseMatrixEqual(SparseMatrix1, SparseMatrix2):
    '''
    Check if two scipy sparse matrix is exactly the same.
    
    :param SparseMatrix SparseMatrix1: The first scipy sparse matrix.
    :param SparseMatrix SparseMatrix2: The second scipy sparse matrix.
    :return Equal: True if they are equal, otherwise will be false.
    :rtype Boolean
    '''
    try:
        if (SparseMatrix1 - SparseMatrix2).nnz == 0:
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)
