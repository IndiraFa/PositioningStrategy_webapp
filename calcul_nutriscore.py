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
        self.nutriscore_label = self.set_scorelabel()

    def calcul_nutriscore(self):
        data = self.data.copy()
        data['nutriscore'] = 14.0  # type float

        grillecolname = self.configs['grillecolname']

        for nutrient in grillecolname:
            if nutrient in self.grille.columns:
                nutrient_grille = self.grille
                nutrient_values = data[nutrient].values

                if nutrient == "dv_protein_%":
                    # Vectorized operation for "dv_protein_%"
                    for i, grille_row in nutrient_grille.iterrows():
                        if i == 0:
                            prev_value = -np.inf  # Si c'est la première ligne, utiliser -infini comme valeur inférieure
                        else:
                            prev_value = nutrient_grille[nutrient].iloc[i-1]
                        if np.isnan(grille_row[nutrient]):
                            mask = (-nutrient_values > prev_value)
                            data.loc[mask, 'nutriscore'] -= grille_row['points']
                            break
                        mask = (-nutrient_values > prev_value) & (-nutrient_values <= grille_row[nutrient])
                        data.loc[mask, 'nutriscore'] -= grille_row['points']

                else:
                    # Vectorized operation for other nutrients
                    for i, grille_row in nutrient_grille.iterrows():
                        if i == 0:
                            prev_value = -np.inf  # Si c'est la première ligne, utiliser -infini comme valeur inférieure
                        else:
                            prev_value = nutrient_grille[nutrient].iloc[i-1]
                        if np.isnan(grille_row[nutrient]):
                            mask = (nutrient_values > prev_value)
                            data.loc[mask, 'nutriscore'] -= grille_row['points']
                            break
                        mask = (nutrient_values > prev_value) & (nutrient_values <= grille_row[nutrient])
                        data.loc[mask, 'nutriscore'] -= grille_row['points']
        return data
    
    def set_scorelabel(self):
        score = self.nutriscore
        if 'nutriscore' not in score.columns:
            raise ValueError('The nutriscore column is not in the dataframe')
        score['label'] = ''
        score['label'].where(score['nutriscore'] >= 12, 'A', inplace=True)
        score['label'].where((score['nutriscore'] >= 9) & (score['nutriscore'] < 12), 'B', inplace=True)
        score['label'].where((score['nutriscore'] >= 6) & (score['nutriscore'] < 9), 'C', inplace=True)
        score['label'].where((score['nutriscore'] >= 3) & (score['nutriscore'] < 6), 'D', inplace=True)
        score['label'].where(score['nutriscore'] < 3, 'E', inplace=True)
        return score
        # label = np.empty(score.shape[0], dtype=str)
        # label[np.where(score['nutriscore'] >= 12)][0] = 'A'
        # label[np.where((score['nutriscore'] >= 9) & (score['nutriscore'] < 12))][0] = 'B'
        # label[np.where((score['nutriscore'] >= 6) & (score['nutriscore'] < 9))][0] = 'C'
        # label[np.where((score['nutriscore'] >= 3) & (score['nutriscore'] < 6))][0] = 'D'
        # label[np.where(score['nutriscore'] < 3)][0] = 'E'
        # return label
        

    def get_data(path, configs):
        nutrition_table = Preprocessing(path, configs).formatdata
        nutrition_table_normal = Preprocessing(path, configs).normaldata
        return nutrition_table, nutrition_table_normal

def main():
    # path = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/data_base/RAW_recipes.csv'
    # path_grille = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Webapp_git/PositioningStrategy_webapp/src/nutrient_table.csv'
    path = Path('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/dataset/RAW_recipes.csv')
    path_grille = Path('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/scripts/nutrient_table (1).csv')
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
    print(nutri_score_instance.nutriscore_label)

    # output_path = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/nutrition_table_nutriscore.csv'
    nutrition_table_nutriscore.to_csv(Path(path.parent, 'score.csv'), index=False)

    return nutrition_table_nutriscore

if __name__ == '__main__':
    main()