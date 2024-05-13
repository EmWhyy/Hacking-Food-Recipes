import warnings
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import ticker
from numpy.random import rand, randn
from tqdm import tqdm
from tueplots import bundles
from tueplots.constants.color import rgb
from scipy.optimize import linprog

plt.rcParams.update(bundles.beamer_moml())
plt.rcParams.update({"figure.dpi": 200})

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

plt.rcParams.update(bundles.beamer_moml(rel_height=0.5))
# Set font because it uses a font which is not on every computer
plt.rcParams['font.family'] = 'Arial'
fig, axs = plt.subplots(1, 2)
imA = axs[0].imshow(A, vmin=-1, vmax=1)
axs[0].set_title("A")
imB = axs[1].imshow(B, vmin=-1, vmax=1)
axs[1].set_title("B")
# fig.colorbar(imA, ax=axs[1]);
plt.savefig("matrices.pdf")



def find_initial_point(A, a, B, b):
    D = A.shape[1]
    
    # Surpress deprecation warning
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        out = linprog(np.ones(D), A_ub=A, b_ub=a, A_eq=B, b_eq=b, method="interior-point")
    return out.x

x0 = find_initial_point(A, a, B, b)

# check your implementation:
print(f"Test for inequalities: {np.all(A @ x0 - a < 0)}")
print(f"Test for equalities: {np.allclose(B @ x0 - b,0)}")

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

def MCMC(A, a, B, b, num_iter=int(1e7), thinning=int(1e5)):

    print("finding initial point.")
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
    for i in tqdm(range(num_iter - 1)):
        xi = project_and_sample(xi, sample(), A, a)
        samples[i + 1, :] = xi

    return samples[0::thinning, :]

S = int(1e5)
SAMPLES = MCMC(A, a, B, b, num_iter=S, thinning=int(S / 100))

fig, ax = plt.subplots()
im = ax.imshow(np.log10(SAMPLES.T), aspect="auto")
ax.set_xlabel("# sample")
# ax.set_ylabel('ingredient')
ax.set_yticks(np.arange(D))
ax.set_yticklabels(Zutaten)
cb = fig.colorbar(im)
cb.set_label("$\log_{10} x_i$")

# plt.savefig("Leberwurst_Samples.png")

def acf(x, length=50):
    return np.array([1] + [np.corrcoef(x[:-i], x[i:])[0, 1] for i in range(1, length)])


fig, ax = plt.subplots()
for i in range(4):
    ax.plot(acf(SAMPLES[:, i]))

ax.axhline(0);


#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------


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