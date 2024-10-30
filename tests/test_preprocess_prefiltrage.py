import sys
import os
import pytest
import pandas as pd

# Add the directory containing preprocess.py to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from preprocess import Preprocessing

def test_prefiltrage():
    path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/RAW_recipes.csv'
    configs = {
        'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
        'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
        'dv_calories': 2000
    }

    # Create an instance of the Preprocessing class
    preprocessing_instance = Preprocessing(path, configs)
    
    # Get the prefiltered data
    prefiltered_data = preprocessing_instance.prefiltredata
    
    # Check that the prefiltered DataFrame is not empty
    assert not prefiltered_data.empty, "The prefiltered DataFrame is empty"
    
    # Check that each column contain values below the threshold defined 
    assert (prefiltered_data['dv_calories_%'] <= 5000).all(), "There are values > 5000 in 'dv_calories_%'"
    assert (prefiltered_data['dv_total_fat_%'] <= 5000).all(), "There are values > 5000 in 'dv_total_fat_%'"
    assert (prefiltered_data['dv_sugar_%'] <= 50000).all(), "There are values > 50000 in 'dv_sugar_%'"
    assert (prefiltered_data['dv_sodium_%'] <= 5000).all(), "There are values > 5000 in 'dv_sodium_%'"
    assert (prefiltered_data['dv_protein_%'] <= 2000).all(), "There are values > 2000 in 'dv_protein_%'"
    assert (prefiltered_data['dv_sat_fat_%'] <= 2000).all(), "There are values > 2000 in 'dv_sat_fat_%'"
    assert (prefiltered_data['dv_carbs_%'] <= 5000).all(), "There are values > 5000 in 'dv_carbs_%'"

if __name__ == '__main__':
    pytest.main()