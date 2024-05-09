import numpy as np

#import the functions we want to test
from MainCode import find_initial_point,construct_directions,project_and_sample, MCMC 

#run with: python -m pytest
#tests are only using the first example so far

#tests find_initial_point
def test_find_initial_point():

    D = 8

    #Inequalities
    A = np.zeros((D + D - 1, D))
    a = np.zeros(D + D - 1)
    A[0:D, 0:D] = -np.eye(D)  
    a[0:D] = 0
    for i in range(D - 1):
        A[D + i, i + 1] = 1
        A[D + i, i] = -1
        a[D + i] = 0

    # equalities
    B = np.zeros((3, D))
    b = np.zeros(3)
    B[0, :] = 1
    b[0] = 1
    B[1, 0] = 1
    b[1] = 0.63
    B[2, 7] = 1
    b[2] = 0.016 

    x0 = find_initial_point(A, a, B, b)

  
    assert np.all(A @ x0 - a < 0) == True #currently false, should be true to satistfy Ax < a (or <= ?)
    assert np.allclose(B @ x0 - b,0) == True #should be true to satisfy Bx = b



#tests construct_directions



#tests project_and_sample



#tests MCMC








