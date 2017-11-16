What does this repository contain?

    This repo contains a python implementation of Arp, Daniel, et al. "DREBIN: Effective and Explainable Detection of Android Malware in Your Pocket." NDSS. 2014.

What package/platform dependencies do I need to have to run the code?

    The code is developed and tested using python 2.7 on Ubuntu 16.04 PC.
    The following packages need to be installed to run the code:
    1. sklearn (==0.18.1)
    2. pebble
    3. glob
    4. joblib (==0.11)

How do I use it?

    Just clone the repo and follow the following instructions:

    1. Move to the "src" folder.

    2. Run 'python Main.py --help' for the input arguments
    Drebin can be run in 2 modes: (1) Random split classification, (2) Holdout classifiction. In random split mode, the apps in the given dataset are split into training and test sets and are used to train and evaluate the malware detection model, respectively. In the holdout classification mode, the apps for the training and test sets are separated from the start by default, or given by user.

    The default value of the arguments of Drebin are:

    --holdout       0 (split the dataset into training and test set and use the same for training and evaluating the model,respectively)
		    1 (the dataset for training and test set are separated from the input)
    --maldir        '../data/small_proto_apks/malware' (malware samples used to train the model)
    --gooddir       '../data/small_proto_apks/goodware' (goodware samples used to train the model)
    --testmaldir    '../data/apks/malware' (malware samples used to test the model. ONLY APPLICABLE IF --holdout IS NOT 0(must be an integer).)
    --testgooddir   '../data/apks/goodware' (goodware samples used to test the model. ONLY APPLICABLE IF --holdout IS NOT 0(must be an integer).)
    --testsize      0.3 (30% of the samples will be used for testing and the remaining 70% will be used to train the model. ONLY APPLICABLE IF --holdout IS 0.)
    --ncpucores     maximum number of CPU cores to be used for multiprocessing (only during the feature extraction phase)
    --model         classifier model will be trained and saved as a .pk1 file(name of file is specified by the user)
    --numfeatforexp 30(number of top features to be shown for each test sample)

    3. Run 'python Main.py --holdout 0 --maldir <folder containing malware apks> --gooddir <folder containing goodware apks>' to build and test a Drebin malware detection model. By defatult, 70% and 30% of the samples will be used for training and testing the model, respectively.

    4. Run 'python Main.py --holdout 1 --maldir <folder containing training set malware apks> --gooddir <folder containing training set goodware apks> --testmaldir <folder containing test set malware apks> --testgooddir <folder containing test set goodware apks>'.

    Functionalities:

    User need to specify which mode* of classification to be done from --holdout option;

    Random split classification:

    **--holdout 0(default)** allows you to do a random split classification for the given malware dataset and benign/goodware dataset.
    The --maldir and --gooddir arguments should be the directories containing malware Apks and benign-ware Apks. The data files will be
    generated automatically before the program does the random split classification.

    Hold-out classification:

    **--holdout 1** allows you to specify the testing set. You can do a hold-out classification for the given training set and test set.
    Beside settling the training set arguments as --holdout 0, You need to specify the testing set arguments in the command line i.e --testmaldir
    and --testgooddir. The txt files will be generated automatically before the program does the hold-out classification.

Who do I talk to?

    In case of issues/difficulties in running the code, please contact me at ANNAMALA002@e.ntu.edu.sg

    You may also contact Arief Kresnadi Ignatius Kasim at arie0010@e.ntu.edu.sg or Loo Jia Yi at e140112@e.ntu.edu.sg
