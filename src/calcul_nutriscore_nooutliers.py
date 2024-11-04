import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
from calcul_nutriscore import NutriScore
from preprocess import Preprocessing
    
def calcul_nutriscore_no_outliers(data, grille, configs):
     # Créer une instance de la classe Preprocessing
    preprocessor = Preprocessing(data, configs)
    
    # Appeler les méthodes sur l'instance de Preprocessing
    gaussian_norm_data_no_outliers, gaussian_norm_outliers = preprocessor.gaussian_normalisation()
    final_data_no_outliers, final_outliers = preprocessor.Denormalisation(gaussian_norm_data_no_outliers, gaussian_norm_outliers)
    
    # Créer une instance de la classe NutriScore
    nutriscore_calculator = NutriScore(final_data_no_outliers, grille, configs)
    
    # Appeler la méthode calcul_nutriscore sur l'instance de NutriScoreCalculator
    nutriscore_no_outliers_nolabel= nutriscore_calculator.calcul_nutriscore()
    nutriscore_no_outliers = nutriscore_calculator.set_scorelabel()

    return nutriscore_no_outliers

path = Path('/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/data_base/RAW_recipes.csv')
path_grille = Path('/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Webapp_git/src/nutrient_table.csv')

configs = {
    'nutritioncolname':['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
    'grillecolname':['dv_calories_%', 'dv_sat_fat_%', "dv_sugar_%", 'dv_sodium_%', 'dv_protein_%'],
    'dv_calories' : 2000
    }

df_nutriscore_no_outliers = calcul_nutriscore_no_outliers(path, path_grille, configs)
print(df_nutriscore_no_outliers)
print(df_nutriscore_no_outliers.shape)
df_nutriscore_no_outliers.info()
print(df_nutriscore_no_outliers.describe())

output_path = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Webapp_git/src/nutrition_table_nutriscore_no_outliers.csv'
df_nutriscore_no_outliers.to_csv(output_path, index=False, header=True, sep=',')

