import sys
from pprint import pprint
import json
import logging
import collections

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sys.stdout')
#This is too slow log info during run time


class PScoutMapping (object):
    
    ##################################################
    #                 Constructor                    #
    ##################################################
    def __init__(self):
#        with open('PScoutPermApiDict.json', 'rb') as FH:
            #Filename of PScout dict is hard-coded
            #It could be changed if needed
        with open('SmallCasePScoutPermApiDict.json', 'rb') as FH:     
            #Use SmallCase json file to prevent run time case conversion in GetPermFromApi
            self.PermApiDictFromJsonTemp = json.load(FH) 
            self.PermApiDictFromJson = {}
#            f=open("SmallCasePScoutPermApiDict.json","wb")
#            for PermAsKey in self.PermApiDictFromJson.keys(): 
#                for k in range(len(self.PermApiDictFromJson[PermAsKey])):
#                    self.PermApiDictFromJson[PermAsKey][k][0]=(self.PermApiDictFromJson[PermAsKey][k][0]).lower()
#                    self.PermApiDictFromJson[PermAsKey][k][1]=(self.PermApiDictFromJson[PermAsKey][k][1]).lower()
#            self.SortDictByKeys()
#            json.dump(self.PermApiDictFromJson,f)
#            f.close()
            for Perms in self.PermApiDictFromJsonTemp:
                for Api in range(len(self.PermApiDictFromJsonTemp[Perms])):
                    ApiName=self.PermApiDictFromJsonTemp[Perms][Api][0].lower()+self.PermApiDictFromJsonTemp[Perms][Api][1].lower()
                    '''Exchange key and values inside the dictionary.'''
                    self.PermApiDictFromJson[ApiName]=Perms
        del self.PermApiDictFromJsonTemp
    ##################################################
    #                 Get Routines                   #
    ##################################################
    
    def GetAllPerms (self):
        return list (self.PermApiDictFromJson.keys())



    def GetAllApis (self):
        return list(self.PermApiDictFromJson.values())


    
    def GetApisFromPerm (self, Perm):
        PermAsKey = Perm
        if PermAsKey not in self.PermApiDictFromJson:
            logger.error ("Permission %s not found in the PScout Dict",
                           PermAsKey)
            return -1
        else:
            return self.PermApiDictFromJson[PermAsKey]



        
    def GetPermFromApi (self, ApiClass, ApiMethodName):
        ApiClass=ApiClass.lower() 
        ApiMethodName=ApiMethodName.lower()

        ApiName=ApiClass+ApiMethodName
        if(ApiClass+ApiMethodName) in self.PermApiDictFromJson:
            return self.PermApiDictFromJson[ApiName]
        else:
            return None



    ##################################################
    #                 Print Routines                 #
    ##################################################
    
    def PrintDict(self):
        pprint (self.PermApiDictFromJson)


        
    def PrintAllPerms (self):        
        for PermAsKey in self.PermApiDictFromJson:
            print PermAsKey


            
    def PrintAllApis(self):
        for Api in self.PermApiDictFromJson.values():
            print Api


    
    def PrintApisForPerm(self, Perm):
        PermAsKey = Perm
        
        if PermAsKey not in self.PermApiDictFromJson:
            logger.error ("Permission %s not found in the PScout Dict", 
                          PermAsKey)
            return -1
            
        for Api in self.PermApiDictFromJson[Perm]:
            pprint (Api)
        return 0
    
    ##################################################
    #                 Sorting the dict               #
    ##################################################
    def SortDictByKeys (self):
        self.PermApiDictFromJson = \
        collections.OrderedDict(sorted(self.PermApiDictFromJson.items()))
        

        

    
def main ():
    '''
    This is a sample showing to init the PScout Mapping dict and query it
    This is how the caller function can create an instance of this 
    'PScoutMapping' class and use it!
    '''
    
    #DictFName = sys.argv[1]
    PMap =  PScoutMapping()
    
    #PMap.PrintDict()
    #PMap.PrintAllPerms()
    #PMap.PrintAllApis()    
    Perms = PMap.GetAllPerms()
    #Apis = PMap.GetAllApis()    
    print Perms[60]
    #raw_input("Enter...")
    #PermsApis = PMap.GetApisFromPerm(Perms[60])
    #pprint (PermsApis)
    
    print PMap.GetPermFromApi(
    'com.android.internal.telephony.sip.SipPhone$SipConnection$1', 
                              'onError')
    
    
    


if __name__ == '__main__':
    main()