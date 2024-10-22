import pytest
import pandas as pd
from preprocess import Preprocessing, Datatools

# Fixture to create a Preprocessing instance
@pytest.fixture
def preprocessing_instance():
    path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/RAW_recipes.csv'
    configs = {
        'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
        'dv_calories': 2000
    }
    return Preprocessing(path, configs)


def test_get_raw_nutrition(preprocessing_instance):
    # Test the get_raw_nutrition method
    result = preprocessing_instance.get_raw_nutrition()
    assert isinstance(result, pd.DataFrame)
    assert 'id' in result.columns
    assert 'nutrition' in result.columns

def test_get_formatted_nutrition(preprocessing_instance):
    # Test the get_formatted_nutrition method
    result = preprocessing_instance.get_formatted_nutrition()
    assert isinstance(result, pd.DataFrame)
    assert 'id' in result.columns
    for col in preprocessing_instance.configs['nutritioncolname']:
        assert col in result.columns

def test_set_dv_normalisation(preprocessing_instance):
    # Test the set_dv_normalisation method
    result = preprocessing_instance.set_dv_normalisation()
    assert isinstance(result, pd.DataFrame)
    assert 'dv_calories_%' in result.columns
    for col in preprocessing_instance.configs['nutritioncolname'][1:]:
        assert f'dv_{col}' in result.columns

def test_prefiltrage(preprocessing_instance):
    # Test the prefiltrage method
    result = preprocessing_instance.prefiltrage()
    assert isinstance(result, pd.DataFrame)
    assert not result.empty

def test_gaussian_normalisation(preprocessing_instance):
    # Test the gaussian_normalisation method
    result = preprocessing_instance.gaussian_normalisation()
    assert isinstance(result, pd.DataFrame)
    assert not result.empty

