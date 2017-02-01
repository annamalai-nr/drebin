import os
import CommonModules as CM
from collections import OrderedDict

def BuildVocabulary(VocabularyDirectory, *ApkDirectoryPaths):
    '''
    Produce Vocabulary for data files.

    :param String VocabularyDirectory: absolute path of directory you want to store the Vocabulary in
    :param *List ApkDirectoryPaths: List of the data file directories

    :return OrderedDict(String:Int)  TotalFeatureDict: Dictionary that stores all features
    '''
    RequestedPermissionDict = {}
    ActivityDict = {}
    ServiceDict = {}
    ContentProviderDict = {}
    BroadcastReceiverDict = {}
    HardwareComponentsDict = {}
    IntentFilterDict = {}
    UsedPermissionsDict = {}
    RestrictedApiDict = {}
    SuspiciousApiDict = {}
    URLDomainDict = {}

    TotalFeatureDict = OrderedDict()

    DataFileList = []
    for ApkDirectoryPath in ApkDirectoryPaths:
        if(ApkDirectoryPath):
            DataFileList.extend(CM.ListFiles(ApkDirectoryPath,".data"))
    for DataFile in DataFileList:
        JsonData = CM.ImportFromJson(DataFile)
        for Service in JsonData["ServiceList"]:
            ServiceDict[Service] = 1
        for RestrictedApi in JsonData["RestrictedApiList"]:
            RestrictedApiDict[RestrictedApi] = 1
        for HardwareComponents in JsonData["HardwareComponentsList"]:
            HardwareComponentsDict[HardwareComponents] = 1
        for BroadcastReceiver in JsonData["BroadcastReceiverList"]:
            BroadcastReceiverDict[BroadcastReceiver] = 1
        for SuspiciousApi in JsonData["SuspiciousApiList"]:
            SuspiciousApiDict[SuspiciousApi] = 1
        for ContentProvider in JsonData["ContentProviderList"]:
            ContentProviderDict[ContentProvider] = 1
        for URLDomain in JsonData["URLDomainList"]:
            URLDomainDict[URLDomain] = 1
        for IntentFilter in JsonData["IntentFilterList"]:
            IntentFilterDict[IntentFilter] = 1
        for RequestedPermission in JsonData["RequestedPermissionList"]:
            RequestedPermissionDict[RequestedPermission] = 1
        for Activity in JsonData["ActivityList"]:
            ActivityDict[Activity] = 1
        for UsedPermissions in JsonData["UsedPermissionsList"]:
            UsedPermissionsDict[UsedPermissions] = 1

    CM.ExportToJson(os.path.join(VocabularyDirectory,"ServiceDict.dict"),ServiceDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"RestrictedApiDict.dict"),RestrictedApiDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"HardwareComponentsDict.dict"),HardwareComponentsDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"BroadcastReceiverDict.dict"),BroadcastReceiverDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"SuspiciousApiDict.dict"),SuspiciousApiDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"ContentProviderDict.dict"),ContentProviderDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"URLDomainDict.dict"),URLDomainDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"IntentFilterDict.dict"),IntentFilterDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"RequestedPermissionDict.dict"),RequestedPermissionDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"ActivityDict.dict"),ActivityDict)
    CM.ExportToJson(os.path.join(VocabularyDirectory,"UsedPermissionsDict.dict"),UsedPermissionsDict)

    TotalFeatureDict.update(ServiceDict)
    TotalFeatureDict.update(RestrictedApiDict)
    TotalFeatureDict.update(HardwareComponentsDict)
    TotalFeatureDict.update(BroadcastReceiverDict)
    TotalFeatureDict.update(SuspiciousApiDict)
    TotalFeatureDict.update(ContentProviderDict)
    TotalFeatureDict.update(URLDomainDict)
    TotalFeatureDict.update(IntentFilterDict)
    TotalFeatureDict.update(RequestedPermissionDict)
    TotalFeatureDict.update(ActivityDict)
    TotalFeatureDict.update(UsedPermissionsDict)
    '''Can also change the dict to the form of key value pairs, then use TotalFeatureDict.values() to fit the vectorizer in the classification function.'''
    #print TotalFeatureDict
    return TotalFeatureDict