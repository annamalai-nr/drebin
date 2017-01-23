SpPy is a sparse matrix library based on the C++ library Eigen with a similar interface to NumPy. Here is a code snippet: 

:: 

    >>> import numpy 
    >>> from sppy import csarray 
    >>> #Create a new column major dynamic array of float type
    >>> B = csarray((5, 5), storagetype="col") 
    >>> B[3, 3] = -0.2
    >>> B[0, 4] = -1.23
    >>> B[numpy.array([0, 1]), numpy.array([0,1])] = 27
    >>> print(B)
    csarray dtype:float64 shape:(5, 5) non-zeros:4 storage:col
    (0, 0) 27.0
    (1, 1) 27.0
    (3, 3) -0.2
    (0, 4) -1.23
    >>> print(B.sum())
    52.57

More Information 
----------------

* See the user guide at http://pythonhosted.org/sppy/
* The source code is available at https://github.com/charanpald/sppy
