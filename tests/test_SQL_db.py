import pytest
import sqlite3
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from preprocess import Preprocessing
from calcul_nutriscore import NutriScore
from calcul_nutriscore_nooutliers import calcul_nutriscore_no_outliers


@pytest.fixture
def setup_preprocessor():
    # Connexion à la base de données SQLite dans le répertoire src
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/nutrition_data.db'))
    conn = sqlite3.connect(db_path)
    
    # Lecture des données existantes depuis la base de données
    rawdata = pd.read_sql_query("SELECT * FROM raw_recipes", conn)
    normaldata = pd.read_sql_query("SELECT * FROM nutrition_withOutliers", conn)
    denormalizedata = pd.read_sql_query("SELECT * FROM nutrition_noOutliers", conn)
    denormalized_outliers = pd.read_sql_query("SELECT * FROM outliers", conn)
    NS_withOutliers = pd.read_sql_query("SELECT * FROM NS_withOutliers", conn)
    NS_noOutliers = pd.read_sql_query("SELECT * FROM NS_noOutliers", conn)

    # Fermeture de la connexion à la base de données
    conn.close()
    
    # Création d'une instance de Preprocessing avec les données existantes
    preprocessor = Preprocessing(normaldata, configs={})
    
    # Initialisation des attributs pour simuler l'environnement de la base de données
    preprocessor.rawdata = rawdata
    preprocessor.normaldata = normaldata
    preprocessor.denormalizedata = denormalizedata
    preprocessor.denormalized_outliers = denormalized_outliers
    preprocessor.NS_withOutliers = NS_withOutliers
    preprocessor.NS_noOutliers = NS_noOutliers
    
    return preprocessor

def test_SQL_database(setup_preprocessor):
    preprocessor = setup_preprocessor
    
    # Appel de la méthode SQL_database
    preprocessor.SQL_database()
    
    # Connexion à la base de données SQLite pour vérifier l'état des tables
    conn = sqlite3.connect('nutrition_data.db')
    
    # Vérification de l'existence des tables et de la conformité des données
    for table_name in ['nutrition_withOutliers', 'nutrition_noOutliers', 'outliers']:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        pd.testing.assert_frame_equal(df, getattr(preprocessor, table_name))
    
    # Fermeture de la connexion à la base de données
    conn.close()
