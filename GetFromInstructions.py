import sys
reload(sys)
sys.path.append("Modules")
sys.path.append("Androguard")
sys.setdefaultencoding("utf-8")

import os
from CommonModules import logger
import androlyze
import BasicBlockAttrBuilder as BasicBlockAttrBuilder
import re

def GetFromInstructions(ApkDirectoryPath, ApkFile, PMap, RequestedPermissionList):
    '''
    Get required permissions, used Apis and HTTP information for an ApkFile.
    Reloaded version of GetPermissions.

    :param String ApkDirectoryPath
    :param String ApkFile
    :param PScoutMapping.PScoutMapping PMap
    :param RequestedPermissionList List([String])
    :return UsedPermissions
    :rtype Set([String])
    :return RestrictedApiSet
    :rtype Set([String])
    :return SuspiciousApiSet
    :rtype Set([String])
    :return URLDomainSet
    :rtype Set([String])
    '''


    UsedPermissions = set()
    RestrictedApiSet = set()
    SuspiciousApiSet = set()
    URLDomainSet = set()
    try:
        ApkFile = os.path.abspath(ApkFile)
        a, d, dx = androlyze.AnalyzeAPK(ApkFile)
    except Exception as e:
        print e
        logger.error(e)
        logger.error("Executing Androlyze on "+ApkFile+" Failed.")
        return
    for method in d.get_methods():
        g = dx.get_method(method)
        for BasicBlock in g.get_basic_blocks().get():
            Instructions = BasicBlockAttrBuilder.GetBasicBlockDalvikCode(BasicBlock)
            Apis, SuspiciousApis = BasicBlockAttrBuilder.GetInvokedAndroidApis(Instructions)
            Permissions, RestrictedApis = BasicBlockAttrBuilder.GetPermissionsAndApis(Apis, PMap, RequestedPermissionList)
            UsedPermissions = UsedPermissions.union(Permissions)
            RestrictedApiSet = RestrictedApiSet.union(RestrictedApis)
            SuspiciousApiSet = SuspiciousApiSet.union(SuspiciousApis)
            for Instruction in Instructions:
                URLSearch = re.search("https?://([\da-z\.-]+\.[a-z\.]{2, 6}|[\d.]+)[^'\"]*", Instruction, re.IGNORECASE)
                if(URLSearch):
                    URL = URLSearch.group()
                    Domain = re.sub("https?://(.*)", "\g<1>", re.search("https?://([^/:\\\\]*)", URL, re.IGNORECASE).group(), 0, re.IGNORECASE)
                    URLDomainSet.add(Domain)
    #Got Set S6, S5, S7 described in Drebian paper
    return UsedPermissions, RestrictedApiSet, SuspiciousApiSet, URLDomainSet