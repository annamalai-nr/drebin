import numpy as np
import scipy.sparse
import time
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer as TF
from sklearn import svm
from sklearn import metrics
from sklearn.metrics import accuracy_score

import random

import CommonModules as CM


def RandomClassification(MalwareCorpus, GoodwareCorpus, TestSize, FeatureOption):
    '''
    Train a classifier for classifying malwares and goodwares using Support Vector Machine technique.
    Compute the prediction accuracy and f1 score of the classifier.
    Modified from Jiachun's code.

    :param String MalwareCorpus: absolute path of the malware corpus
    :param String GoodwareCorpus: absolute path of the goodware corpus
    :param String FeatureOption: tfidf or binary, specify how to construct the feature vector

    :rtype String Report: result report
    '''
    # step 1: creating feature vector

    AllMalSamples = CM.ListFiles(MalwareCorpus, ".data")
    AllGoodSamples = CM.ListFiles(GoodwareCorpus, ".data")
    print "Loaded samples"

    FeatureVectorizer = TF(input='filename', tokenizer=lambda x: x.split('\n'), token_pattern=None,
                           binary=FeatureOption)
    x = FeatureVectorizer.fit_transform(AllMalSamples + AllGoodSamples)

    # label malware as 1 and goodware as -1
    Mal_labels = np.ones(len(AllMalSamples))
    Good_labels = np.empty(len(AllGoodSamples))
    Good_labels.fill(-1)
    y = np.concatenate((Mal_labels, Good_labels), axis=0)
    print "Label array - generated"


    # step 2: split all samples to training set and test set

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=TestSize,
                                                 random_state=random.randint(0, 100))
    print "train-test split done"

    # step 3: train the model

    LinearSVM = svm.LinearSVC()
    T0 = time.time()
    LinearSVM.fit(x_train, y_train)
    print "The training time for random split classification is %s sec." % (round(time.time() - T0,2))
    # print "CV done - model selected"

    # step 4: Evaluate the best model on test set
    T0 = time.time()
    y_pred = LinearSVM.predict(x_test)
    print "The testing time for random split classification is %s sec." % (round(time.time() - T0,2))
    Accuracy = accuracy_score(y_test, y_pred)
    print "Test Set Accuracy = {}".format(Accuracy)
    print(metrics.classification_report(y_test,
                                       y_pred, labels=[1, -1],
                                        target_names=['Malware', 'Goodware']))
    Report = "Test Set Accuracy = " + str(Accuracy) + "\n" + metrics.classification_report(y_test,
                                                                                           y_pred,
                                                                                           labels=[1, -1],
                                                                                           target_names=['Malware',
                                                                                                         'Goodware'])
    # return TestLabels, PredictedLabels
    return Report
