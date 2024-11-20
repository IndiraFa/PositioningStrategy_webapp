import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import psycopg2
from sqlalchemy import create_engine
import toml

from preprocess import Preprocessing, Datatools

# Lire les informations de connexion depuis secrets.toml
secrets = toml.load('secrets.toml')
postgresql_config = secrets['connections']['postgresql']

# Informations de connexion à la base de données PostgreSQL
db_host = postgresql_config['host']
db_name = postgresql_config['database']
db_user = postgresql_config['username']
db_password = postgresql_config['password']
db_port = postgresql_config['port']

class NutriScore:
    def __init__(self, data, grille, configs):
        self.data = data
        self.grille = grille
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
        score['label'] = ''
        if 'nutriscore' not in score.columns:
            raise ValueError('The nutriscore column is not in the dataframe')
        else:
            score['label'] = ''
            score.loc[score['nutriscore'] >= 12, 'label'] = 'A'
            score.loc[(score['nutriscore'] >= 9) & (score['nutriscore'] < 12), 'label'] = 'B'
            score.loc[(score['nutriscore'] >= 6) & (score['nutriscore'] < 9), 'label'] = 'C'
            score.loc[(score['nutriscore'] >= 3) & (score['nutriscore'] < 6), 'label'] = 'D'
            score.loc[score['nutriscore'] < 3, 'label'] = 'E'
            return score

    @staticmethod
    def get_data(path, configs):
        # Get the formatted and normalized nutrition data
        nutrition_table = Preprocessing(path, configs).formatdata
        nutrition_table_normal = Preprocessing(path, configs).normaldata
        return nutrition_table, nutrition_table_normal

    def stock_database(self):
        # Save the NutriScore + Labels data to PostgreSQL
        # Créer une connexion à la base de données PostgreSQL
        engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
        conn = engine.connect()

        self.nutriscore_label.to_sql('NS_withOutliers', conn, if_exists='replace', index=False)
        print(f'NutriScore data saved to the database : {len(self.nutriscore_label)} rows')

        conn.close()

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
        sns.countplot(x=self.data, order=labels)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        plt.savefig(self.output_path)

def connect_to_database():
    """
    Crée une connexion à la base de données PostgreSQL.
    Retourne l'objet connexion ou lève une exception en cas d'erreur.
    """
    try:
        engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
        conn = engine.connect()
        print("Connexion réussie à la base de données.")
        return conn
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
        raise

def load_data_from_database(conn):
    """
    Charge les données nécessaires depuis la base de données.
    Retourne les DataFrames pour les recettes, la grille et les tables nutritionnelles.
    """
    try:
        queries = {
            "raw_recipes": "SELECT * FROM raw_recipes",
            "grille": "SELECT * FROM nutrient_table",
            'formatted_data': 'SELECT * FROM "Formatted_data"',
            "nutrition_with_outliers": 'SELECT * FROM "nutrition_withOutliers"'
        }

        print("Chargement des données...")
        raw_recipes = pd.read_sql_query(queries["raw_recipes"], conn)
        grille = pd.read_sql_query(queries["grille"], conn)
        formatted_data = pd.read_sql_query(queries["formatted_data"], conn)
        nutrition_with_outliers = pd.read_sql_query(queries["nutrition_with_outliers"], conn)
        print("Données chargées avec succès.")
        return raw_recipes, grille, formatted_data, nutrition_with_outliers
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")
        raise

def save_plots(nutriscore_data, nutriscore_labels):
    """
    Génère et sauvegarde les graphiques de distribution des NutriScores.
    """
    print("Génération des graphiques...")
    plot(
        nutriscore_data['nutriscore'], 
        title='Nutriscore distribution', 
        xlabel='Nutriscore', 
        ylabel='Number of recipes', 
        output_path='nutriscore_distribution.png'
    ).plot_distribution()

    plot(
        nutriscore_labels['label'], 
        title='Nutriscore label distribution', 
        xlabel='Nutriscore label', 
        ylabel='Number of recipes', 
        output_path='nutriscore_label_distribution.png'
    ).plot_distribution_label(labels=['A', 'B', 'C', 'D', 'E'])
    print("Graphiques sauvegardés.")

def main():
    try:
        # Connexion à la base de données
        conn = connect_to_database()

        # Chargement des données
        raw_recipes, grille, formatted_data, nutrition_with_outliers = load_data_from_database(conn)

        # Fermeture de la connexion
        conn.close()

        # Configuration des colonnes
        configs = {
            'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
            'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
            'dv_calories': 2000
        }

        # Calcul du NutriScore
        print("Calcul des NutriScores...")
        nutri_score_instance = NutriScore(nutrition_with_outliers, grille, configs)
        nutrition_table_nutriscore = nutri_score_instance.nutriscore
        print(nutrition_table_nutriscore.head())
        print(nutri_score_instance.nutriscore_label.head())

        # Sauvegarde dans la base de données
        nutri_score_instance.stock_database()

        # Génération des graphiques
        save_plots(nutrition_table_nutriscore, nutri_score_instance.nutriscore_label)

        print("Script exécuté avec succès.")
        return nutrition_table_nutriscore
    except Exception as e:
        print(f"Erreur lors de l'exécution du script : {e}")
        raise

if __name__ == '__main__':
    main()
