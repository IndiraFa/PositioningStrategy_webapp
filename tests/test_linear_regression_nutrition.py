import sys
import os
import pytest
import pandas as pd
import pandas.testing as pdt
import numpy
import matplotlib.pyplot as plt
from unittest.mock import patch, mock_open
# to be able to import the module from the src folder
sys.path.insert(0, os.path.abspath(os.path.join
                                   (os.path.dirname(__file__), '../src')
                                   ))
from linear_regression_nutrition import (
    calories_per_gram,
    DataPreprocessing,
    LinearRegressionNutrition, 
    main
)


# Tests for the DataPreprocessing class

@pytest.fixture
def raw_recipes_data():
    """
    Mock data for the raw recipes data

    Args:
    None

    Returns:
    a DataFrame with the following columns:
    - name: the name of the recipe
    - id: the id of the recipe
    - minutes: the time to prepare the recipe
    - contributor_id: the id of the contributor
    - submitted: the date the recipe was submitted
    - tags: the tags of the recipe
    - nutrition: the nutrition of the recipe
    - n_steps: the number of steps in the recipe
    - steps: the steps of the recipe
    - description: the description of the recipe
    - ingredients: the ingredients of the recipe
    - n_ingredients: the number of ingredients in the recipe
    """

    data = pd.DataFrame({
        'name': ['recipe1', 'recipe2', 'recipe3'],
        'id': [100, 200, 300],
        'minutes': [10, 20, 30],
        'contributor_id': [5, 10, 15],
        'submitted': ['2005-09-16', '2006-10-20', '2007-11-24'],
        'tags': ['tag1 tag2', 'tag3-tag4', 'tag5tag6'],
        'nutrition': [
            "[8.2, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]",
            "[3.0, 0.0, 6.0, 0.0, 22.0, 0.0, 0.0]",
            "[40.0, 32.0, 3.0, 6.0, 8.0, 3.4, 0.0]"
        ],
        'n_steps': [5, 10, 15],
        'steps': [
            "['step1', 'step2']",
            "['step2', 'step3', 'step4']",
            "['step5', 'step6']"],
        'description': ['desc, 1', 'desc2', 'desc3'],
        'ingredients': [
            "['ing1, ing2']",
            "['ing3, ing2, ing10']",
            "['ing1, ing2']"
        ],
        'n_ingredients': [2, 4, 6]
    })
    return data


@pytest.fixture
def nutriscore_data():
    """
    Mock data for the nutriscore data

    Args:
    None

    Returns:
    a DataFrame with the following columns:
    - id: the id of the recipe
    - dv_calories_%: the percentage of daily value for calories
    - dv_total_fat_%: the percentage of daily value for total fat
    - dv_sugar_%: the percentage of daily value for sugar
    - dv_sodium_%: the percentage of daily value for sodium
    - dv_protein_%: the percentage of daily value for protein
    - dv_sat_fat_%: the percentage of daily value for saturated fat
    - dv_carbs_%: the percentage of daily value for carbohydrates
    - nutriscore: the nutriscore of the recipe
    - label: the label of the recipe
    """
    data = pd.DataFrame({
        'id': [100, 200],
        'dv_calories_%': [10, 20],
        'dv_total_fat_%': [30, 40],
        'dv_sugar_%': [50, 60],
        'dv_sodium_%': [7, 8],
        'dv_protein_%': [9, 10],
        'dv_sat_fat_%': [11, 12],
        'dv_carbs_%': [130, 140],
        'nutriscore': ['12.0', '9.2'],
        'label': ['A', 'B']
    })
    return data


@pytest.fixture
def mock_data_preprocessing():
    return DataPreprocessing(
        path_recipes_data='dummy_path', path_nutriscore_data='dummy_path'
    )

@patch('linear_regression_nutrition.Preprocessing')
def test_load_and_preprocess_recipes_data_with_data(
    mock_Preprocessing, mock_data_preprocessing
):
    # Mock data
    mock_data = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Recipe1', 'Recipe2', 'Recipe3']
    })
    mock_data_preprocessing.data = mock_data

    # Call the function
    result = mock_data_preprocessing.load_and_preprocess_recipes_data()

    # Assert that the data is returned directly
    assert result.equals(mock_data)
    mock_Preprocessing.assert_not_called()

