import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

from preprocess import Preprocessing, Datatools


class NutriScore:
    """
    This class is used to calculate the nutriscore of a dataset
    based on the nutriscore grid provided in the file grille.
    The nutriscore is calculated based on the following nutrients:
    - calories
    - sugar_%
    - sodium_%
    - protein_%
    - sat_fat_%
    with a reference daily value of 2000 calories.

    attributes:
    - data: the dataset to calculate the nutriscore
    - grille: the nutriscore grid
    - configs: the configuration of the nutriscore calculation
    - nutriscore: the calculated nutriscore
    - nutriscore_label: the nutriscore label
  
    methods:
    - calcul_nutriscore: calculate the nutriscore based on the grid
    - set_scorelabel: set the nutriscore label (A to E)based on the 
    nutriscore value
    """
    def __init__(self, data, grille, configs):
        self.data = data
        self.grille = pd.read_csv(grille, sep=',')
        self.configs = configs
        self.nutriscore = self.calcul_nutriscore()
        self.nutriscore_label = self.set_scorelabel()

    def calcul_nutriscore(self):
        """
        calculate the nutriscore based on the grid

        parameters:
        - data: the dataset to calculate the nutriscore
        - grille: the nutriscore grid
        - configs: the configuration of the nutriscore calculation

        return:
        - data: the dataset with the nutriscore column

        """
        data = self.data.copy()
        data['nutriscore'] = 14.0

        grillecolname = self.configs['grillecolname']

        for nutrient in grillecolname:
            if nutrient in self.grille.columns:
                nutrient_grille = self.grille
                nutrient_values = data[nutrient].values

                if nutrient == "dv_protein_%":
                    # Vectorized operation for "dv_protein_%"
                    for i, grille_row in nutrient_grille.iterrows():
                        if i == 0:
                            # if it is the first row, use -inf as lower value
                            prev_value = -np.inf
                        else:
                            prev_value = nutrient_grille[nutrient].iloc[i-1]
                        if np.isnan(grille_row[nutrient]):
                            mask = (-nutrient_values > prev_value)
                            data.loc[mask, 'nutriscore'] -= grille_row['points']
                            break
                        mask = (-nutrient_values > prev_value) & \
                               (-nutrient_values <= grille_row[nutrient])
                        data.loc[mask, 'nutriscore'] -= grille_row['points']

                else:
                    # Vectorized operation for other nutrients
                    for i, grille_row in nutrient_grille.iterrows():
                        if i == 0:
                            # if it is the first row, use -inf as lower value
                            prev_value = -np.inf
                        else:
                            prev_value = nutrient_grille[nutrient].iloc[i-1]
                        if np.isnan(grille_row[nutrient]):
                            mask = (nutrient_values > prev_value)
                            data.loc[mask, 'nutriscore'] -= grille_row['points']
                            break
                        mask = (nutrient_values > prev_value) & \
                            (nutrient_values <= grille_row[nutrient])
                        data.loc[mask, 'nutriscore'] -= grille_row['points']

        return data

    def set_scorelabel(self):
        """
        calculate the nutriscore label (A to E) based on the nutriscore value

        Parameters:
        - data: the dataset with the nutriscore column

        Returns:
        - data: the dataset with the nutriscore label column

        """
        score = self.nutriscore
        score['label'] = ''
        if 'nutriscore' not in score.columns:
            raise ValueError('The nutriscore column is not in the dataframe')
        else:
            score['label'] = ''
            score.loc[score['nutriscore'] >= 12, 'label'] = 'A'
            score.loc[
                (score['nutriscore'] >= 9) & (score['nutriscore'] < 12),
                'label'
            ] = 'B'
            score.loc[
                (score['nutriscore'] >= 6) & (score['nutriscore'] < 9),
                'label'
            ] = 'C'
            score.loc[
                (score['nutriscore'] >= 3) & (score['nutriscore'] < 6),
                'label'
            ] = 'D'
            score.loc[
                score['nutriscore'] < 3,
                'label'
            ] = 'E'
            return score

    def get_data(path, configs):
        nutrition_table = Preprocessing(path, configs).formatdata
        nutrition_table_normal = Preprocessing(path, configs).normaldata
        return nutrition_table, nutrition_table_normal


class plot:
    """
    This class is used to plot the distribution of a dataset

    attributes:
    - data: the dataset to plot
    - title: the title of the plot
    - xlabel: the label of the x axis
    - ylabel: the label of the y axis
    - output_path: the path to save the plot

    methods:
    - plot_distribution: plot the distribution of the dataset
    - plot_distribution_label: plot the distribution of the dataset with labels
    """
    def __init__(
            self,
            data,
            title=None,
            xlabel=None,
            ylabel=None,
            output_path=None
    ):
        self.data = data
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.output_path = output_path

    def plot_distrubution(self):
        fig, ax = plt.subplots()
        ax.hist(self.data)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        plt.savefig(self.output_path)

    def plot_distribution_label(self, labels):
        fig, ax = plt.subplots()
        sns.countplot(self.data, order=labels)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        plt.savefig(self.output_path)


def main():
    path = Path('src/datasets/RAW_recipes.csv')
    path_grille = Path('src/nutrient_table.csv')

    configs = {
        'nutritioncolname': [
            'calories',
            'total_fat_%',
            'sugar_%',
            'sodium_%',
            'protein_%',
            'sat_fat_%',
            'carbs_%'
        ],
        'grillecolname': [
            'dv_calories_%',
            'dv_sat_fat_%',
            'dv_sugar_%',
            'dv_sodium_%',
            'dv_protein_%'
        ],
        'dv_calories': 2000
    }

    nutrition_table = Preprocessing(path, configs).formatdata
    nutrition_table_normal = Preprocessing(path, configs).normaldata
    nutri_score_instance = NutriScore(
        nutrition_table_normal,
        path_grille,
        configs
    )
    nutrition_table_nutriscore = nutri_score_instance.nutriscore
    print(nutrition_table_nutriscore)
    print(nutri_score_instance.nutriscore_label)
    print(nutrition_table_nutriscore.describe())  # test for comparison

    output_path = './datasets/nutrition_table_nutriscore.csv'
    nutrition_table_withlabels = nutrition_table_nutriscore.set_scorelabel()
    nutrition_table_withlabels.to_csv(
        output_path,
        index=False,
        header=True,
        sep=','
    )

    return nutrition_table_nutriscore


if __name__ == '__main__':
    main()
