import time
import scipy.sparse
import numpy as np
import CommonModules as CM
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm
from sklearn import metrics
from collections import OrderedDict


def HoldoutClassification(MalwareCorpus, GoodwareCorpus, TestBadSet, TestGoodSet, FeatureDict, FeatureOption):
    '''
    Train a classifier for classifying malwares and goodwares using Support Vector Machine technique.
    Compute the prediction accuracy and f1 score of the classifier.
    Modified from Jiachun's code.

    :param String/List MalwareCorpus: absolute path/paths of the malware corpus for trainning set
    :param String/List GoodwareCorpus: absolute path/paths of the goodware corpus for trainning set
    :param String/List TestBadSet: absolute path/paths of the malware corpus for test set
    :param String/List TestGoodSet: absolute path/paths of the goodware corpus for test set
    :param OrderedDict(String:Int) FeatureDict: Dictionary that stores all features
    :param String FeatureOption: tfidf or binary, specify how to construct the feature vector
    '''
    # step 1: creating feature vector
    AllMalFeatureVectors = scipy.sparse.csr_matrix((1, len(FeatureDict)), dtype=bool)
    AllGoodFeatureVectores = scipy.sparse.csr_matrix((1, len(FeatureDict)), dtype=bool)
    # In order to use scipy.sparse.vstack, there will be one row with zeros appearing in both matrix, so it should not affect the results.
    # Modified. These two rows will be deleted after adding all vectors.

    if type(MalwareCorpus) == list:
        AllMalSamples = []
        for Directory in MalwareCorpus:
            AllMalSamples.extend(CM.ListFiles(Directory, ".data"))
    else:
        AllMalSamples = CM.ListFiles(MalwareCorpus, ".data")
    if type(GoodwareCorpus) == list:
        AllGoodSamples = []
        for Directory in GoodwareCorpus:
            AllGoodSamples.extend(CM.ListFiles(Directory, ".data"))
    else:
        AllGoodSamples = CM.ListFiles(GoodwareCorpus, ".data")

    MalSamplesTrainingSize = len(AllMalSamples)
    GoodSamplesTrainingSize = len(AllGoodSamples)

    if type(TestBadSet) == list:
        for Directory in TestBadSet:
            AllMalSamples.extend(CM.ListFiles(Directory, ".data"))
    else:
        AllMalSamples.extend(CM.ListFiles(TestBadSet, ".data"))
    if type(TestGoodSet) == list:
        for Directory in TestGoodSet:
            AllGoodSamples.extend(CM.ListFiles(Directory, ".data"))
    else:
        AllGoodSamples.extend(CM.ListFiles(TestGoodSet, ".data"))

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
        AllGoodFeatureVectores = scipy.sparse.vstack([AllGoodFeatureVectores, FeatureVector])
    CM.DeleteCsrMatrixRow(AllMalFeatureVectors, 0)
    CM.DeleteCsrMatrixRow(AllGoodFeatureVectores, 0)

    # step 2: split samples to training set and test set

    TrainSamples, TestSamples = (
    AllMalFeatureVectors[:MalSamplesTrainingSize], AllMalFeatureVectors[MalSamplesTrainingSize:])
    TrainGoodSamples, TestGoodSamples = (
    AllGoodFeatureVectores[:GoodSamplesTrainingSize], AllGoodFeatureVectores[GoodSamplesTrainingSize:])
    # Test split will return sparse matrices if the arguments are sparse matrices.
    # print "train-test split done"

    # label malware as 1 and goodware as -1
    TrainMalLabels = np.ones(TrainSamples.shape[0])
    TestMalLabels = np.ones(TestSamples.shape[0])
    TrainGoodLabels = np.empty(TrainGoodSamples.shape[0])
    TrainGoodLabels.fill(-1)
    TestGoodLabels = np.empty(TestGoodSamples.shape[0])
    TestGoodLabels.fill(-1)

    TrainSamples = scipy.sparse.vstack([TrainSamples, TrainGoodSamples])
    TestSamples = scipy.sparse.vstack([TestSamples, TestGoodSamples])

    TrainLabels = TrainMalLabels.tolist()
    TrainLabels.extend(TrainGoodLabels.tolist())
    TestLabels = TestMalLabels.tolist()
    TestLabels.extend(TestGoodLabels.tolist())
    print "Labels array - generated"

    # step 3: train the model

    LinearSVM = svm.LinearSVC()
    T0 = time.time()
    LinearSVM.fit(TrainSamples, TrainLabels)
    TrainningTime = time.time() - T0
    # print "CV done - model selected"

    # step 4: Evaluate the best model on test set
    PredictedLabels = LinearSVM.predict(TestSamples)
    TestingTime = time.time() - TrainningTime - T0
    Accuracy = np.mean(PredictedLabels == TestLabels)  # Return (x1 == x2) element-wise.
    print "Test Set Accuracy = ", Accuracy
    print(metrics.classification_report(TestLabels,
                                        PredictedLabels, labels=[1, -1],
                                        target_names=['Malware', 'Goodware']))
    Report = "Test Set Accuracy = " + str(Accuracy) + "\n" + metrics.classification_report(TestLabels,
                                                                                           PredictedLabels,
                                                                                           labels=[1, -1],
                                                                                           target_names=['Malware',
                                                                                                         'Goodware'])
    return TrainLabels, TestLabels, PredictedLabels, TrainningTime, TestingTime