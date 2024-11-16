import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
from calcul_nutriscore import NutriScore
from preprocess import Preprocessing
import psycopg2
from sqlalchemy import create_engine
import toml

# Lire les informations de connexion depuis secrets.toml
secrets = toml.load('secrets.toml')
postgresql_config = secrets['connections']['postgresql']

def calcul_nutriscore_no_outliers(data, grille, configs):
    # Créer une instance de la classe Preprocessing
    preprocessor = Preprocessing(data, configs)
    
    # Appeler les méthodes sur l'instance de Preprocessing
    gaussian_norm_data_no_outliers, gaussian_norm_outliers = preprocessor.gaussian_normalisation()
    final_data_no_outliers, final_outliers = preprocessor.Denormalisation(gaussian_norm_data_no_outliers, gaussian_norm_outliers)
    
    # Créer une instance de la classe NutriScore
    nutriscore_calculator = NutriScore(final_data_no_outliers, grille, configs)
    
    # Appeler la méthode calcul_nutriscore sur l'instance de NutriScoreCalculator
    nutriscore_no_outliers_nolabel = nutriscore_calculator.calcul_nutriscore()
    nutriscore_no_outliers = nutriscore_calculator.set_scorelabel()

    return nutriscore_no_outliers

# Informations de connexion à la base de données PostgreSQL
db_host = postgresql_config['host']
db_name = postgresql_config['database']
db_user = postgresql_config['username']
db_password = postgresql_config['password']
db_port = postgresql_config['port']

# Créer une connexion à la base de données PostgreSQL
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
conn = engine.connect()

# Read raw_recipes data from the database
query = "SELECT * FROM raw_recipes"
query_grille = "SELECT * FROM nutrient_table"
df = pd.read_sql_query(query, conn)
df_grille = pd.read_sql_query(query_grille, conn)

# Close the database connection
conn.close()

configs = {
    'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
    'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
    'dv_calories': 2000
}

df_nutriscore_no_outliers = calcul_nutriscore_no_outliers(df, df_grille, configs)
print(df_nutriscore_no_outliers)
print(df_nutriscore_no_outliers.shape)
df_nutriscore_no_outliers.info()
print(df_nutriscore_no_outliers.describe())

# Save the NutriScore + Labels data to the database
nutriscore_calculator = NutriScore(df_nutriscore_no_outliers, df_grille, configs)
nutriscore_calculator.stock_database()
