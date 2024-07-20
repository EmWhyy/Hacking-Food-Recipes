import pandas as pd
import numpy as np

def transform_data():
    # Transform data
    raw_data = pd.read_csv("full_dataset.csv")
    # combine title and NER columns and remove [] from NER 
    raw_data["NER"] =raw_data["NER"].str[1:-1]
    raw_data["NER"] = raw_data["NER"].str.replace("\"", "")
    raw_data["Input"] = "Title: " + raw_data["title"] + " Ingredients: " + raw_data["NER"]
    raw_data = raw_data.drop(columns=["Unnamed: 0", "ingredients", "link", "source", "title", "NER"])
    raw_data = raw_data.rename(columns={"directions": "Output"})
    raw_data["Output"] = raw_data["Output"].str[1:-1]
    raw_data["Output"] = raw_data["Output"].str.replace("\"", "")
    raw_data["Output"] = raw_data["Output"].str.replace(".,", ".")
    #swap columns
    raw_data = raw_data[["Input", "Output"]]
    print(raw_data.head())
    print(raw_data["Output"][100])
    raw_data.to_csv("transformed_data.csv", index=False)

def main():
    transform_data()
    print("Data transformation complete.")

main()