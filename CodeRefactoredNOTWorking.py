import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker
from numpy.random import rand, randn
from tqdm import tqdm
from tueplots import bundles
from tueplots.constants.color import rgb
from scipy.optimize import linprog

def construct_directions(B):
    """
    The main challenge here is to ensure the equality constraints remain satisfied
    Naïvely using random.multivariatenormal or similar typically adds a "nugget",
    a minimal amount of "noise" to the covariance's diagonal, which messes up the
    equality constaraints. We solve this by actually computing the SVD manually, and
    then setting all directions that have nearly zero singular values to an actual zero.
    """

    _, D = B.shape
    q, s, ut = np.linalg.svd(
        B, full_matrices=False
    )  # the "full_matrices=False" matters, otherwise the next line is garbage
    Q, S, Ut = np.linalg.svd(np.eye(D) - ut.T @ ut)
    S[S < 1e-12] = 0  # set numerically zero to actually zero
    Q[np.abs(Q) < 1e-12] = 0  # do the same for the directions
    R = Q[:, S != 0]  # only keep directions with nonzero singular value
    S = np.sqrt(S[S != 0])

    K = R.shape[1]

    # now define the sampling function, as per usual for multivariate Gaussians:
    def sample():
        u = R @ np.reshape(np.sqrt(S) * randn(K), [K, 1])
        u /= np.linalg.norm(u)
        return u.flatten()

    return sample

def project_and_sample(xi, s, A, a):
    # take direction d, project the inequality constraints Ax <= a onto it, and sample
    y = (A @ xi) - a  # value of inequality constraints
    z = A @ s  # projected onto the slice

    # find the *tightest* of all constraints in both directions (i.e. towards xi + d and xi - d).
    K = len(y)
    upper = np.inf
    lower = -np.inf
    for k in range(K):
        if z[k] > 0:
            upper = np.minimum(upper, -y[k] / z[k])
        elif z[k] < 0:
            lower = np.maximum(lower, -y[k] / z[k])

    # sanity checks:
    assert np.isfinite(lower) and np.isfinite(
        upper
    ), f"lower bound {lower} and upper bound {upper}"  # constraints exist
    #assert ~np.isclose(upper, lower)  # slice has finite length
    #Todo: throw an error because the first values of upper and lower are the same 0 and 0
    
    # sample:
    a = lower + (upper - lower) * np.random.rand()

    return xi + a * s

def MCMC(A, a, B, b,D, num_iter=int(1e7), thinning=int(1e5)):

    print("finding initial point.")
    out = linprog(np.ones(D), A_ub=A, b_ub=a, A_eq=B, b_eq=b)
    x0 = out.x.flatten()

    print("precomputing space of search directions")
    sample = construct_directions(B)

    print("starting MCMC loop")
    samples = np.zeros(shape=(num_iter, D))
    samples[0, :] = x0
    xi = x0
    for i in tqdm(range(num_iter - 1)):
        xi = project_and_sample(xi, sample(), A, a)
        samples[i + 1, :] = xi

    return samples[0::thinning, :]


#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------

def input(Zutaten):
    D = len(Zutaten)
    
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
    
    # count the number of given values
    given_numbers = sum(value is not None for value in Zutaten.values()) + 1
    
    # equalities
    B = np.zeros((given_numbers, D))
    b = np.zeros(given_numbers)
    
    # get the positions of the given values
    posititons = []
    for i, value in enumerate(Zutaten.values()):
        if value is not None:
            posititons.append(i)
    
    # they all sum to 1:
    B[0, :] = 1 
    b[0] = 1
    
    # fill the equalities
    for i, position in enumerate(posititons):
        B[i+1, position] = 1
        b[i+1] = Zutaten[list(Zutaten.keys())[position]]
        
    return A, a, B, b, D

def run_samples(A, a, B, b, D, num_iter=int(1e5), thinning=int(int(1e5/100))):
    SAMPLES = MCMC(A, a, B, b, D, num_iter=num_iter, thinning=thinning)
    return SAMPLES
    
def output(samples, Zutaten, D, dish_name = ""):
    mean_sample = np.mean(samples, axis=0)
    std_sample = np.std(samples, axis=0)

    print(f"MCMC predictions from {samples.shape[0]:d} (thinned) samples:")
    print("Dish: ", dish_name)
    print(f"{D} ingredients in total")
    print("=" * 66)
    for i, zutat in enumerate(Zutaten):
        print(
            "{:>42}".format(zutat)
            + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
        )
    print("=" * 66)  
    
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

Zutaten_mengen = {
    "gek. Hülsenfrüchte (braune Berglinsen)": 0.63,
    "Kokosfett": None,
    "Sonnenblumenöl": None,
    "geröstete Zwiebeln (in Sonnenblumenöl)": None,
    "Zitronensaft": None,
    "Gewürze": None,
    "Agavendicksaft": None,
    "geräuchertes Meersalz": 0.016,
}

A,a,B,b,D = input(Zutaten_mengen)

SAMPLES = run_samples(A, a, B, b, D, num_iter=int(1e6), thinning=int(int(1e5/100)))
output(SAMPLES, Zutaten_mengen, D, "Linsen-Salat")
                      


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

# # equalities
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
# SAMPLES = MCMC(A, a, B, b, num_iter=int(1e5), thinning=int(int(1e5/100)))
# output(SAMPLES, Zutaten, "Linsen-Salat")



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
# SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))
# output(SAMPLES, Zutaten)

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
# SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))
# output(SAMPLES, Zutaten)