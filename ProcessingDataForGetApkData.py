import time
import os
from CommonModules import logger
from GetFromXML import GetFromXML
from GetFromInstructions import GetFromInstructions
import CommonModules as CM


def ProcessingDataForGetApkData(ApkDirectoryPath, ApkFile, PMap):
    '''
    Produce .data file for a given ApkFile.

    :param String ApkDirectoryPath: absolute path of the ApkFile directory
    :param String ApkFile: absolute path of the ApkFile
    :param PScoutMapping.PScoutMapping() PMap: PMap for API mapping

    :return Tuple(String, Boolean)  ProcessingResult: The processing result, (ApkFile, True/False)
    True means successful. False means unsuccessful.
    '''
    try:
        StartTime = time.time()
        logger.info("Start to process " + ApkFile + "...")
        print("Start to process " + ApkFile + "...")
        DataDictionary = {}
        RequestedPermissionSet, ActivitySet, ServiceSet, ContentProviderSet, BroadcastReceiverSet, HardwareComponentsSet, IntentFilterSet = GetFromXML(
            ApkDirectoryPath, ApkFile)
        RequestedPermissionList = list(RequestedPermissionSet)
        ActivityList = list(ActivitySet)
        ServiceList = list(ServiceSet)
        ContentProviderList = list(ContentProviderSet)
        BroadcastReceiverList = list(BroadcastReceiverSet)
        HardwareComponentsList = list(HardwareComponentsSet)
        IntentFilterList = list(IntentFilterSet)
        DataDictionary["RequestedPermissionList"] = RequestedPermissionList
        DataDictionary["ActivityList"] = ActivityList
        DataDictionary["ServiceList"] = ServiceList
        DataDictionary["ContentProviderList"] = ContentProviderList
        DataDictionary["BroadcastReceiverList"] = BroadcastReceiverList
        DataDictionary["HardwareComponentsList"] = HardwareComponentsList
        DataDictionary["IntentFilterList"] = IntentFilterList
        # Got Set S2 and others

        UsedPermissions, RestrictedApiSet, SuspiciousApiSet, URLDomainSet = GetFromInstructions(ApkDirectoryPath,
                                                                                                ApkFile, PMap,
                                                                                                RequestedPermissionList)
        UsedPermissionsList = list(UsedPermissions)
        RestrictedApiList = list(RestrictedApiSet)
        SuspiciousApiList = list(SuspiciousApiSet)
        URLDomainList = list(URLDomainSet)
        DataDictionary["UsedPermissionsList"] = UsedPermissionsList
        DataDictionary["RestrictedApiList"] = RestrictedApiList
        DataDictionary["SuspiciousApiList"] = SuspiciousApiList
        DataDictionary["URLDomainList"] = URLDomainList
        # Set S6, S5, S7, S8


        CM.ExportToJson(os.path.splitext(ApkFile)[0] + ".data", DataDictionary)

    except Exception as e:
        FinalTime = time.time()
        logger.error(e)
        logger.error(ApkFile + " processing failed in " + str(FinalTime - StartTime) + "s...")
        print ApkFile + " processing failed in " + str(FinalTime - StartTime) + "s..."
        return ApkFile, False
    else:
        FinalTime = time.time()
        logger.info(ApkFile + " processed successfully in " + str(FinalTime - StartTime) + "s")
        print ApkFile + " processed successfully in " + str(FinalTime - StartTime) + "s"
        return ApkFile, True