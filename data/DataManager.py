import pandas as pd
from pathlib import Path
import numpy as np

def save_data(Ingredients, Recipe):
    path = Path("data/ingredients.csv")
    if not path.exists():
        df = pd.DataFrame(columns=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'])
        df.to_csv(path, index=False)
    for i in range(20 - len(Ingredients)):
        Ingredients.append(None)
    Ingredients = np.array([Ingredients])
    Ingredients.transpose()
    df = pd.DataFrame(Ingredients)
    df.to_csv(path, mode = 'a', index=False, header=False)

def load_data():
    path = Path("data/ingredients.csv")
    if not path.exists():
        return None
    df = pd.read_csv(path)
    return df