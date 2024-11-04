import sys
import os
import pytest
import pandas as pd
from tabulate import tabulate

# Add the directory containing preprocess.py to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from preprocess import Preprocessing

def test_gaussian_normalisation():
    path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/RAW_recipes.csv'
    configs = {
        'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
        'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
        'dv_calories': 2000
    }

    # Create an instance of the Preprocessing class
    preprocessing_instance = Preprocessing(path, configs)
    
    # Get the Gaussian normalized data
    DF_noOutliers, DF_outliers = preprocessing_instance.gaussian_normalisation()
    
    # Check that the normalization (with outliers data) was applied correctly
    for col in configs['grillecolname']:
        table_gauss = preprocessing_instance.prefiltredata.copy()
        mu = table_gauss[col].mean()
        sigma = table_gauss[col].std()
        table_gauss[col] = (table_gauss[col] - mu) / sigma
        assert table_gauss[col].mean() == pytest.approx(0, abs=1e-1), f"The mean of {col} is not approximately 0"
        assert table_gauss[col].std() == pytest.approx(1, abs=1e-1), f"The standard deviation of {col} is not approximately 1"

    # Check that the DataFrame is not empty
    assert not DF_noOutliers.empty, "The DataFrame with no outliers is empty"
    assert not DF_outliers.empty, "The DataFrame with outliers is empty"

    #Check that the outliers > 3 have been removed
    assert (DF_noOutliers['dv_calories_%'] > 3).sum() == 0, "Normalized Outliers with dv_calories_% > 3 found and should have been removed"
    assert (DF_noOutliers['dv_sat_fat_%'] > 3).sum() == 0, "Normalized Outliers with dv_sat_fat_% > 3 found and should have been removed"
    assert (DF_noOutliers['dv_sugar_%'] > 3).sum() == 0, "Normalized Outliers with dv_sugar_% > 3 found and should have been removed"
    assert (DF_noOutliers['dv_sodium_%'] > 3).sum() == 0, "Normalized Outliers with dv_sodium_% > 3 found and should have been removed"
    assert (DF_noOutliers['dv_protein_%'] > 3).sum() == 0, "Normalized Outliers with dv_protein_% > 3 found and should have been removed"
    
    # Check the size of the data frames
    initial_outliers_count = len(preprocessing_instance.outliers)
    print(f"Size of Total_outliers before processing: {initial_outliers_count}") 
    assert len(DF_noOutliers) > 0, "The DataFrame with no outliers should have rows"
    assert len(DF_outliers) > 0, "The DataFrame with outliers should have rows"
    print(f"Size of DF_noOutliers after processing: {len(DF_noOutliers)}") 
    print(f"Size of DF_outliers after processing: {len(DF_outliers)}") 

if __name__ == '__main__':
    pytest.main()