@patch('linear_regression_nutrition.Preprocessing')
def test_load_and_preprocess_recipes_data_without_data(
    mock_Preprocessing, mock_data_preprocessing
):
    # Mock Preprocessing instance and its method
    mock_preprocessing_instance = mock_Preprocessing.return_value
    mock_preprocessing_instance.get_formatted_nutrition.return_value = \
        pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Recipe1', 'Recipe2', 'Recipe3']
    })

    # Ensure self.data is None
    mock_data_preprocessing.data = None

    # Call the function
    result = mock_data_preprocessing.load_and_preprocess_recipes_data()

    # Assert that Preprocessing is called and the correct data is returned
    mock_Preprocessing.assert_called_once()
    mock_preprocessing_instance.get_formatted_nutrition.assert_called_once()
    assert result.equals(
        mock_preprocessing_instance.get_formatted_nutrition.return_value
    )


def test_merge_data(raw_recipes_data, nutriscore_data):
    mock_recipe_path = 'data/recipe.csv'
    mock_nutriscore_path = 'data/nutriscore.csv'
    data_preprocessing = DataPreprocessing(
        mock_recipe_path,
        mock_nutriscore_path
    )
    result = data_preprocessing.merge_data(raw_recipes_data, nutriscore_data)
    expected_result = pd.DataFrame({
        'name': ['recipe1', 'recipe2'],
        'id': [100, 200],
        'minutes': [10, 20],
        'contributor_id': [5, 10],
        'submitted': ['2005-09-16', '2006-10-20'],
        'tags': ['tag1 tag2', 'tag3-tag4'],
        'nutrition': [
            "[8.2, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]",
            "[3.0, 0.0, 6.0, 0.0, 22.0, 0.0, 0.0]"
        ],
        'n_steps': [5, 10],
        'steps': ["['step1', 'step2']", "['step2', 'step3', 'step4']"],
        'description': ['desc, 1', 'desc2'],
        'ingredients': ["['ing1, ing2']", "['ing3, ing2, ing10']"],
        'n_ingredients': [2, 4],
        'dv_calories_%': [10, 20],
        'dv_total_fat_%': [30, 40],
        'dv_sugar_%': [50, 60],
        'dv_sodium_%': [7, 8],
        'dv_protein_%': [9, 10],
        'dv_sat_fat_%': [11, 12],
        'dv_carbs_%': [130, 140],
        'nutriscore': ['12.0', '9.2'],
        'label': ['A', 'B']
    })
    try:
        pdt.assert_frame_equal(result, expected_result)
    except AssertionError as e:
        raise AssertionError(f"Test failed: {e}")


# Tests for LinearRegressionNutrition class

@pytest.fixture
def nutrition_data():
    """
    Returns a tuple with the following data for the test:

    - data: a DataFrame with the following columns:
        - id: the id of the recipe
        - calories: the calories per portion
        - total_fat_%: the percentage of total fat per portion
        - sugar_%: the percentage of sugar per portion
        - sodium_%: the percentage of sodium per portion
        - protein_%: the percentage of protein per portion
        - sat_fat_%: the percentage of saturated fat per portion
        - carbs_%: the percentage of carbohydrates per portion

    - target: the target variable for the linear regression model
    - features: the features for the linear regression model

    Args:
    None

    Returns:
    a tuple with the data, target, and features
    """
    data = pd.DataFrame({
        'id': [100, 200, 300, 400, 500, 600],
        'calories': [100, 150, 200, 250, 300, 350],
        'total_fat_%': [10, 15, 20, 25, 30, 35],
        'sugar_%': [5, 10, 15, 20, 25, 30],
        'sodium_%': [1, 2, 3, 4, 5, 6],
        'protein_%': [2, 4, 6, 8, 10, 12],
        'sat_fat_%': [1, 1.5, 2, 2.5, 3, 3.5],
        'carbs_%': [50, 55, 60, 65, 70, 75],
    })
    target = 'calories'
    features = ['total_fat_%', 'protein_%', 'carbs_%']
    return data, target, features


