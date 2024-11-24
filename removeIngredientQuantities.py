import pandas as pd
import re

filePath = r'RecipeNLG_dataset.csv'
df = pd.read_csv(filePath)

# regular expression to clean the ingredients column

def cleanIngredientsRegex(row):
    # remove numbers, fractions, measurement units, and unnecessary descriptions
    cleaned = re.sub(r"(\d+/\d+|\d+|tsp\.|tbsp\.|cup|pkg\.|c\.|oz\.|lb\.|,)", "", row)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    cleaned= re.sub(r"\(.*?\)", "", cleaned).strip()
    return cleaned

df["cleanedIngredients"] = df["ingredients"].apply(cleanIngredientsRegex)

df.to_csv("cleanedData.csv")