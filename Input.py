import MainCode
import numpy as np
import flet as ft
from matplotlib import pyplot as plt
from tueplots import bundles
from tueplots.constants.color import rgb


# Function to create the needed Equality and Inequality matrices
# this function might need to be changed in the future when we decide to also consider the Nutritional values of the products
def createMatrices(Ingredients, givenAmounts, Nutrients, page: ft.Page, recipe_name: str):
    plt.rcParams.update(bundles.beamer_moml())
    plt.rcParams.update({"figure.dpi": 200})

    # Number of Ingredients
    D = len(Ingredients)
    print(f"{D} ingredients in total")

    # WE NEED 2D - 1 INEQUALITIES:
    # * all variables should be >0: (D inequality constraints)
    # * the i-th variable is larger than the i+1-th variable, for all i in [1,D-1] (D-1 inequalities)
    #
    # AND 1 + non 0 in givenAmounts EQUALITIES:
    # * all variables should sum to 1 (the D-simplex, 1 equality)
    # * the first variable (gek. Linsen) is 0.63 (1 equality)
    # * the 8th variable (Salz) is equal to 0.016 (1 equality)

    # inequalities A <= a
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

    n = 1 + np.count_nonzero(givenAmounts)

    # equalities B = b
    B = np.zeros((n, D))
    b = np.zeros(n)

    # they all sum to 1:
    B[0, :] = 1
    b[0] = 1

    # other equalities given by the givenAmounts:
    for i in range(D):
        if givenAmounts[i] != None:
            B[n - 1, i] = 1
            b[n - 1] = givenAmounts[i]
            n -= 1

    MainCode.Main(Ingredients, A, a, B, b, Nutrients, page, recipe_name)

    # plt.rcParams.update(bundles.beamer_moml(rel_height=0.5))
    # # Set font because it uses a font which is not on every computer
    # plt.rcParams['font.family'] = 'Arial'
    # fig, axs = plt.subplots(1, 2)
    # imA = axs[0].imshow(A, vmin=-1, vmax=1)
    # axs[0].set_title("A")
    # imB = axs[1].imshow(B, vmin=-1, vmax=1)
    # axs[1].set_title("B")
    # # fig.colorbar(imA, ax=axs[1]);
    # plt.savefig("matrices.pdf")
    #return A, a, B, b


#--------------------------------------------------------------
# Example

Ingredients = [
        "gek. Hülsenfrüchte (braune Berglinsen)",
        "Kokosfett",
        "Sonnenblumenöl",
        "geröstete Zwiebeln (in Sonnenblumenöl)",
        "Zitronensaft",
        "Gewürze",
        "Agavendicksaft",
        "geräuchertes Meersalz",
    ]
givenAmounts = [0.63, None, None, None, None, None, None, 0.016]

#A, a, B, b = createMatrices(Ingredients, givenAmounts)
# MainCode.Main(Ingredients, A, a, B, b)