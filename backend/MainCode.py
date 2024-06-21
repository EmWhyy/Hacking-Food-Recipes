import warnings
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from numpy.random import rand, randn
from tqdm import tqdm
from tueplots import bundles
from tueplots.constants.color import rgb
from scipy.optimize import linprog
import flet as ft
import os
from io import BytesIO
#import data.DataManager as DataManager
import logging
from time import sleep

logging.getLogger('matplotlib.font_manager').disabled = True
matplotlib.use('Agg')



def execute_mcmc(Zutaten, A, a, B, b, Nutrients, page: ft.Page):
    D = len(Zutaten)

    x0 = find_initial_point(A, a, B, b)

    # check your implementation:
    print(f"Test for inequalities: {np.all(A @ x0 - a < 0)}")
    print(f"Test for equalities: {np.allclose(B @ x0 - b,0)}")

    # now we can start the MCMC loop
    S = int(1e5)
    SAMPLES = MCMC(D, A, a, B, b,page, num_iter=S, thinning=int(S / 100))
    
    # plots 
    script_dir = os.path.dirname(os.path.realpath(__file__))
    asset_dir = os.path.join(script_dir, "plots")
    
    # plot_sample(SAMPLES, Zutaten, D, asset_dir)
    # DataManager.save_data(Zutaten, Nutrients, recipe_name)
    
    return SAMPLES
    
    


def find_initial_point(A, a, B, b):
    D = A.shape[1]
    
    # Surpress deprecation warning
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        out = linprog(np.ones(D), A_ub=A, b_ub=a, A_eq=B, b_eq=b, method="interior-point")
    return out.x

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
        if np.linalg.norm(u) != 0:
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
        else:
            upper = np.minimum(upper, 1)
            lower = np.maximum(lower, 0)

    # sanity checks:
    assert np.isfinite(lower) and np.isfinite(
        upper
    ), f"lower bound {lower} and upper bound {upper}"  # constraints exist
    #assert ~np.isclose(upper, lower)  # slice has finite length
    #Todo: throw an error because the first values of upper and lower are the same 0 and 0
    
    # sample:
    a = lower + (upper - lower) * np.random.rand()

    return xi + a * s

