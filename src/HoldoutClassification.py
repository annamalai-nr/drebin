import numpy as np
import time
import scipy.sparse
import numpy as np
import CommonModules as CM
from sklearn.feature_extraction.text import TfidfVectorizer as TF
from sklearn import svm
from sklearn import metrics
from sklearn.metrics import accuracy_score


def HoldoutClassification(TrainMalSet, TrainGoodSet, TestMalSet, TestGoodSet, FeatureOption):
    '''
    Train a classifier for classifying malwares and goodwares using Support Vector Machine technique.
    Compute the prediction accuracy and f1 score of the classifier.
    Modified from Jiachun's code.

    :param String/List TrainMalSet: absolute path/paths of the malware corpus for trainning set
    :param String/List TrainGoodSet: absolute path/paths of the goodware corpus for trainning set
    :param String/List TestMalSet: absolute path/paths of the malware corpus for test set
    :param String/List TestGoodSet: absolute path/paths of the goodware corpus for test set
    :param String FeatureOption: tfidf or binary, specify how to construct the feature vector
    '''
    # step 1: creating feature vector
    TrainMalSamples = CM.ListFiles(TrainMalSet, ".data")
    TrainGoodSamples = CM.ListFiles(TrainGoodSet, ".data")
    TestMalSamples = CM.ListFiles(TestMalSet, ".data")
    TestGoodSamples = CM.ListFiles(TestGoodSet, ".data")
    print "Loaded Samples"

    FeatureVectorizer = TF(input="filename", tokenizer=lambda x: x.split('\n'), token_pattern=None,
                           binary=FeatureOption)
    x_train = FeatureVectorizer.fit_transform(TrainMalSamples + TrainGoodSamples)
    x_test = FeatureVectorizer.transform(TestMalSamples + TestGoodSamples)

    # label training sets malware as 1 and goodware as -1
    Train_Mal_labels = np.ones(len(TrainMalSamples))
    Train_Good_labels = np.empty(len(TrainGoodSamples))
    Train_Good_labels.fill(-1)
    y_train = np.concatenate((Train_Mal_labels, Train_Good_labels), axis=0)
    print "Training Label array - generated"

    # label testing sets malware as 1 and goodware as -1
    Test_Mal_labels = np.ones(len(TestMalSamples))
    Test_Good_labels = np.empty(len(TestGoodSamples))
    Test_Good_labels.fill(-1)
    y_test = np.concatenate((Test_Mal_labels, Test_Good_labels), axis=0)
    print "Testing Label array - generated"

    # step 2: train the model

    LinearSVM = svm.LinearSVC()
    T0 = time.time()
    LinearSVM.fit(x_train, y_train)
    TrainingTime = round(time.time() - T0,2)
    print "The training time for classification is %s sec." % (TrainingTime)
    # print "CV done - model selected"

    # step 4: Evaluate the best model on test set
    y_pred = LinearSVM.predict(x_test)
    TestingTime = round(time.time() - TrainingTime - T0,2)
    Accuracy = accuracy_score(y_test, y_pred)  # Return (x1 == x2) element-wise.
    print "Test Set Accuracy = ", Accuracy
    print(metrics.classification_report(y_test,
                                        y_pred, labels=[1, -1],
                                        target_names=['Malware', 'Goodware']))
    Report = "Test Set Accuracy = " + str(Accuracy) + "\n" + metrics.classification_report(y_test,
                                                                                           y_pred,
                                                                                           labels=[1, -1],
                                                                                           target_names=['Malware',
                                                                                                         'Goodware'])
    return y_train, y_test, y_pred, TrainingTime, TestingTime
