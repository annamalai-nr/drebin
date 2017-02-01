import scipy.sparse
import numpy as np
import time
from sklearn.feature_extraction import DictVectorizer
from sklearn.cross_validation import train_test_split
from sklearn import svm
from sklearn import metrics
import random
from collections import OrderedDict

import CommonModules as CM


def RandomClassification(MalwareCorpus, GoodwareCorpus, FeatureDict, FeatureOption):
    '''
    Train a classifier for classifying malwares and goodwares using Support Vector Machine technique.
    Compute the prediction accuracy and f1 score of the classifier.
    Modified from Jiachun's code.

    :param String MalwareCorpus: absolute path of the malware corpus
    :param String GoodwareCorpus: absolute path of the goodware corpus
    :param OrderedDict(String:Int) FeatureDict: Dictionary that stores all features
    :param String FeatureOption: tfidf or binary, specify how to construct the feature vector

    :rtype String Report: result report
    '''
    # step 1: creating feature vector
    AllMalFeatureVectors = scipy.sparse.csr_matrix((1, len(FeatureDict)), dtype=bool)
    AllGoodFeatureVectores = scipy.sparse.csr_matrix((1, len(FeatureDict)), dtype=bool)
    # In order to use scipy.sparse.vstack, there will be one row with zeros appearing in both matrix, so it should not affect the results.
    # Modified. These two rows will be deleted after adding all vectors.

    AllMalSamples = CM.ListFiles(MalwareCorpus, ".data")
    AllGoodSamples = CM.ListFiles(GoodwareCorpus, ".data")
    print "Loaded samples"

    FeatureDictVectorizer = DictVectorizer(sort=False)  # Set sparse = False if necessary(Need to change the code below)
    FeatureDictVectorizer.fit_transform(FeatureDict)  # Cannot use fit.(Need to use "materializing" before fit)
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
        # print FeatureVector.__class__
        # FeatureVectorList = FeatureVector.toarray().tolist()
        # FeatureVectorList = FeatureVector.tolist() if sparse = False
        # CM.ExportToJson(os.path.splitext(Sample)[0]+".fv", FeatureVectorList)
        AllGoodFeatureVectores = scipy.sparse.vstack([AllGoodFeatureVectores, FeatureVector])
    CM.DeleteCsrMatrixRow(AllMalFeatureVectors, 0)
    CM.DeleteCsrMatrixRow(AllGoodFeatureVectores, 0)

    # step 2: split all samples to training set and test set

    TrainSamples, TestSamples = train_test_split(AllMalFeatureVectors, test_size=0.3,
                                                 random_state=random.randint(0, 100))
    TrainGoodSamples, TestGoodSamples = train_test_split(AllGoodFeatureVectores, test_size=0.3,
                                                         random_state=random.randint(0, 100))
    # Test split will return sparse matrices if the arguments are sparse matrices.
    print "train-test split done"

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
    print "The trainning time for random split classification is %s sec." % (time.time() - T0)
    # print "CV done - model selected"

    # step 4: Evaluate the best model on test set
    T0 = time.time()
    PredictedLabels = LinearSVM.predict(TestSamples)
    print "The testing time for random split classification is %s sec." % (time.time() - T0)
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
    # return TestLabels, PredictedLabels
    return Report