def test_linear_regression(nutrition_data):
    """
    Tests the linear_regression function

    Args:
    nutrition_data: a tuple with data for the test

    Returns:
    None
    """
    data, target, features = nutrition_data
    lr_nutrition = LinearRegressionNutrition(data, target, features)
    mse, r2, intercept, coefficients, y_test, y_pred \
        = lr_nutrition.linear_regression()

    # Check the types of the returned values
    assert isinstance(mse, float), "MSE should be a float"
    assert isinstance(r2, float), "R-squared should be a float"

    # R2 should be between 0 and 1
    assert 0 <= r2 <= 1, "R-squared should be between 0 and 1"
    assert isinstance(intercept, float), "Intercept should be a float"
    assert isinstance(coefficients, pd.DataFrame), \
        "Coefficients should be a DataFrame"
    assert isinstance(y_test, pd.Series), "y_test should be a Series"
    assert isinstance(y_pred, numpy.ndarray), \
        "y_pred should be a NumPy array"

    # Check the shape of the coefficients DataFrame
    assert coefficients.shape == (len(features), 1), \
        "Coefficients DataFrame shape is incorrect"

    # Check that the coefficients DataFrame has the correct index
    assert list(coefficients.index) == features, \
        "Coefficients DataFrame index is incorrect"

    # Check that the y_test and y_pred Series have the same length
    assert len(y_test) == len(y_pred), \
        "y_test and y_pred should have the same length"


def test_plot_linear_regression(nutrition_data):
    """
    Tests the plot_linear_regression function

    Args:
    nutrition_data: a tuple with data for the test

    Returns:
    None
    """
    data, target, features = nutrition_data
    lr_nutrition = LinearRegressionNutrition(data, target, features)
    mse, r2, intercept, coefficients, y_test, y_pred \
        = lr_nutrition.linear_regression()

    plt.close('all')

    # Create the plot
    lr_nutrition.plot_linear_regression(y_test, y_pred)

    # Check if the plot was created correctly
    fig = plt.gcf()
    assert len(fig.axes) == 1, " There should be one axis in the plot"
    ax = fig.axes[0]
    assert len(ax.lines) == 1, "There should be one line in the plot"
    assert len(ax.collections) == 1, \
        "There should be one scatter plot in the plot"

    # Check the labels and title
    assert ax.get_xlabel() == 'Actual Calories per Portion', \
        "X-axis label is incorrect"
    assert ax.get_ylabel() == 'Predicted Calories per Portion', \
        "Y-axis label is incorrect"
    assert ax.get_title() == 'Actual vs Predicted Calories per Portion', \
        "Title is incorrect"

    # Check the legend
    legend = ax.get_legend()
    assert legend is not None, "Legend should be present"
    assert len(legend.get_texts()) == 2, "Legend should have two entries"
    assert legend.get_texts()[0].get_text() == 'Predicted vs Actual', \
        "First legend entry is incorrect"
    assert legend.get_texts()[1].get_text() == 'Ideal Fit', \
        "Second legend entry is incorrect"


def test_bootstrap_confidence_interval(nutrition_data):
    """
    Tests the bootstrap_confidence_interval function

    Args:
    nutrition_data: a tuple with data for the test

    Returns:
    None
    """
    data, target, features = nutrition_data
    lr_nutrition = LinearRegressionNutrition(data, target, features)
    intervals = lr_nutrition.bootstrap_confidence_interval(
        num_bootstrap_samples=100,
        confidence_level=0.95
    )

    # Check the type of the returned value
    assert isinstance(intervals, dict), "Intervals should be a dictionary"

    # Check that the dictionary contains the correct keys
    assert set(intervals.keys()) == set(features), \
        "Intervals dictionary keys are incorrect"

    # Check that each value in the dictionary is a tuple of length 2
    for feature in features:
        assert isinstance(intervals[feature], tuple), \
            f"Interval for {feature} should be a tuple"
        assert len(intervals[feature]) == 2, \
            f"Interval for {feature} should have length 2"


# Tests for the function calories_per_gram

@pytest.fixture
def calories_data():
    """
    Returns a tuple with the following data for the test:
    - coefficient_data: a DataFrame with the coefficients of the 
    linear regression model
    - daily_g_protein: daily intake of protein in grams
    - daily_g_total_fat: daily intake of total fat in grams
    - daily_g_carbs: daily intake of carbohydrates in grams
    """
    coefficient_data = pd.DataFrame(
        {'Coefficient': [41, 12, 22]},
        index=['total_fat_%', 'protein_%', 'carbs_%']
    )
    daily_g_protein = 50
    daily_g_total_fat = 70
    daily_g_carbs = 260
    return coefficient_data, daily_g_protein, daily_g_total_fat, daily_g_carbs


