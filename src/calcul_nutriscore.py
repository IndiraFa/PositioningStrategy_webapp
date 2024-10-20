import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

from preprocess import Preprocessing, Datatools

class NutriScore:
    def __init__(self, data, grille, configs):
        self.data = data
        self.grille = pd.read_csv(grille, sep=',')
        self.configs = configs
        self.nutriscore = self.calcul_nutriscore()
        self.nutriscore_label = self.set_scorelabel()

    def calcul_nutriscore(self):
        data = self.data.copy()
        data['nutriscore'] = 14.0  # Initialize nutriscore with a base value of 14.0

        grillecolname = self.configs['grillecolname']

        for nutrient in grillecolname:
            if nutrient in self.grille.columns:
                nutrient_grille = self.grille
                nutrient_values = data[nutrient].values

                if nutrient == "dv_protein_%":
                    # Vectorized operation for "dv_protein_%"
                    for i, grille_row in nutrient_grille.iterrows():
                        if i == 0:
                            prev_value = -np.inf  # Use -infinity as the lower bound for the first row
                        else:
                            prev_value = nutrient_grille.iloc[i-1][nutrient]
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
                            prev_value = -np.inf  # Use -infinity as the lower bound for the first row
                        else:
                            prev_value = nutrient_grille.iloc[i-1][nutrient]
                        if np.isnan(grille_row[nutrient]):
                            mask = (nutrient_values > prev_value)
                            data.loc[mask, 'nutriscore'] -= grille_row['points']
                            break
                        mask = (nutrient_values > prev_value) & (nutrient_values <= grille_row[nutrient])
                        data.loc[mask, 'nutriscore'] -= grille_row['points']

        return data
    
    def set_scorelabel(self):
        # Set the NutriScore label based on the calculated nutriscore
        score = self.nutriscore
        label = np.empty(score.shape[0], dtype=str)
        # Assign labels based on the score ranges
        label[np.where(score >= 12)] = 'A'
        label[np.where((score >= 9) & (score < 12))] = 'B'
        label[np.where((score >= 6) & (score < 9))] = 'C'
        label[np.where((score >= 3) & (score < 6))] = 'D'
        label[np.where(score < 3)] = 'E'
        return label

    @staticmethod
    def get_data(path, configs):
        # Get the formatted and normalized nutrition data
        nutrition_table = Preprocessing(path, configs).formatdata
        nutrition_table_normal = Preprocessing(path, configs).normaldata
        return nutrition_table, nutrition_table_normal

class plot:
    def __init__(self, data, title=None, xlabel=None, ylabel=None, output_path=None):
        # Initialize the plot class with data and plot parameters
        self.data = data
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.output_path = output_path
    
    def plot_distribution(self):
        # Plot the distribution of the data
        fig, ax = plt.subplots()
        ax.hist(self.data)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        plt.savefig(self.output_path)
    
    def plot_distribution_label(self, labels):
        # Plot the distribution of the NutriScore labels
        fig, ax = plt.subplots()
        sns.countplot(self.data, order=labels)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        plt.savefig(self.output_path)

def main():
    # Define the paths to the data files
    path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/RAW_recipes.csv'
    path_grille = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/nutrient_table.csv'
    
    # Define the configuration for the nutrition data
    configs = {
        'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
        'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
        'dv_calories': 2000
    }

    # Get the formatted and normalized nutrition data
    nutrition_table = Preprocessing(path, configs).formatdata
    nutrition_table_normal = Preprocessing(path, configs).normaldata
    
    # Create an instance of the NutriScore class and calculate the NutriScore
    nutri_score_instance = NutriScore(nutrition_table_normal, path_grille, configs)
    nutrition_table_nutriscore = nutri_score_instance.nutriscore
    print(nutrition_table_nutriscore)
    print(nutri_score_instance.nutriscore_label)

    # Save the NutriScore data to a CSV file (commented out)
    # output_path = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/nutrition_table_nutriscore.csv'
    # nutrition_table_nutriscore.to_csv(output_path, index=False, header=True, sep=',')

    # Plot the distribution of the NutriScore and NutriScore labels
    plot(nutrition_table_nutriscore['nutriscore'], title='Nutriscore distribution', xlabel='Nutriscore', ylabel='Number of recipes', output_path='nutriscore_distribution.png').plot_distribution()
    plot(nutri_score_instance.nutriscore_label, title='Nutriscore label distribution', xlabel='Nutriscore label', ylabel='Number of recipes', output_path='nutriscore_label_distribution.png').plot_distribution_label(labels=['A', 'B', 'C', 'D', 'E'])
    
    return nutrition_table_nutriscore

if __name__ == '__main__':
    main()