import os
from sklearn import metrics
import datetime

import CommonModules as CM
from BuildVocabulary import BuildVocabulary
from HoldoutClassification import HoldoutClassification

class OnlineAnalysis:
    def __init__(self, VocabularyDirectory, MalwareDirectory, GoodwareDirectory, TrainningWindowSize, TestingWindowSize,
                 OutputFileName="OnlineAnalysisReport.txt"):
        self.VocabularyDirectory = VocabularyDirectory
        self.MalwareDirectory = MalwareDirectory
        self.GoodwareDirectory = GoodwareDirectory
        self.TrainningWindowSize = int(TrainningWindowSize)
        self.TestingWindowSize = int(TestingWindowSize)
        self.TrainningTime = 0
        self.TestingTime = 0
        self.OutputFileName = OutputFileName
        self.GetProcessingDirList()
        with open(OutputFileName, "w+") as Fd:
            pass

    def GetProcessingDirList(self):
        # MalwareDirList and GoodwareDirList contain the abs paths of all malware and goodware date-wise-named dirs
        MalwareDirList = CM.ListDirs(self.MalwareDirectory)
        GoodwareDirList = CM.ListDirs(self.GoodwareDirectory)
        for Dir in MalwareDirList:
            if (os.path.basename(Dir)).isdigit() == False:
                MalwareDirList.remove(Dir)
        for Dir in GoodwareDirList:
            if (os.path.basename(Dir)).isdigit() == False:
                GoodwareDirList.remove(Dir)
        # Taking 01/01/1900 as the inception date and calculating the difference b/w each day in the mal/goodware dir list to represent them as integers
        # this difference in ints is stored in MalwareDirNumList and GoodwareDirNumList
        InitialDay = datetime.datetime.strptime("19000101", "%Y%m%d")
        MalwareDirNumList = map(lambda x: datetime.datetime.strptime(x, "%Y%m%d"),
                                map((os.path.basename), MalwareDirList))
        GoodwareDirNumList = map(lambda x: datetime.datetime.strptime(x, "%Y%m%d"),
                                 map((os.path.basename), GoodwareDirList))
        MalwareDirNumList = map(lambda x: (x - InitialDay).days, MalwareDirNumList)
        GoodwareDirNumList = map(lambda x: (x - InitialDay).days, GoodwareDirNumList)
        # (1) Find if malware is earlier of goodware is earlier dated
        # (2) according to this dates, chop the malware or goodware dir to have only the overlapping portion
        # (3) 1900 Jan 01 is used as reference to calcluate this difference

        if (MalwareDirNumList[0] >= GoodwareDirNumList[0]):
            DifferenceList = map(lambda x: abs(x - MalwareDirNumList[0]), GoodwareDirNumList)
            GoodwareDirList = GoodwareDirList[DifferenceList.index(min(DifferenceList)):]
            GoodwareDirNumList = GoodwareDirNumList[DifferenceList.index(min(DifferenceList)):]
        if (GoodwareDirNumList[0] > MalwareDirNumList[0]):
            DifferenceList = map(lambda x: abs(x - GoodwareDirNumList[0]), MalwareDirNumList)
            MalwareDirList = MalwareDirList[DifferenceList.index(min(DifferenceList)):]
            MalwareDirNumList = MalwareDirNumList[DifferenceList.index(min(DifferenceList)):]

        self.MalwareDirList = MalwareDirList
        self.GoodwareDirList = GoodwareDirList
        self.MalwareDirNumList = MalwareDirNumList  # contains the diff in days from Jan 1 1900
        self.GoodwareDirNumList = GoodwareDirNumList  # contains the diff in days from Jan 1 1900
        print MalwareDirList
        print GoodwareDirList
        if min(DifferenceList) > self.TrainningWindowSize:
            raise ValueError(
                "TrainningWindowSize is too small for this dataset. No overlapping can be found to do the test.")
        return MalwareDirList, GoodwareDirList, MalwareDirNumList, GoodwareDirNumList

    def GeneratorForOnce(self):
        StartingDate = min(self.MalwareDirNumList[0], self.GoodwareDirNumList[0])
        EndingDate = max(self.MalwareDirNumList[-1], self.GoodwareDirNumList[-1])
        TrainBad = []
        TrainGood = []
        TestBad = []
        TestGood = []
        # ------------------------Trainning set-----------------------------------
        for Date in range(StartingDate, StartingDate + self.TrainningWindowSize):
            if Date in self.MalwareDirNumList:
                TrainBad.append(self.MalwareDirList[self.MalwareDirNumList.index(Date)])
            if Date in self.GoodwareDirNumList:
                TrainGood.append(self.GoodwareDirList[self.GoodwareDirNumList.index(Date)])
        if TrainGood == [] or TrainBad == []:
            raise ValueError("One of the trainning is empty for the given period.")
        # ------------------------Testing set-----------------------------------
        for Date in range(StartingDate + self.TrainningWindowSize, EndingDate + 1):
            TestBad = []
            TestGood = []
            for TestDate in range(Date, Date + self.TestingWindowSize):
                if TestDate in self.MalwareDirNumList:
                    TestBad.append(self.MalwareDirList[self.MalwareDirNumList.index(TestDate)])
                if TestDate in self.GoodwareDirNumList:
                    TestGood.append(self.GoodwareDirList[self.GoodwareDirNumList.index(TestDate)])
            if TestBad == [] and TestGood == []:
                continue
            # Yield TrainSet StartingDate, TrainSet EndingDate, TestSet StartingDate, TestSet EndingDate,
            # Malware TrainningSet, Goodware TrainningSet, Malware TestSet, Goodware TestSet
            yield StartingDate, StartingDate + self.TrainningWindowSize - 1, Date, \
                  Date + self.TestingWindowSize - 1, TrainBad, TrainGood, TestBad, TestGood

    def GeneratorForDaily(self):
        StartingDate = min(self.MalwareDirNumList[0], self.GoodwareDirNumList[0])
        EndingDate = max(self.MalwareDirNumList[-1], self.GoodwareDirNumList[-1])

        # ------------------------Trainning set-----------------------------------
        for Date in range(StartingDate, EndingDate):
            TrainBad = []
            TrainGood = []
            for TrainDate in range(Date, Date + self.TrainningWindowSize):
                if TrainDate in self.MalwareDirNumList:
                    TrainBad.append(self.MalwareDirList[self.MalwareDirNumList.index(TrainDate)])
                if TrainDate in self.GoodwareDirNumList:
                    TrainGood.append(self.GoodwareDirList[self.GoodwareDirNumList.index(TrainDate)])
            if TrainGood == [] or TrainBad == []:
                continue
                # ------------------------Testing set-----------------------------------
            TestBad = []
            TestGood = []
            for TestDate in range(TrainDate + 1, TrainDate + 1 + self.TestingWindowSize):
                if TestDate in self.MalwareDirNumList:
                    TestBad.append(self.MalwareDirList[self.MalwareDirNumList.index(TestDate)])
                if TestDate in self.GoodwareDirNumList:
                    TestGood.append(self.GoodwareDirList[self.GoodwareDirNumList.index(TestDate)])
            if TestBad == [] and TestGood == []:
                continue
            # Yield TrainSet StartingDate, TrainSet EndingDate, TestSet StartingDate, TestSet EndingDate,
            # Malware TrainningSet, Goodware TrainningSet, Malware TestSet, Goodware TestSet
            yield Date, Date + self.TrainningWindowSize - 1, TrainDate + 1, \
                  TrainDate + self.TestingWindowSize, TrainBad, TrainGood, TestBad, TestGood

    def ClassificationForDrebin(self, TrainBad, TrainGood, TestBad, TestGood):
        # -----------------------------------Classification-------------------------------
        self.TotalFeatureDict = BuildVocabulary(self.VocabularyDirectory, *(TrainBad + TrainGood + TestBad + TestGood))
        try:
            self.TrainLabels, self.TestLabels, self.PredictedLabels, self.TrainningTime, self.TestingTime = HoldoutClassification(
                TrainBad, TrainGood, TestBad, TestGood, self.TotalFeatureDict, "binary")
        except:
            return [], [], [], 0, 0
        return self.TrainLabels, self.TestLabels, self.PredictedLabels, self.TrainningTime, self.TestingTime

    def PrintReport(self, TrainStart, TrainEnd, TestStart, TestEnd, TrainLabels, TestLabels, PredictedLabels):
        '''
        Format strings, calculate the statistics and print the report.
        '''
        TrainStartString = (datetime.datetime.strptime("19000101", "%Y%m%d") + \
                            datetime.timedelta(TrainStart)).strftime("%Y%m%d")
        TrainEndString = (datetime.datetime.strptime("19000101", "%Y%m%d") + \
                          datetime.timedelta(TrainEnd)).strftime("%Y%m%d")
        TestStartString = (datetime.datetime.strptime("19000101", "%Y%m%d") + \
                           datetime.timedelta(TestStart)).strftime("%Y%m%d")
        TestEndString = (datetime.datetime.strptime("19000101", "%Y%m%d") + \
                         datetime.timedelta(TestEnd)).strftime("%Y%m%d")
        NumberOfTrainBad = TrainLabels.count(1)
        NumberOfTrainGood = TrainLabels.count(-1)
        NumberOfTestBad = TestLabels.count(1)
        NumberOfTestGood = TestLabels.count(-1)

        print "Trainning Period:", TrainStartString, "-", TrainEndString, "Testing Period:", TestStartString, "-", TestEndString
        print "Trainning Time:", "%ss" % self.TrainningTime, "Testing Time:", "%ss" % self.TestingTime
        print "NumberOfTrainBad:", NumberOfTrainBad, "NumberOfTrainGood:", NumberOfTrainGood, "NumberOfTestBad:", NumberOfTestBad, "NumberOfTestGood:", NumberOfTestGood
        print "Accuracy classification score:", metrics.accuracy_score(TestLabels, PredictedLabels)
        print "Hamming loss:", metrics.hamming_loss(TestLabels, PredictedLabels)
        print "Average hinge loss:", metrics.hinge_loss(TestLabels, PredictedLabels)
        print "Log loss:", metrics.log_loss(TestLabels, PredictedLabels)
        print "F1 Score:", metrics.f1_score(TestLabels, PredictedLabels)
        print "Zero-one classification loss:", metrics.zero_one_loss(TestLabels, PredictedLabels)
        print "----------------------------------------------------------------------------------"

        with open(self.OutputFileName, "a+") as Fd:
            print >> Fd, "----------------------------------------------------------------------------------"
            print >> Fd, "Trainning Period:", TrainStartString, "-", TrainEndString, "Testing Period:", TestStartString, "-", TestEndString
            print >> Fd, "Trainning Time:", "%ss" % self.TrainningTime, "Testing Time:", "%ss" % self.TestingTime
            print >> Fd, "NumberOfTrainBad:", NumberOfTrainBad, "NumberOfTrainGood:", NumberOfTrainGood, "NumberOfTestBad:", NumberOfTestBad, "NumberOfTestGood:", NumberOfTestGood
            print >> Fd, metrics.classification_report(TestLabels, PredictedLabels, labels=[1, -1],
                                                       target_names=['Malware', 'Goodware'])
            print >> Fd, "Accuracy classification score:", metrics.accuracy_score(TestLabels, PredictedLabels)
            print >> Fd, "Hamming loss:", metrics.hamming_loss(TestLabels, PredictedLabels)
            print >> Fd, "Average hinge loss:", metrics.hinge_loss(TestLabels, PredictedLabels)
            print >> Fd, "Log loss:", metrics.log_loss(TestLabels, PredictedLabels)
            print >> Fd, "F1 Score:", metrics.f1_score(TestLabels, PredictedLabels)
            print >> Fd, "Zero-one classification loss:", metrics.zero_one_loss(TestLabels, PredictedLabels)
            print >> Fd, "----------------------------------------------------------------------------------"

            # for Num in self.MalwareDirNumList:
            #    if Num - StartingDate <= TrainningWindowSize:
            #        TrainBad.append(self.MalwareDirList[self.MalwareDirNumList.index(Num)])
            # for Num in self.GoodwareDirNumList:
            #    if Num - StartingDate <= TrainningWindowSize:
            #        TrainGood.append(self.GoodwareDirList[self.GoodwareDirNumList.index(Num)])

            # for Num in self.MalwareDirNumList:
            #    if Num - StartingDate <= 1:
            #        TrainBad.append(self.MalwareDirList[self.MalwareDirNumList.index(Num)])
            # for Num in self.GoodwareDirNumList:
            #    if Num - StartingDate <= TrainningWindowSize:
            #        TrainGood.append(self.GoodwareDirList[self.GoodwareDirNumList.index(Num)])
