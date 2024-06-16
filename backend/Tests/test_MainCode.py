import numpy as np
import os 
import sys 
from MainCode import find_initial_point,construct_directions

#run locally with: python -m pytest
#theres a github workflow too

#tests find_initial_point
def test_find_initial_point():

    D = 8 

    # inequalities
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

    #ensure Ax < a 
    assert np.all(A @ x0 - a < 0), "Product of A and x0 minus a should be smaller than 0" 
    #ensure Bx = b
    assert np.allclose(B @ x0 - b,0), "Product of B and x0 minus b should be close to 0" 


#tests construct_directions
def test_construct_directions():
    D = 8
    B = np.zeros((3, D))
    B[0, :] = 1
    B[1, 0] = 1
    B[2, 7] = 1

    sample = construct_directions(B) #get the sample function
    direction = sample() #get a direction vektor from the sample function

    #ensure direction has unit norm 
    assert np.isclose(np.linalg.norm(direction),1), "direction should have unit norm"
    #ensure direction is one-dimensional
    assert np.ndim(direction) == 1, "direction must be one-dimensional"
    #ensure that if Bx-b=0 , B(x+du) = 0 for all d
    assert np.allclose(B @ direction, 0), "Product of B and direction should be close to 0" 







