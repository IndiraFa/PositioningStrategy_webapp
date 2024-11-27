import sys
import os
import pytest
import importlib.util
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

# Add the source path to import necessary modules
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
)

# Dynamically import the file 3_Nutritional_data_quality.py
spec = importlib.util.spec_from_file_location(
    "module_3_Nutritional_data_quality",  
    os.path.join(os.path.dirname(__file__),
                  '../src/pages/3_Nutritional_data_quality.py')
)
module_3_Nutritional_data_quality = importlib.util.module_from_spec(spec)
sys.modules["module_3_Nutritional_data_quality"] = \
    module_3_Nutritional_data_quality
spec.loader.exec_module(module_3_Nutritional_data_quality)

# Define the mocks
@pytest.fixture
def mock_fetch_data():
    """
    Fixture to mock data retrieval from the database
    """

    with patch('pandas.read_sql_query') as mock:  
        # Mock test data
        mock.return_value = pd.DataFrame({
            'id': [1, 2],
            'calories': [200, 250],
            'total_fat_%': [10, 15],
            'sugar_%': [5, 8],
            'sodium_%': [1, 2],
            'protein_%': [20, 25],
            'sat_fat_%': [4, 5],
            'carbs_%': [60, 55]
        })
        yield mock

# Example test to verify the functionality of the Streamlit page
def test_page_load(mock_fetch_data):
    """Test to verify that the page loads correctly"""
    # Test if the module 3_Nutritional_data_quality loads without error
    assert module_3_Nutritional_data_quality is not None

def test_linear_regression_results(mock_fetch_data):
    """Test to verify the calculation of linear regression results"""
    # Mock data for linear regression
    mock_fetch_data.return_value = pd.DataFrame({
        'total_fat_%': [10, 20, 15, 25, 30, 35],
        'protein_%': [30, 40, 35, 45, 50, 55],
        'carbs_%': [50, 60, 55, 65, 70, 75],
        'calories': [200, 250, 225, 275, 300, 350]
    })

    # Initialize the LinearRegressionNutrition class
    lr_nutrition = module_3_Nutritional_data_quality.LinearRegressionNutrition(
        mock_fetch_data.return_value,
        target='calories',
        features=['total_fat_%', 'protein_%', 'carbs_%']
    )
    
    # Perform linear regression
    mse, r2, intercept, coefficients, y_test, y_pred = lr_nutrition\
        .linear_regression()

    # Check that the regression results are correct
    assert isinstance(mse, float)
    assert isinstance(r2, float)
    assert isinstance(intercept, float)

    # Check that the coefficient indices match the features
    assert set(coefficients.index) == {'total_fat_%', 'protein_%', 'carbs_%'}



def test_confidence_intervals(mock_fetch_data):
    """Test to verify the confidence intervals"""
    mock_fetch_data.return_value = pd.DataFrame({
        'total_fat_%': [10, 20],
        'protein_%': [30, 40],
        'carbs_%': [50, 60],
        'calories': [200, 250]
    })
    
    # Mock the bootstrap method for confidence intervals
    lr_nutrition = module_3_Nutritional_data_quality.LinearRegressionNutrition(
        mock_fetch_data.return_value, 
        target='calories',
        features=['total_fat_%', 'protein_%', 'carbs_%']
    )

    conf_level = 0.9  # Example confidence level
    confidence_intervals = lr_nutrition.bootstrap_confidence_interval(
        num_bootstrap_samples=500, 
        confidence_level=conf_level
    )

    # Check that the intervals are calculated correctly
    assert isinstance(confidence_intervals, dict)
    # Check that each feature has a confidence interval in the form of a tuple
    for feature in ['total_fat_%', 'protein_%', 'carbs_%']:
        assert feature in confidence_intervals
        lower, upper = confidence_intervals[feature]
        assert isinstance(lower, (float, np.float64))
        assert isinstance(upper, (float, np.float64))

