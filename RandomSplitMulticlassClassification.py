import os
import scipy.sparse
import numpy as np
import CommonModules as CM
from sklearn.feature_extraction import DictVectorizer
from sklearn import metrics
from sklearn.cross_validation import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from collections import OrderedDict
import random

def RandomSplitMulticlassClassification(MalwareFamilyFolders, GoodwareCorpus, FeatureDict, FeatureOption,
                                        ProcessNumber):
    '''
    Train a multiclass classifier for classifying malwares and goodwares using Support Vector Machine technique.
    Compute the prediction accuracy and f1 score of the classifier.
    Modified from Jiachun's code.

    :param String MalwareFamilyFolders: absolute path of the Malware Family Folders
    :param String GoodwareCorpus: absolute path of the goodware corpus
    :param OrderedDict(String:Int) FeatureDict: Dictionary that stores all features
    :param String FeatureOption: tfidf or binary, specify how to construct the feature vector
    '''
    # step 1: creating feature vector
    AllMalFeatureVectors = scipy.sparse.csr_matrix((1, len(FeatureDict)), dtype=bool)
    AllGoodFeatureVectores = scipy.sparse.csr_matrix((1, len(FeatureDict)), dtype=bool)
    # In order to use scipy.sparse.vstack, there will be one row with zeros appearing in both matrix, so it should not affect the results.
    # Modified. These two rows will be deleted after adding all vectors.

    LabelCount = 0  # Label count for Malware is >= 1.
    LabelsForReport = []
    TargetNamesForReport = []

    AllMalSamples = []
    MalLabels = []
    for MalwareCorpus in MalwareFamilyFolders:
        LabelCount = LabelCount + 1
        MalwareFamilyName = os.path.basename(MalwareCorpus)
        AllMalSamples = AllMalSamples.extend(CM.ListFiles(MalwareCorpus, ".data"))
        # ---Label the samples---
        MalSamplesTrainingSize = len(AllMalSamples)
        Labels = np.empty(MalSamplesTrainingSize)
        Labels.fill(LabelCount)
        MalLabels.extend(Labels)
        LabelsForReport.append(LabelCount)
        TargetNamesForReport.append(MalwareFamilyName)

    LabelCount = 0  # Label count for Goodware is 0.
    GoodLabels = []
    AllGoodSamples = CM.ListFiles(GoodwareCorpus, ".data")
    # ---Label the samples---
    GoodSamplesTrainingSize = len(AllGoodSamples)
    Labels = np.empty(GoodSamplesTrainingSize)
    Labels.fill(LabelCount)
    GoodLabels = Labels
    LabelsForReport.append(LabelCount)
    TargetNamesForReport.append("GoodWare")

    print "Loaded samples"

    FeatureDictVectorizer = DictVectorizer(sort=False)  # Set sparse = False if necessary(Need to change the code below)
    FeatureDictVectorizer.fit_transform(FeatureDict)  # Cannot use fit.(Need to use "materializing" before fit)
    # print FeatureDictVectorizer.feature_names_
    for Sample in AllMalSamples:
        SampleData = CM.ImportFromJson(Sample)
        SampleData = CM.FlattenList(SampleData.values())
        SampleDataDict = OrderedDict()
        # No need to use SampleDataDict. Even if we use traditional dict, the feature vector transformed by Vectorizer
        # should also be in the correct order, because we set sort parameter of vectorizer to be False.
        SampleDataDict = {Value: 1 for Value in SampleData}
        FeatureVector = FeatureDictVectorizer.transform(SampleDataDict)
        # FeatureVectorList = FeatureVector.toarray().tolist()
        # FeatureVectorList = FeatureVector.tolist() if sparse = False
        # CM.ExportToJson(os.path.splitext(Sample)[0]+".fv", FeatureVectorList)
        AllMalFeatureVectors = scipy.sparse.vstack([AllMalFeatureVectors, FeatureVector])
        # Add a new row in sparse matrix.

    for Sample in AllGoodSamples:
        SampleData = CM.ImportFromJson(Sample)
        SampleData = CM.FlattenList(SampleData.values())
        SampleDataDict = OrderedDict()
        # No need to use SampleDataDict. Even if we use traditional dict, the feature vector transformed by Vectorizer
        # should also be in the correct order, because we set sort parameter of vectorizer to be False.
        SampleDataDict = {Value: 1 for Value in SampleData}
        FeatureVector = FeatureDictVectorizer.transform(SampleDataDict)
        # print FeatureVector.__class__
        # FeatureVectorList = FeatureVector.toarray().tolist()
        # FeatureVectorList = FeatureVector.tolist() if sparse = False
        # CM.ExportToJson(os.path.splitext(Sample)[0]+".fv", FeatureVectorList)
        AllGoodFeatureVectores = scipy.sparse.vstack([AllGoodFeatureVectores, FeatureVector])
    CM.DeleteCsrMatrixRow(AllMalFeatureVectors, 0)
    CM.DeleteCsrMatrixRow(AllGoodFeatureVectores, 0)

    # step 2: split all samples to training set and test set (3:1)
    RandomState = random.randint(0, 100)
    TrainMalSamples, TestMalSamples = train_test_split(AllMalFeatureVectors, test_size=0.3, random_state=RandomState)
    TrainMalLabels, TestMalLabels = train_test_split(MalLabels, test_size=0.3, random_state=RandomState)
    TrainGoodSamples, TestGoodSamples = train_test_split(AllGoodFeatureVectores, test_size=0.3,
                                                         random_state=RandomState)
    TrainGoodLabels, TestGoodLabels = train_test_split(GoodLabels, test_size=0.3, random_state=RandomState)
    # Test split will return sparse matrices if the arguments are sparse matrices.
    print "train-test split done"

    TrainSamples = scipy.sparse.vstack([TrainMalSamples, TrainGoodSamples])
    TestSamples = scipy.sparse.vstack([TestMalSamples, TestGoodSamples])

    TrainLabels = TrainMalLabels.tolist()
    TrainLabels.extend(TrainGoodLabels.tolist())
    TestLabels = TestMalLabels.tolist()
    TestLabels.extend(TestGoodLabels.tolist())
    print "Labels array - generated"

    # step 3: model selection

    # LinearSVM = svm.LinearSVC()
    # LinearSVM.fit(TrainSamples, TrainLabels)
    Classifier = OneVsRestClassifier(LinearSVC(random_state=RandomState), n_jobs=ProcessNumber)
    Classifier.fit(TrainSamples, TrainLabels)
    print "CV done - model selected"

    # step 4: Evaluate the best model on test set
    PredictedLabels = Classifier.predict(TestSamples)
    Accuracy = np.mean(PredictedLabels == TestLabels)  # Return (x1 == x2) element-wise.
    print "Test Set Accuracy = ", Accuracy
    print(metrics.classification_report(TestLabels,
                                        PredictedLabels, labels=LabelsForReport,
                                        target_names=TargetNamesForReport))