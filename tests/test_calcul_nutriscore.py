import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from preprocess import Preprocessing
from calcul_nutriscore import NutriScore, plot

# Fixture to create a Preprocessing instance
@pytest.fixture
def preprocessing_instance():
    path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/RAW_recipes.csv'
    configs = {
        'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
        'dv_calories': 2000
    }
    return Preprocessing(path, configs)

# Fixture to create a NutriScore instance
@pytest.fixture
def nutriscore_instance(preprocessing_instance):
    path_grille = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/nutrient_table.csv'
    configs = {
        'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
        'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
        'dv_calories': 2000
    }
    nutrition_table_normal = preprocessing_instance.normaldata
    return NutriScore(nutrition_table_normal, path_grille, configs)

#Test return type of get_data method
def test_calcul_nutriscore(nutriscore_instance):
    # Test the calcul_nutriscore method
    result = nutriscore_instance.calcul_nutriscore()
    assert isinstance(result, pd.DataFrame)
    assert 'nutriscore' in result.columns

#Test value of nutriscore_label attribute
def test_set_scorelabel(nutriscore_instance):
    # Test the set_scorelabel method
    result = nutriscore_instance.set_scorelabel()
    assert isinstance(result, np.ndarray)
    assert set(result).issubset({'A', 'B', 'C', 'D', 'E'})

#Test file creation 
def test_plot_distribution():
    # Test the plot_distribution method
    data = np.random.randn(100)
    plot_instance = plot(data, title='Test Plot', xlabel='X-axis', ylabel='Y-axis', output_path='test_plot.png')
    plot_instance.plot_distribution()  # Assurez-vous que le nom de la méthode est correct
    # Check if the file was created
    assert Path('test_plot.png').is_file()

def test_plot_distribution_label():
    # Test the plot_distribution_label method
    labels = np.random.choice(['A', 'B', 'C', 'D', 'E'], 100)
    plot_instance = plot(labels, title='Test Plot', xlabel='X-axis', ylabel='Y-axis', output_path='test_plot_label.png')
    plot_instance.plot_distribution_label(labels=['A', 'B', 'C', 'D', 'E'])
    # Check if the file was created
    assert Path('test_plot_label.png').is_file()