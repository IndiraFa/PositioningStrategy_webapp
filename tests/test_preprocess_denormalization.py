import sys
import os
import pytest
import pandas as pd

# Add the directory containing preprocess.py to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from preprocess import Preprocessing

def test_denormalisation():
    path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/RAW_recipes.csv'
    configs = {
        'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
        'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
        'dv_calories': 2000
    }

    # Create an instance of the Preprocessing class
    preprocessing_instance = Preprocessing(path, configs)
    
    # Get the denormalized data
    finalDF_noOutliers, finalDF_outliers = preprocessing_instance.denormalizedata, preprocessing_instance.denormalized_outliers
    
    # Get the original formatted data
    original_data = preprocessing_instance.normaldata
    
    # Check that the denormalized DataFrame is not empty
    assert not finalDF_noOutliers.empty, "The denormalized DataFrame with no outliers is empty"
    assert not finalDF_outliers.empty, "The denormalized DataFrame with outliers is empty"

    # Verify that for each id, the values in the denormalized DataFrame match the original values
    for col in configs['grillecolname']:
        print(f"Checking column: {col}")
        merged_data = pd.merge(original_data[['id', col]], finalDF_noOutliers[['id', col]], on='id', suffixes=('_original', '_denormalized'))
        mismatches = merged_data[~merged_data.apply(lambda row: pytest.approx(row[f'{col}_original'], abs=1e-1) == row[f'{col}_denormalized'], axis=1)]
        if not mismatches.empty:
            for _, row in mismatches.iterrows():
                print(f"Mismatch in column {col} for id {row['id']}: original {row[f'{col}_original']}, denormalized {row[f'{col}_denormalized']}")
        assert mismatches.empty, f"Mismatches found in column {col}"

if __name__ == '__main__':
    pytest.main()