def test_calories_per_gram(calories_data):
    """
    Function to test the calories_per_gram function

    Args:
    calories_data: a tuple with data for the test

    Returns:
    None
    """
    coefficient_data, daily_g_protein, daily_g_total_fat, \
        daily_g_carbs = calories_data
    result = calories_per_gram(
        coefficient_data,
        daily_g_protein,
        daily_g_total_fat,
        daily_g_carbs
    )
    expected_result = pd.DataFrame({
        'Calories per gram of Protein': [12*100/50],
        'Calories per gram of Fat': [41*100/70],
        'Calories per gram of Carbohydrates': [22*100/260]
    }, index=['Value'])
    try:
        pdt.assert_frame_equal(result, expected_result)
    except AssertionError as e:
        raise AssertionError(f"Test failed: {e}")


@patch('linear_regression_nutrition.DataPreprocessing')
@patch('linear_regression_nutrition.pd.read_csv')
@patch('linear_regression_nutrition.LinearRegressionNutrition')
@patch('linear_regression_nutrition.calories_per_gram')
def test_main(
    mock_calories_per_gram,
    mock_LinearRegressionNutrition,
    mock_read_csv,
    mock_DataPreprocessing
):
    # Mock data
    mock_raw_data = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Recipe1', 'Recipe2', 'Recipe3']
    })
    mock_nutriscore_data = pd.DataFrame({
        'id': [1, 2, 3],
        'calories': [100, 200, 300],
        'total_fat_%': [10, 20, 30],
        'sugar_%': [5, 10, 15],
        'sodium_%': [1, 2, 3],
        'protein_%': [10, 20, 30],
        'sat_fat_%': [2, 4, 6],
        'carbs_%': [50, 60, 70]
    })
    mock_merged_data = mock_nutriscore_data.copy()
    mock_filtered_data = mock_nutriscore_data.copy()

    # Mock return values
    mock_DataPreprocessing.return_value.load_and_preprocess_recipes_data.return_value = mock_raw_data
    mock_read_csv.return_value = mock_nutriscore_data
    mock_DataPreprocessing.return_value.merge_data.return_value \
        = mock_merged_data
    mock_DataPreprocessing.return_value.filter_columns.return_value \
        = mock_filtered_data

    mock_linear_regression_nutrition = \
        mock_LinearRegressionNutrition.return_value
    mock_linear_regression_nutrition.linear_regression.return_value = (
        0.1, 0.9, 1.0, [0.5, 0.3, 0.2], [100, 200, 300], [110, 210, 310]
    )
    mock_linear_regression_nutrition.bootstrap_confidence_interval.return_value = {
        'total_fat_%': [0.4, 0.6],
        'protein_%': [0.2, 0.4],
        'carbs_%': [0.1, 0.3]
    }
    mock_calories_per_gram.return_value = [4.0, 4.0, 9.0]

    # Call the main function
    main()

    # Assert that the functions were called
    mock_DataPreprocessing.assert_called_once_with(
        './datasets/RAW_recipes.csv', './datasets/nutrition_table_nutriscore_no_outliers.csv'
    )
    mock_DataPreprocessing.return_value.load_and_preprocess_recipes_data.assert_called_once()
    mock_read_csv.assert_called_once_with(
        './datasets/nutrition_table_nutriscore_no_outliers.csv'
    )
    mock_DataPreprocessing.return_value.merge_data.assert_called_once_with(
        mock_raw_data, mock_nutriscore_data
    )
    mock_DataPreprocessing.return_value.filter_columns.assert_called_once_with(
        mock_merged_data, [
        'id', 'calories', 'total_fat_%', 'sugar_%', 'sodium_%',
        'protein_%', 'sat_fat_%', 'carbs_%'
    ])
    mock_LinearRegressionNutrition.assert_called_once_with(
        mock_filtered_data,
        'calories',
        ['total_fat_%', 'protein_%', 'carbs_%']
    )
    mock_linear_regression_nutrition.linear_regression.assert_called_once()
    mock_linear_regression_nutrition.plot_linear_regression.assert_called_once_with(
        [100, 200, 300], [110, 210, 310]
    )
    mock_calories_per_gram.assert_called_once_with([0.5, 0.3, 0.2])
    mock_linear_regression_nutrition.bootstrap_confidence_interval.assert_called_once()
    