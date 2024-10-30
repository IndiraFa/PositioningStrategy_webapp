import pytest
import pandas as pd
from preprocess import Preprocessing
from outliers_remove import plot_distribution, display_table

# Fixture to create a Preprocessing instance
@pytest.fixture
def preprocessing_instance():
    path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/RAW_recipes.csv'
    configs = {
        'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
        'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
        'dv_calories': 2000
    }
    return Preprocessing(path, configs)

def test_plot_distribution(preprocessing_instance):
    # Test the plot_distribution function
    data = preprocessing_instance.gaussiandata
    plot_distribution(data, plot_type='dot', title_prefix="Test Distribution")
    # Since plot_distribution does not return anything, we cannot assert its output directly.
    # Instead, we ensure that no exceptions are raised during its execution.

def test_display_table(preprocessing_instance):
    # Test the display_table function
    data = preprocessing_instance.gaussiandata
    display_table(data, "Test Table")
    # Since display_table prints the output, we cannot assert its output directly.
    # Instead, we ensure that no exceptions are raised during its execution.

def test_gaussian_normalisation(preprocessing_instance):
    # Test the gaussian_normalisation method
    result = preprocessing_instance.gaussian_normalisation()
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    # Add more assertions based on expected behavior

def test_prefiltrage(preprocessing_instance):
    # Test the prefiltrage method
    result = preprocessing_instance.prefiltrage()
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    # Add more assertions based on expected behavior
