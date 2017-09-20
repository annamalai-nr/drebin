import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
os.sys.path.insert(0,parentdir) 
import CommonModules as CM

import zipfile


def RenameApk(Directory):
    Directory = os.path.normpath(Directory)
    print "Renaming ", Directory, ":"
    for Apk in CM.ListApkFiles(Directory):
        try:
            ZipApk = zipfile.ZipFile(Apk, "r")
            ZipDex = ZipApk.getinfo("classes.dex")
            Time = "%04d%02d%02d%02d%02d%02d" % ZipDex.date_time
            ZipApk.close()
            YearMonthDay = str(int(Time)/1000000)
            TargetName = Time + "_" + os.path.basename(Apk)
            DestinationFolder = os.path.join(Directory, YearMonthDay)
            #print Apk, os.path.join(Directory, DestinationFolder, TargetName)
            os.renames(Apk, os.path.join(Directory, DestinationFolder, TargetName))
            sys.stdout.write("#")
        except:
            sys.stdout.write("X")
            continue
    print 
    return


if __name__ == "__main__":
    RenameApk(sys.argv[1])