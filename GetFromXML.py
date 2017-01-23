import sys
reload(sys)
sys.path.append("Modules")
sys.path.append("Androguard")
sys.setdefaultencoding("utf-8")

import os
from CommonModules import logger
import androlyze
from xml.dom import minidom


def GetFromXML(ApkDirectoryPath, ApkFile):
    '''
    Get requested permission etc. for an ApkFile from Manifest files.
    :param String ApkDirectoryPath
    :param String ApkFile
    :return RequestedPermissionSet
    :rtype Set([String])
    :return ActivitySet
    :rtype Set([String])
    :return ServiceSet
    :rtype Set([String])
    :return ContentProviderSet
    :rtype Set([String])
    :return BroadcastReceiverSet
    :rtype Set([String])
    :return HardwareComponentsSet
    :rtype Set([String])
    :return IntentFilterSet
    :rtype Set([String])
    '''
    ApkDirectoryPath = os.path.abspath(ApkDirectoryPath)
    ApkFileName = os.path.splitext(ApkFile)[0]

    RequestedPermissionSet = set()
    ActivitySet = set()
    ServiceSet = set()
    ContentProviderSet = set()
    BroadcastReceiverSet = set()
    HardwareComponentsSet = set()
    IntentFilterSet = set()
    try:
        ApkFile = os.path.abspath(ApkFile)
        a = androlyze.APK(ApkFile)
        f = open(os.path.splitext(ApkFile)[0] + ".xml", "w")
        f.write((a.xml["AndroidManifest.xml"].toprettyxml()).encode("utf-8"))
        f.close()
    except Exception as e:
        print e
        logger.error(e)
        logger.error("Executing Androlyze on " + ApkFile + " to get AndroidManifest.xml Failed.")
        return
    try:
        f = open(ApkFileName + ".xml", "r")
        Dom = minidom.parse(f)
        DomCollection = Dom.documentElement

        DomPermission = DomCollection.getElementsByTagName("uses-permission")
        for Permission in DomPermission:
            if Permission.hasAttribute("android:name"):
                RequestedPermissionSet.add(Permission.getAttribute("android:name"))

        DomActivity = DomCollection.getElementsByTagName("activity")
        for Activity in DomActivity:
            if Activity.hasAttribute("android:name"):
                ActivitySet.add(Activity.getAttribute("android:name"))

        DomService = DomCollection.getElementsByTagName("service")
        for Service in DomService:
            if Service.hasAttribute("android:name"):
                ServiceSet.add(Service.getAttribute("android:name"))

        DomContentProvider = DomCollection.getElementsByTagName("provider")
        for Provider in DomContentProvider:
            if Provider.hasAttribute("android:name"):
                ContentProviderSet.add(Provider.getAttribute("android:name"))

        DomBroadcastReceiver = DomCollection.getElementsByTagName("receiver")
        for Receiver in DomBroadcastReceiver:
            if Receiver.hasAttribute("android:name"):
                BroadcastReceiverSet.add(Receiver.getAttribute("android:name"))

        DomHardwareComponent = DomCollection.getElementsByTagName("uses-feature")
        for HardwareComponent in DomHardwareComponent:
            if HardwareComponent.hasAttribute("android:name"):
                HardwareComponentsSet.add(HardwareComponent.getAttribute("android:name"))

        DomIntentFilter = DomCollection.getElementsByTagName("intent-filter")
        DomIntentFilterAction = DomCollection.getElementsByTagName("action")
        for Action in DomIntentFilterAction:
            if Action.hasAttribute("android:name"):
                IntentFilterSet.add(Action.getAttribute("android:name"))


    except Exception as e:
        logger.error(e)
        logger.error("Cannot resolve " + DestinationFolder + "'s AndroidManifest.xml File!");
        return RequestedPermissionSet, ActivitySet, ServiceSet, ContentProviderSet, BroadcastReceiverSet, HardwareComponentsSet, IntentFilterSet
    finally:
        f.close()
        return RequestedPermissionSet, ActivitySet, ServiceSet, ContentProviderSet, BroadcastReceiverSet, HardwareComponentsSet, IntentFilterSet