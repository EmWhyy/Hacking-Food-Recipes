import pandas as pd
from pathlib import Path
import numpy as np

# Save the data to the csv file
# Ingredients cant be more than 20 
# First 20 columns are the ingredients and the last 6 columns are the nutritional values and last column is the recipe name

def save_data(Ingredients, Nutrients, Recipe):
    path = Path("data/ingredients.csv")
    if not path.exists():
        df = pd.DataFrame(columns=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 'carbs', 'fat', 'protein', 'salt', 'fiber', 'sugar', 'recipe'])
        df.to_csv(path, index=False)
    for i in range(20 - len(Ingredients)):
        Ingredients.append(None)
    Ingredients.extend(Nutrients)
    Ingredients.append(Recipe)
    Ingredients = np.array([Ingredients])
    Ingredients.T
    df = pd.DataFrame(Ingredients)
    df.to_csv(path, mode = 'a', index=False, header=False)

def load_data():
    path = Path("data/ingredients.csv")
    if not path.exists():
        return None
    df = pd.read_csv(path)
    return df