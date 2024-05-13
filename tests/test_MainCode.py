import numpy as np
import os 
import sys 
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  
from MainCode import find_initial_point,construct_directions,project_and_sample, MCMC 

#run with: python -m pytest
#tests are only using the first example so far

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



#tests project_and_sample
"""
def test_project_and_sample():
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


    xi = find_initial_point(A, a, B, b)
    s = construct_directions(B) 

    result = project_and_sample(xi, s(), A, a)

 """





#tests MCMC
def test_MCMC():
    """
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

    S = int(1e5)
    SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))
    """
    





#Examples
#
#first Example: Leberwurst
"""
Zutaten = [
    "gek. Hülsenfrüchte (braune Berglinsen)",
    "Kokosfett",
    "Sonnenblumenöl",
    "geröstete Zwiebeln (in Sonnenblumenöl)",
    "Zitronensaft",
    "Gewürze",
    "Agavendicksaft",
    "geräuchertes Meersalz",
]

D = len(Zutaten)
print(f"{D} ingredients in total")

# WE NEED 2D - 1 INEQUALITIES:
# * all variables should be >0: (D inequality constraints)
# * the i-th variable is larger than the i+1-th variable, for all i in [1,D-1] (D-1 inequalities)
#
# AND 3 EQUALITIES:
# * all variables should sum to 1 (the D-simplex, 1 equality)
# * the first variable (gek. Linsen) is 0.63 (1 equality)
# * the 8th variable (Salz) is equal to 0.016 (1 equality)

# inequalities
A = np.zeros((D + D - 1, D))
a = np.zeros(D + D - 1)

# first, the >=0 inequality
A[0:D, 0:D] = -np.eye(D)  # note the minus, for the >= equality
a[0:D] = 0

# then the ordering:
for i in range(D - 1):
    A[D + i, i + 1] = 1
    A[D + i, i] = -1
    a[D + i] = 0

# equalities
B = np.zeros((3, D))
b = np.zeros(3)

# they all sum to 1:
B[0, :] = 1
b[0] = 1

# the first variable (Linsen) is 0.63:
B[1, 0] = 1
b[1] = 0.63

# * the 8th variable (Salz) is equal to 0.016 (1 equality)
B[2, 7] = 1
b[2] = 0.016

...

# SAMPLES = MCMC(A, a, B, b, num_iter=int(1e6), thinning=int(1e4))
mean_sample = np.mean(SAMPLES, axis=0)
std_sample = np.std(SAMPLES, axis=0)

print(f"MCMC predictions from {SAMPLES.shape[0]:d} (thinned) samples:")
print("=" * 56)
for i, zutat in enumerate(Zutaten):
    print(
        "{:>38}".format(zutat)
        + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
    )
print("=" * 56)
"""

