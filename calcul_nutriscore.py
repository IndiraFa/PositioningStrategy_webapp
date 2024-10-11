import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path

class datatools:
    def get_value_from_string(string):
    # Utilisation de re.findall pour extraire les nombres (flottants et entiers)
        numbers = re.findall(r"\d+\.\d+|\d+", string)
        # Convertir les nombres extraits en float ou int
        numbers = [float(num) if '.' in num else int(num) for num in numbers]
        return numbers


class preprocessing:
    def __init__(self, path, configs):
        self.rawdata = pd.read_csv(path, sep = ',')
        self.configs = configs
        self.formatdata = self.get_formatted_nutrition()
        self.normaldata = self.set_dv_normalisation()
    
    def get_raw_nutrition(self):
        return self.rawdata['nutrition']
    
    def get_formatted_nutrition(self):
        data = self.get_raw_nutrition()
        formatted_data = data.apply(datatools.get_value_from_string)
        table = pd.DataFrame(formatted_data.tolist(), columns=self.configs['nutritioncolname'])
        return table
    
    def set_dv_normalisation(self):
        # ajouter une colonne dv_calories_% pour normaliser les valeurs nutritionnelles 
        # par rapport aux apports journaliers recommandés
        dv_calories = self.configs['dv_calories']
        fttable = self.formatdata
        table = pd.DataFrame()
        table['dv_calories_%'] = fttable['calories'] * 100 / dv_calories
        for col in self.configs['nutritioncolname'][1:]:
            table[f'dv_{col}'] = fttable[col] * dv_calories /fttable['calories']
        return table
    
class NutriScore:
    def __init__(self, data, grille, configs):
        self.data = data
        self.grille = pd.read_csv(grille, sep = ';')
        print("Colonnes de self.grille:", self.grille.columns)
        self.configs = configs
        self.nutriscore = self.calcul_nutriscore()
        self.plot = self.plot_nutriscore()

    def calcul_nutriscore(self):
        data = self.data.copy()
        data['nutriscore'] = 14
        print("Colonnes de data:", data.columns)  # Ligne de débogage

        grillecolname = self.configs['grillecolname']

        for nutrient in grillecolname:
            print("Traitement du nutrient:", nutrient)  # Ligne de débogage
            if nutrient in self.grille.columns:
                nutrient_grille = self.grille
                first_row = nutrient_grille.iloc[0]
                max_value = first_row[nutrient]
                points = first_row['points']

                for index, row in data.iterrows():
                    value = row[nutrient]

                    if nutrient == "dv_protein_%":
                        if -value <= max_value:
                            data.at[index, 'nutriscore'] -= points
                        else:
                            for grille_index, grille_row in nutrient_grille.iterrows():
                                if -value <= grille_row[nutrient]:
                                    data.at[index, 'nutriscore'] -= grille_row['points']
                                    break 
                                elif pd.isna(grille_row[nutrient]):
                                    data.at[index, 'nutriscore'] -= grille_row['points']
                                    break
                    else : 
                        if value <= max_value:
                            data.at[index, 'nutriscore'] -= points
                        else:
                            for grille_index, grille_row in nutrient_grille.iterrows():
                                if value <= grille_row[nutrient]:
                                    data.at[index, 'nutriscore'] -= grille_row['points']
                                    break 
                                elif pd.isna(grille_row[nutrient]):
                                    data.at[index, 'nutriscore'] -= grille_row['points']
                                    break
        return data
    
    def plot_nutriscore(self):
            # Tracer l'histogramme des valeurs de Nutri-Score
        plt.figure(figsize=(10, 6))
        plt.hist(self.nutriscore['nutriscore'].dropna(), bins=15, edgecolor='k', alpha=0.7)
        plt.title('Répartition des valeurs de Nutri-Score')
        plt.xlabel('Nutri-Score')
        plt.ylabel('Fréquence')
        plt.grid(True)
        plt.show()


    def get_data(path, configs):
        nutrition_table = preprocessing(path, configs).formatdata
        nutrition_table_normal = preprocessing(path, configs).normaldata
        return nutrition_table, nutrition_table_normal

def main():
    path = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/data_base/RAW_recipes.csv'
    path_grille = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/nutrient_table.csv'
    configs = {
    'nutritioncolname':['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
    'grillecolname':['dv_calories_%', 'dv_sat_fat_%', "dv_sugar_%", 'dv_sodium_%', 'dv_protein_%'],
    'dv_calories' : 2000
    }

    nutrition_table = preprocessing(path, configs).formatdata
    nutrition_table_normal = preprocessing(path, configs).normaldata
    nutri_score_instance = NutriScore(nutrition_table_normal, path_grille, configs)
    nutrition_table_nutriscore = nutri_score_instance.nutriscore
    #nutrition_table_nutriscore.plot_nutriscore()
    #print(nutrition_table.head())
    #print(nutrition_table_normal.head())
    print(nutrition_table_nutriscore.head(30))

    return nutrition_table, nutrition_table_normal, nutrition_table_nutriscore
 
if __name__ == '__main__':
    main()