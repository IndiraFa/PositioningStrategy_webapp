import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path

from preprocess import Preprocessing, Datatools
    
class NutriScore:
    def __init__(self, data, grille, configs):
        self.data = data
        self.grille = pd.read_csv(grille, sep = ',')
        self.configs = configs
        self.nutriscore = self.calcul_nutriscore()

    def calcul_nutriscore(self):
        data = self.data.copy()
        data['nutriscore'] = 14.0  # type float

        grillecolname = self.configs['grillecolname']

        for nutrient in grillecolname:
            if nutrient in self.grille.columns:
                nutrient_grille = self.grille
                first_row = nutrient_grille.iloc[0]
                max_value = first_row[nutrient]
                points = first_row['points']

                nutrient_values = data[nutrient].values

                if nutrient == "dv_protein_%":
                    # Vectorized operation for "dv_protein_%"
                    mask = -nutrient_values <= max_value
                    data.loc[mask, 'nutriscore'] -= points

                    for _, grille_row in nutrient_grille.iterrows():
                        mask = (-nutrient_values > max_value) & (-nutrient_values <= grille_row[nutrient])
                        data.loc[mask, 'nutriscore'] -= grille_row['points']
                        max_value = grille_row[nutrient]

                else:
                    # Vectorized operation for other nutrients
                    mask = nutrient_values <= max_value
                    data.loc[mask, 'nutriscore'] -= points

                    for _, grille_row in nutrient_grille.iterrows():
                        mask = (nutrient_values > max_value) & (nutrient_values <= grille_row[nutrient])
                        data.loc[mask, 'nutriscore'] -= grille_row['points']
                        max_value = grille_row[nutrient]

        return data

    def get_data(path, configs):
        nutrition_table = Preprocessing(path, configs).formatdata
        nutrition_table_normal = Preprocessing(path, configs).normaldata
        return nutrition_table, nutrition_table_normal

def main():
    path = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/data_base/RAW_recipes.csv'
    path_grille = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Webapp_git/PositioningStrategy_webapp/src/nutrient_table.csv'
    configs = {
    'nutritioncolname':['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
    'grillecolname':['dv_calories_%', 'dv_sat_fat_%', "dv_sugar_%", 'dv_sodium_%', 'dv_protein_%'],
    'dv_calories' : 2000
    }

    nutrition_table = Preprocessing(path, configs).formatdata
    nutrition_table_normal = Preprocessing(path, configs).normaldata
    nutri_score_instance = NutriScore(nutrition_table_normal, path_grille, configs)
    nutrition_table_nutriscore = nutri_score_instance.nutriscore
    print(nutrition_table_nutriscore)

    # output_path = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/nutrition_table_nutriscore.csv'
    # nutrition_table_nutriscore.to_csv(output_path, index=False)

    return nutrition_table_nutriscore

if __name__ == '__main__':
    main()