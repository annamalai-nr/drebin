import sys
from pprint import pprint
import json
import logging
import collections


#logging level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('sys.stdout')



class SusiDictMaker:
    ##################################################
    #                 Constructor                    #
    ##################################################
    def __init__(self, 
        SrcTextFName = None, 
        SinkTextFName = None, 
        SrcDictFName = 'Ouput_CatSources_v0_9.txt.json',
        SinkDictFName = 'Ouput_CatSinks_v0_9.txt.json'):
        
        #Declare dicts for holding src and sink apis
        self.SusiSrcDict = {}
        self.SusiSinkDict = {}
        #Init src and sink api file lines to empty types
        self.SrcLines = None
        self.SinkLines = None


        #If the src api to src/sink mapping is provided, then we need to load them
        if SrcTextFName:
            logger.debug ("reading the susi srcs from file: %s",
                SrcTextFName)
            self.SrcLines = [Line.strip() \
            for Line in open (SrcTextFName, 'r').readlines()]
        if SinkTextFName:
            logger.debug ("reading the susi sinks from file: %s",
                SinkTextFName)
            self.SinkLines = [Line.strip() \
            for Line in open (SinkTextFName, 'r').readlines()]
            #have to exit the constructor from here
            #no need to proceed to create dicts from json file
            return
        
        #If dicts of src and sink apis are available, then the api - src/sink
        #mapping routines could be avoided
        #if SrcDictFName:
        logger.debug ("reading the susi src dict from file: %s",
            SrcDictFName)
        with open(SrcDictFName, 'rb') as FH:
            self.SusiSrcDict = json.load(FH)
        #if SinkDictFName:
        logger.debug ("reading the susi sink dict from file: %s",
        SinkDictFName)
        with open(SinkDictFName, 'rb') as FH:
            self.SusiSinkDict = json.load(FH)
  

    ##################################################
    #     make susi api-src and api-sink dict        #
    ##################################################
    def MakeDict(self):
        '''
        Creates the api-src and api-sink mapping 
        args - none
        '''
        #example src file line:
        #<com.android.internal.telephony.cdma.CDMAPhone: java.lang.String getDeviceId()> (UNIQUE_IDENTIFIER)

        if None == self.SrcLines or None == self.SinkLines:
            logger.error ("SrcLine or SinkLine is empty, \
                could not create susi mapping dict")
            return 

        for Line in self.SrcLines:
            if Line.startswith ('<'):
                Parts = [Part.strip() for Part in Line.split()]
                SrcCat = Parts[-1]
                ClassName = Parts[0][1:-1] #first char = '<';last char = ':'
                ApiName = Parts[2].split("(")[0].strip()

                Key    = SrcCat
                Val = ClassName + " " + ApiName #SPACE used as delim
                self.SusiSrcDict.setdefault (Key, []).append (Val)

        #Removing duplicate entries
        for Key in self.SusiSrcDict:
            self.SusiSrcDict[Key] = list(set(self.SusiSrcDict[Key]))
        logger.info ("Srcs dict made!!")

        #example sink file line:
        #<com.android.email.Email: void enableStrictMode(boolean)> (EMAIL)
        for Line in self.SinkLines:
            if Line.startswith ('<'):
                Parts = [Part.strip() for Part in Line.split()]
                SinkCat = Parts[-1]
                ClassName = Parts[0][1:-1] #first char = '<';last char = ':'
                ApiName = Parts[2].split("(")[0].strip()

                Key    = SinkCat
                Val = ClassName + " " + ApiName #SPACE used as delim
                self.SusiSinkDict.setdefault (Key, []).append (Val)
            
        #Removing duplicate entries
        for Key in self.SusiSinkDict:
            self.SusiSinkDict[Key] = list(set(self.SusiSinkDict[Key]))
        logger.info ("Sink dict made!!")



    ##################################################
    #     Deletes  (NO_CATEGORY) category            #
    ##################################################
    def RemoveNoCatKeyFromDict (self):
        '''
        Deletes the (NO_CATEGORY) category from api-src and api-sink dicts 
        args - none
        '''
        #May throw error if the key is missing
        try:
            del self.SusiSrcDict['(NO_CATEGORY)']
            logger.debug ("Deleted (NO_CATEGORY) from src dict")
        except:
            logger.error ("Could not delete (NO_CATEGORY) from src dict")

        try:
            del self.SusiSinkDict['(NO_CATEGORY)']
            logger.debug ("Deleted (NO_CATEGORY) from sink dict")
        except:
            logger.error ("Could not delete (NO_CATEGORY) from sink dict")
  


    ##################################################
    #              Json Dict Dumper                  #
    ##################################################
    def JsonDumpSusiDicts(self, SrcDictFName, SinkDictFName):
        '''
        Dump api-src and api-sink dicts as Json files
        args:
            SrcDictFName - Name of the api-src dict json file
            SinkDictFName - Name of the api-sink dict json file
        '''
        with open(SrcDictFName, 'w') as FH:
            json.dump(self.SusiSrcDict, FH)
        logger.info ("Susi src dict dumped as json ")

        with open(SinkDictFName, 'w') as FH:
            json.dump(self.SusiSinkDict, FH)
        logger.info ("Susi sink dict dumped as json ")



    ##################################################
    #     Get SUSI src/sink category from api        #
    ##################################################
    def GetSusiCategoryFromApi (self, ClassName, ApiName, CatType = None):
        '''
        Most important method of the class.
        Get Susi src OR Susi sink category from Android 4.2 APIs 
        args:
            ClassName - api class name
            ApiName - api name
            CatType - src/sink
        '''
        if CatType == "src":
            SearchDict = self.SusiSrcDict
        elif CatType == "sink":
            SearchDict = self.SusiSinkDict
        else:
            logger.error("Invalid Susi category. \
                Please use \"src\" or \"sink\" as the \"CatType\" arg")
            return -1


        SearchString = ClassName.strip() + " " + ApiName.strip()
        logger.debug(" Searching for ClassName and API: %s",
            SearchString)
        for SrcCatAsKey in SearchDict:
            if SearchString in SearchDict[SrcCatAsKey]:
                return SrcCatAsKey
        #have checked all the dict values
        return -1



    ##################################################
    #              Getters and Printers              #
    ##################################################    
    def GetSrcDict (self):
        '''
        Get api-src dicts
        args - none
        '''
        return self.SusiSrcDict
    def PrintSrcDict (self):
        '''
        Print api-src dicts
        args - none
        '''
        pprint (self.SusiSrcDict)



    def GetSinkDict (self):
        '''
        Get api-sink dicts
        args - none
        '''
        return self.SusiSinkDict
    def PrintSinkDict (self):
        '''
        Print api-sink dicts
        args - none
        '''
        pprint (self.SusiSinkDict)



    def GetSrcSinkDicts (self):
        '''
        Get api-src and api-sink dicts
        args - none
        '''
        return self.GetSrcDict(), self.GetSinkDict()
    def PrintSrcSinkDicts (self):
        '''
        Print api-src and api-sink dicts
        args - none
        '''
        self.PrintSrcDict()
        self.PrintSinkDict()



    def GetSusiSrcCategories(self):
        '''
        Get Susi src categories
        args - none
        '''
        return list (self.SusiSrcDict.keys())
    def PrintSusiSrcCategories(self):
        '''
        Print Susi src categories
        args - none
        '''
        pprint (list (self.SusiSrcDict.keys()))



    def GetSusiSinkCategories(self):
        '''
        Get Susi sink categories
        args - none
        '''
        return list (self.SusiSinkDict.keys())
    def PrintSusiSinkCategories(self):
        '''
        Print Susi sink categories
        args - none
        '''
        pprint (list (self.SusiSinkDict.keys()))
        
        
    ##################################################
    #                 Sorting the dict               #
    ##################################################
    def SortSrcSinkDictsByKeys (self):
        self.SusiSrcDict = \
        collections.OrderedDict(sorted(self.SusiSrcDict.items()))
        self.SusiSinkDict = \
        collections.OrderedDict(sorted(self.SusiSinkDict.items()))


    

  

    





##################################################
#              main function to test             #
##################################################
def main ():

    SusiDictMakerObj = SusiDictMaker ()

    #Use if dict is already avail
    #SusiDictMakerObj = SusiDictMaker (SrcDictFName = sys.argv[1],
        #SinkDictFName = sys.argv[2])

    #no need to call this if dict already avail
    SusiDictMakerObj.MakeDict()
    #no need to call this if dict already avail
    SusiDictMakerObj.RemoveNoCatKeyFromDict()

    SusiDictMakerObj.PrintSusiSrcCategories()
    SusiDictMakerObj.PrintSusiSinkCategories()

    #SusiDictMakerObj.PrintSrcSinkDicts()
    #SusiDictMakerObj.PrintSinkDict()

    #Belongs to no_category
    #please check if it is avail or removed!
    print SusiDictMakerObj.GetSusiCategoryFromApi(\
        "com.android.camera.PanoProgressBar",
        "setDoneColor",
        "sink")

    SusiDictMakerObj.JsonDumpSusiDicts(str(sys.argv[1])+".json",
        str(sys.argv[2]+".json"))


if __name__ == '__main__':
    main()