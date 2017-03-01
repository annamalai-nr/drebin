## **How do I get set up?** ##
***
* Install Anaconda

    Anaconda is a completely free Python distribution (including for commercial use and redistribution). It includes over 195 of the most popular Python packages for science, math, engineering, data analysis.
Download from [http://continuum.io/downloads](http://continuum.io/downloads).

* Download this repository
* (Optional) Install Visual Studio 2015 with Python Tools

    You may see there are solution files inside the repository. You may want to use Visual Studio 2015 to open it and do some modifications.

* Done. Follow the **How do I use it?** section below to do your experiments.

## **Who do I talk to?** ##
***
* You may send email to [e120060@e.ntu.edu.sg](mailto:e120060@e.ntu.edu.sg) to seek help~
* You may also contact Annamalai at ANNAMALA002@e.ntu.edu.sg

## **How do I use it?** ##
***
1. Drebin

    For Drebin, please make the repository folder as the current working directory. The arguments of Drebin are: 

    MalwareDirectory, GoodwareDirectory, TestBad, TestGood, ProcessNumber, Option**

    You have to specify at least **MalwareDirectory, GoodwareDirectory** before conducting any experiments.

    a. Meaning of the parameters:

    * MalwareDirectory: The location of the malware training set folder. It can be an absolute path of folder that contains all malware Apks or a folder that contains folders of malware Apks(used for malware family analysis and malware online analysis). More details will be shown in the functionality section.
    * GoodwareDirectory: The location of the benign-ware training set folder. It is an absolute path of folder that contains all benign-ware Apks.
    * TestBad: The location of the malware training set folder. It is an absolute path of folder that contains all malware Apks.
    * TestGood: The location of the benign-ware training set folder. It is an absolute path of folder that contains all benign-ware Apks.
    * ProcessNumber: The number of processes that you want to parallelly run. It depends on how many cores your CPU have. E.g. If you have Intel 4 cores Core i7 CPU, then you’d better set this parameter to be 3. (One core for you to do some other tasks.)
    * Option: Set this parameter to do automatically execution of Drebin. If you want to do Drebin experiments manually, i.e. select what functionality you want to use, you should leave this parameter as empty.

    b. Functionalities:

    Once you run Drebin without setting the Option parameter, you shall see some prompts to let you input the Option. Each option corresponds to one functionality.

    1. Random split classification:

        **Option 1** allows you to do a random split classification for the given malware dataset and benign-ware dataset. The MalwareDirectory and GoodwareDirectory parameters should be the directories containing malware Apks and benign-ware Apks. The program will ask you to generate the missing data files for all Apks. (If you run the code for the first time, you need to generate the data files by input “Y”, otherwise you can input “N”.) After the data files are generated, the program will do the random split classification automatically.

    2. Hold-out classification:

        **Option 2** allows you to specify the testing set. You can do a hold-out classification for the given trainning set and test set. Beside seting the trainning set arguments as Option 1, you need to specify the testing set parameters in the command line arguments, i.e. TestBad and TestGood. The program will ask you to generate the missing data files for all Apks. (If you run the code for the first time, you need to generate the data files by input “Y”, otherwise you can input “N”.) After the data files are generated, the program will do the hold-out classification automatically.