def MCMC(D, A, a, B, b,page: ft.Page, num_iter=int(1e7), thinning=int(1e5)):

    print("finding initial point.")
    
    # suppress deprecation warning
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        out = linprog(np.ones(D), A_ub=A, b_ub=a, A_eq=B, b_eq=b, method="interior-point")
    x0 = out.x.flatten()

    print("precomputing space of search directions")
    sample = construct_directions(B)

    print("starting MCMC loop")
    samples = np.zeros(shape=(num_iter, D))
    samples[0, :] = x0
    xi = x0
    
    # show progress bar in flet UI
    loading_bar = ft.ProgressBar(width=610)
    page.add(loading_bar)
    
    for i in tqdm(range(num_iter - 1)):
        xi = project_and_sample(xi, sample(), A, a)
        samples[i + 1, :] = xi
        
        # update progress bar
        if i % (num_iter // 100) == 0:
            loading_bar.value = i/num_iter
            sleep(0.01)
            page.update()
    sleep(0.3)
    page.remove(loading_bar)
    

    return samples[0::thinning, :]

def acf(x, length=50):
    return np.array([1] + [np.corrcoef(x[:-i], x[i:])[0, 1] for i in range(1, length)])


def output(samples, Zutaten, D, page: ft.Page ,recipe_name = ""):
    mean_sample = np.mean(samples, axis=0)
    std_sample = np.std(samples, axis=0)

    if page:
        page.add(ft.Text("Dish: " + recipe_name))
        page.add(ft.Text(f"{D} ingredients in total"))
        page.add(ft.Text("=" * 66))
        for i, zutat in enumerate(Zutaten):
            page.add(ft.Text("{:>42}".format(zutat) + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"))
        page.add(ft.Text("=" * 66))

    print(f"MCMC predictions from {samples.shape[0]:d} (thinned) samples:")
    print("Dish: ", recipe_name)
    print(f"{D} ingredients in total")
    print("=" * 66)
    for i, zutat in enumerate(Zutaten):
        print(
            "{:>42}".format(zutat)
            + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
        )
    print("=" * 66)


def plot_sample(SAMPLES, Zutaten, D, path):
    plt.rcParams['font.family'] = 'Arial'
    fig, ax = plt.subplots()
    im = ax.imshow(np.log10(SAMPLES.T), aspect="auto")
    ax.set_xlabel("# sample")
    ax.set_yticks(np.arange(D))
    ax.set_yticklabels(Zutaten)
    cb = fig.colorbar(im)
    cb.set_label(r"$\log_{10} x_i$")
    # plt.savefig(os.path.join(path, "Samples.png"))
    # plt.close('all')  # Close the plot

# Zutaten = [
#     "gek. Hülsenfrüchte (rote & braune Berglinsen)",
#     "Kokosfett",
#     "Sonnenblumenöl",
#     "Gewüre (u.a. Senf)",
#     "Zitronensaft",
#     "geräuchertes Meersalz",
#     "Agavendicksaft",
#     "Shiitake",
# ]

# D = len(Zutaten)
# print(f"{D} ingredients in total")

# # WE NEED 2D - 1 INEQUALITIES:
# # * all variables should be >0: (D inequality constraints)
# # * the i-th variable is larger than the i+1-th variable, for all i in [1,D-1] (D-1 inequalities)
# #
# # AND 4 EQUALITIES:
# # * all variables should sum to 1 (the D-simplex, 1 equality)
# # * the first variable (gek. Linsen) is 0.66 (1 equality)
# # * the 2nd and third variables (Fat & Oils) together are equal to 0.25 (1 equality)
# # * the 6th variable (salt) is 0.015

# # inequalities
# A = np.zeros((D + D - 1, D))
# a = np.zeros(D + D - 1)

# # first, the >=0 inequality
# A[0:D, 0:D] = -np.eye(D)  # note the minus, for the >= equality
# a[0:D] = 0

# # then the ordering:
# for i in range(D - 1):
#     A[D + i, i + 1] = 1
#     A[D + i, i] = -1
#     a[D + i] = 0

# # equalities
# B = np.zeros((4, D))
# b = np.zeros(4)

# # they all sum to 1:
# B[0, :] = 1
# b[0] = 1

# # the first variable (Linsen) is 0.66:
# B[1, 0] = 1
# b[1] = 0.66

# # * the 2nd and third variables (Fat & Oils) together are equal to 0.25 (1 equality)
# B[2, 1] = 1
# B[2, 2] = 1
# b[2] = 0.25

# # * the 6th variable (salt) is 0.015
# B[3, 5] = 1
# b[3] = 0.015


# S = int(1e5)
# SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))

# mean_sample = np.mean(SAMPLES, axis=0)
# std_sample = np.std(SAMPLES, axis=0)

# print(f"MCMC predictions from {SAMPLES.shape[0]:d} (thinned) samples:")
# print("=" * 66)
# for i, zutat in enumerate(Zutaten):
#     print(
#         "{:>48}".format(zutat)
#         + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
#     )
# print("=" * 66)

# Zutaten = [
#     "gek. Hülsenfrüchte (rote Linsen)",
#     "Sonnenblumenöl",
#     "Kokosfett",
#     "Tomatenmark",
#     "geräuchertes Meersalz",
#     "Gewürze (u.a. Sellerie, Senf)",
#     "Zitronensaft",
# ]

# D = len(Zutaten)
# print(f"{D} ingredients in total")

# # WE NEED 2D - 1 INEQUALITIES:
# # * all variables should be >0: (D inequality constraints)
# # * the i-th variable is larger than the i+1-th variable, for all i in [1,D-1] (D-1 inequalities)
# #
# # AND 4 EQUALITIES:
# # * all variables should sum to 1 (the D-simplex, 1 equality)
# # * the first variable (gek. Linsen) is 0.55 (1 equality)
# # * the 2nd and third variables (Fat & Oils) together are equal to 0.31 (1 equality)
# # * the 5th variable (salt) is 0.02

# # inequalities
# A = np.zeros((D + D - 1, D))
# a = np.zeros(D + D - 1)

# # first, the >=0 inequality
# A[0:D, 0:D] = -np.eye(D)  # note the minus, for the >= equality
# a[0:D] = 0

# # then the ordering:
# for i in range(D - 1):
#     A[D + i, i + 1] = 1
#     A[D + i, i] = -1
#     a[D + i] = 0

# # equalities
# B = np.zeros((4, D))
# b = np.zeros(4)

# # they all sum to 1:
# B[0, :] = 1
# b[0] = 1

# # the first variable (Linsen) is 0.55:
# B[1, 0] = 1
# b[1] = 0.55

# # * the 2nd and third variables (Fat & Oils) together are equal to 0.31 (1 equality)
# B[2, 1] = 1
# B[2, 2] = 1
# b[2] = 0.31

# # * the 5th variable (salt) is 0.015
# B[3, 4] = 1
# b[3] = 0.02


# S = int(1e5)
# SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))

# mean_sample = np.mean(SAMPLES, axis=0)
# std_sample = np.std(SAMPLES, axis=0)

# print(f"MCMC predictions from {SAMPLES.shape[0]:d} (thinned) samples:")
# print("=" * 66)
# for i, zutat in enumerate(Zutaten):
#     print(
#         "{:>48}".format(zutat)
#         + f": {mean_sample[i] * 100:5.2g}% +/- {2*std_sample[i] * 100:4.2f}%"
#     )
# print("=" * 66)