#second example: Pastete
"""
Zutaten = [
    "gek. Hülsenfrüchte (rote & braune Berglinsen)",
    "Kokosfett",
    "Sonnenblumenöl",
    "Gewüre (u.a. Senf)",
    "Zitronensaft",
    "geräuchertes Meersalz",
    "Agavendicksaft",
    "Shiitake",
]

D = len(Zutaten)
print(f"{D} ingredients in total")

# WE NEED 2D - 1 INEQUALITIES:
# * all variables should be >0: (D inequality constraints)
# * the i-th variable is larger than the i+1-th variable, for all i in [1,D-1] (D-1 inequalities)
#
# AND 4 EQUALITIES:
# * all variables should sum to 1 (the D-simplex, 1 equality)
# * the first variable (gek. Linsen) is 0.66 (1 equality)
# * the 2nd and third variables (Fat & Oils) together are equal to 0.25 (1 equality)
# * the 6th variable (salt) is 0.015

# inequalities
A = np.zeros((D + D - 1, D))
a = np.zeros(D + D - 1)

# first, the >=0 inequality
A[0:D, 0:D] = -np.eye(D)  # note the minus, for the >= equality
a[0:D] = 0

# then the ordering:
for i in range(D - 1):
    A[D + i, i + 1] = 1
    A[D + i, i] = -1
    a[D + i] = 0

# equalities
B = np.zeros((4, D))
b = np.zeros(4)

# they all sum to 1:
B[0, :] = 1
b[0] = 1

# the first variable (Linsen) is 0.66:
B[1, 0] = 1
b[1] = 0.66

# * the 2nd and third variables (Fat & Oils) together are equal to 0.25 (1 equality)
B[2, 1] = 1
B[2, 2] = 1
b[2] = 0.25

# * the 6th variable (salt) is 0.015
B[3, 5] = 1
b[3] = 0.015

S = int(1e5)
SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))

mean_sample = np.mean(SAMPLES, axis=0)
std_sample = np.std(SAMPLES, axis=0)

print(f"MCMC predictions from {SAMPLES.shape[0]:d} (thinned) samples:")
print("=" * 66)
for i, zutat in enumerate(Zutaten):
    print(
        "{:>48}".format(zutat)
        + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
    )
print("=" * 66)

"""
#third example: Teewurst
"""
Zutaten = [
    "gek. Hülsenfrüchte (rote Linsen)",
    "Sonnenblumenöl",
    "Kokosfett",
    "Tomatenmark",
    "geräuchertes Meersalz",
    "Gewürze (u.a. Sellerie, Senf)",
    "Zitronensaft",
]

D = len(Zutaten)
print(f"{D} ingredients in total")

# WE NEED 2D - 1 INEQUALITIES:
# * all variables should be >0: (D inequality constraints)
# * the i-th variable is larger than the i+1-th variable, for all i in [1,D-1] (D-1 inequalities)
#
# AND 4 EQUALITIES:
# * all variables should sum to 1 (the D-simplex, 1 equality)
# * the first variable (gek. Linsen) is 0.55 (1 equality)
# * the 2nd and third variables (Fat & Oils) together are equal to 0.31 (1 equality)
# * the 5th variable (salt) is 0.02

# inequalities
A = np.zeros((D + D - 1, D))
a = np.zeros(D + D - 1)

# first, the >=0 inequality
A[0:D, 0:D] = -np.eye(D)  # note the minus, for the >= equality
a[0:D] = 0

# then the ordering:
for i in range(D - 1):
    A[D + i, i + 1] = 1
    A[D + i, i] = -1
    a[D + i] = 0

# equalities
B = np.zeros((4, D))
b = np.zeros(4)

# they all sum to 1:
B[0, :] = 1
b[0] = 1

# the first variable (Linsen) is 0.55:
B[1, 0] = 1
b[1] = 0.55

# * the 2nd and third variables (Fat & Oils) together are equal to 0.31 (1 equality)
B[2, 1] = 1
B[2, 2] = 1
b[2] = 0.31

# * the 5th variable (salt) is 0.015
B[3, 4] = 1
b[3] = 0.02 

S = int(1e5)
SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))

mean_sample = np.mean(SAMPLES, axis=0)
std_sample = np.std(SAMPLES, axis=0)

print(f"MCMC predictions from {SAMPLES.shape[0]:d} (thinned) samples:")
print("=" * 66)
for i, zutat in enumerate(Zutaten):
    print(
        "{:>48}".format(zutat)
        + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
    )
print("=" * 66)

"""
#fourth example: Cabanossi
"""
Zutaten = [
    "gek. Hülsenfrüchte (rote Linsen)",
    "Kokosfett",
    "Sonnenblumenöl",
    "Gewürze (u.a. Sellerie, Senf)",
    "Tomatenmark",
    "geräuchertes Meersalz",
    "Zitronensaft",
    "Agavendicksaft",
    "Chili",
]

D = len(Zutaten)
print(f"{D} ingredients in total")

# WE NEED 2D - 1 INEQUALITIES:
# * all variables should be >0: (D inequality constraints)
# * the i-th variable is larger than the i+1-th variable, for all i in [1,D-1] (D-1 inequalities)
#
# AND 4 EQUALITIES:
# * all variables should sum to 1 (the D-simplex, 1 equality)
# * the first variable (gek. Linsen) is 0.61 (1 equality)
# * the 2nd and third variables (Fat & Oils) together are equal to 0.28 (1 equality)
# * the 6th variable (salt) is 0.021

# inequalities
A = np.zeros((D + D - 1, D))
a = np.zeros(D + D - 1)

# first, the >=0 inequality
A[0:D, 0:D] = -np.eye(D)  # note the minus, for the >= equality
a[0:D] = 0

# then the ordering:
for i in range(D - 1):
    A[D + i, i + 1] = 1
    A[D + i, i] = -1
    a[D + i] = 0

# equalities
B = np.zeros((4, D))
b = np.zeros(4)

# they all sum to 1:
B[0, :] = 1
b[0] = 1

# the first variable (Linsen) is 0.61:
B[1, 0] = 1
b[1] = 0.61

# * the 2nd and third variables (Fat & Oils) together are equal to 0.28 (1 equality)
B[2, 1] = 1
B[2, 2] = 1
b[2] = 0.28

# * the 6th variable (salt) is 0.015
B[3, 5] = 1
b[3] = 0.021

S = int(1e5)
SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))

mean_sample = np.mean(SAMPLES, axis=0)
std_sample = np.std(SAMPLES, axis=0)

print(f"MCMC predictions from {SAMPLES.shape[0]:d} (thinned) samples:")
print("=" * 66)
for i, zutat in enumerate(Zutaten):
    print(
        "{:>48}".format(zutat)
        + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
    )
print("=" * 66)

"""
#fith example: Currywurst 
"""
Zutaten = [
    "gek. Hülsenfrüchte (rote Linsen)",
    "Kokosfett",
    "passierte Tomaten",
    "Sonnenblumenöl",
    "Agavendicksaft",
    "Tomatenmark",
    "Gewürze (Curry!)",
    "geräuchertes Meersalz",
    "geröstete Zwiebeln",
    "Zitronensaft",
    "Shiitake",
]

D = len(Zutaten)
print(f"{D} ingredients in total")

# WE NEED 2D - 1 INEQUALITIES:
# * all variables should be >0: (D inequality constraints)
# * the i-th variable is larger than the i+1-th variable, for all i in [1,D-1] (D-1 inequalities)
#
# AND 4 EQUALITIES:
# * all variables should sum to 1 (the D-simplex, 1 equality)
# * the first variable (gek. Linsen) is 0.50 (1 equality)
# * the 3nd and 4th variables (Fat & Oils) together are equal to 0.21 (1 equality)
# * the 8th variable (salt) is 0.021

# inequalities
A = np.zeros((D + D - 1, D))
a = np.zeros(D + D - 1)

# first, the >=0 inequality
A[0:D, 0:D] = -np.eye(D)  # note the minus, for the >= equality
a[0:D] = 0

# then the ordering:
for i in range(D - 1):
    A[D + i, i + 1] = 1
    A[D + i, i] = -1
    a[D + i] = 0

# equalities
B = np.zeros((4, D))
b = np.zeros(4)

# they all sum to 1:
B[0, :] = 1
b[0] = 1

# the first variable (Linsen) is 0.50:
B[1, 0] = 1
b[1] = 0.50

# * the 3nd and fourth variables (Fat & Oils) together are equal to 0.21 (1 equality)
B[2, 1] = 1
B[2, 2] = 1
b[2] = 0.21

# * the 8th variable (salt) is 0.021
B[3, 7] = 1
b[3] = 0.021 

S = int(1e5)
SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))

mean_sample = np.mean(SAMPLES, axis=0)
std_sample = np.std(SAMPLES, axis=0)

print(f"MCMC predictions from {SAMPLES.shape[0]:d} (thinned) samples:")
print("=" * 66)
for i, zutat in enumerate(Zutaten):
    print(
        "{:>48}".format(zutat)
        + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
    )
print("=" * 66)

"""
