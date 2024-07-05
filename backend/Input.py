import backend.MainCode as MainCode
import numpy as np
import flet as ft
from matplotlib import pyplot as plt
from tueplots import bundles
from tueplots.constants.color import rgb



# Function to create the needed Equality and Inequality matrices
# this function might need to be changed in the future when we decide to also consider the Nutritional values of the products
def createMatrices(Ingredients, givenAmounts, Nutrients, page: ft.Page):
    testResult = checkForSimpleSolutions(Ingredients, givenAmounts, Nutrients, page)
    if testResult is not None:
        result = testResult
    else:
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

        result = MainCode.execute_mcmc(Ingredients, A, a, B, b, Nutrients, page)
    return result


def checkForSimpleSolutions(Ingredients, givenAmounts, Nutrients, page: ft.Page):
    max_index = len(givenAmounts) - 1
    result = None

    temp1 = givenAmounts.copy()
    for ind in range(len(givenAmounts)):
        if givenAmounts[max_index - ind] == None:
            if max_index - ind + 1 < len(givenAmounts):
                temp1[max_index - ind] = temp1[max_index - ind + 1]
            else:
                temp1[max_index - ind] = 0

    temp2 = givenAmounts.copy()
    for ind in range(len(givenAmounts)):
        if givenAmounts[ind] == None:
            if ind - 1 >= 0:
                temp2[ind] = temp2[ind - 1]
            else:
                temp2[ind] = 0

    # print(givenAmounts)
    # print(temp1)
    # print(temp2)

    if(givenAmounts.count(None) == 1):
        # Plots fehlen für diesen Fall noch
        temp = 1 - sum([x for x in givenAmounts if x != None])
        givenAmounts[givenAmounts.index(None)] = temp
        result = np.array([givenAmounts])

    elif(givenAmounts.count(None) == 0):
        # Plots fehlen für diesen Fall noch
        result = np.array([givenAmounts])
    
    elif sum([float(value) for value in temp1]) == 1:
        result = np.array([temp1])
    
    elif sum([float(value) for value in temp2]) == 1:
        result = np.array([temp2])
    
    return result




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
