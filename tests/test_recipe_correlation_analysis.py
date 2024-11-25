import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch
# to be able to import the module from the src folder
sys.path.insert(0, os.path.abspath(os.path.join
                                   (os.path.dirname(__file__), '../src')
                                   ))
from recipe_correlation_analysis import CorrelationAnalysis

# Test the CorrelationAnalysis class


@pytest.fixture
def test_data():
    """
    This fixture returns a DataFrame with the following columns:
    - id: recipe id
    - dv_calories_%: % daily value of calories
    - dv_total_fat_%: % daily value of total fat
    - dv_sugar_%: % daily value of sugar
    - dv_sodium_%: % daily value of sodium
    - dv_protein_%: % daily value of protein
    - dv_sat_fat_%: % daily value of saturated fat
    - dv_carbs_%: % daily value of carbohydrates
    - nutriscore: nutriscore of the recipe
    - minutes: time to prepare the recipe in minutes
    - n_steps: number of steps in the recipe
    - n_ingredients: number of ingredients in the recipe
    """
    return pd.DataFrame({
        'id': [1, 2, 3],
        'dv_calories_%': [10, 20, 30],
        'dv_total_fat_%': [5, 10, 15],
        'dv_sugar_%': [2, 4, 6],
        'dv_sodium_%': [1, 2, 3],
        'dv_protein_%': [3, 6, 9],
        'dv_sat_fat_%': [1, 2, 3],
        'dv_carbs_%': [50, 60, 70],
        'nutriscore': [1, 2, 3],
        'minutes': [30, 45, 60],
        'n_steps': [5, 10, 15],
        'n_ingredients': [7, 8, 9]
    })


@pytest.fixture
def columns_to_keep():
    """
    This fixture returns a list of columns to keep in the data
    """
    return [
        'id',
        'dv_calories_%',
        'dv_total_fat_%',
        'dv_sugar_%',
        'dv_sodium_%',
        'dv_protein_%',
        'dv_sat_fat_%',
        'dv_carbs_%',
        'nutriscore',
        'minutes',
        'n_steps',
        'n_ingredients'
    ]


@pytest.fixture
def columns_of_interest():
    """
    This fixture returns a list of columns of interest for the correlation
    """
    return [
        'dv_calories_%',
        'dv_total_fat_%',
        'dv_sugar_%',
        'dv_sodium_%',
        'dv_protein_%',
        'dv_sat_fat_%',
        'dv_carbs_%',
        'nutriscore',
        'minutes',
        'n_steps',
        'n_ingredients'
    ]


# Test the two possible cases of the __init__ method
def test_init_with_data(columns_to_keep, columns_of_interest, test_data):
    """
    Test the __init__ method when the data is passed as a DataFrame

    Parameters
    ----------
    columns_to_keep : list
        List of columns to keep in the data
    columns_of_interest : list
        List of columns of interest for the correlation
    test_data : DataFrame
        DataFrame with the data to analyze

    Returns
    -------
    None
    """
    correlation_analysis = CorrelationAnalysis(
        columns_to_keep,
        columns_of_interest,
        data=test_data
    )
    assert correlation_analysis.data.equals(test_data)
    assert correlation_analysis.columns_to_keep == columns_to_keep
    assert correlation_analysis.columns_of_interest == columns_of_interest
    assert correlation_analysis.filtered_data.equals(
        test_data[columns_to_keep]
    )


@patch('pandas.read_csv')
def test_init_with_paths(mock_read_csv, columns_to_keep, columns_of_interest):
    """
    test the __init__ method when the data is passed as paths to csv files

    Parameters
    ----------
    mock_read_csv : MagicMock
        Mock object for the pandas.read_csv function
    columns_to_keep : list
        List of columns to keep in the data
    columns_of_interest : list
        List of columns of interest for the correlation

    Returns
    -------
    None
    """
    # mock data
    recipes_data = pd.DataFrame({
        'id': [1, 2, 3],
        'dv_calories_%': [10, 20, 30],
        'dv_total_fat_%': [5, 10, 15],
        'dv_sugar_%': [2, 4, 6],
        'dv_sodium_%': [1, 2, 3],
        'dv_protein_%': [3, 6, 9],
        'dv_sat_fat_%': [1, 2, 3],
        'dv_carbs_%': [50, 60, 70]
    })
    nutriscore_data = pd.DataFrame({
        'id': [1, 2, 3],
        'nutriscore': [1, 2, 3],
        'minutes': [30, 45, 60],
        'n_steps': [5, 10, 15],
        'n_ingredients': [7, 8, 9]
    })
    merged_data = pd.merge(recipes_data, nutriscore_data, on='id')

    # Configure the mock to return the data
    mock_read_csv.side_effect = [recipes_data, nutriscore_data]

    # fake paths
    path_recipes_data = 'path/to/recipes.csv'
    path_nutriscore_data = 'path/to/nutriscore.csv'

    correlation_analysis = CorrelationAnalysis(
        columns_to_keep,
        columns_of_interest,
        path_recipes_data=path_recipes_data,
        path_nutriscore_data=path_nutriscore_data
    )
    assert correlation_analysis.recipes_data.equals(recipes_data)
    assert correlation_analysis.nutriscore_data.equals(nutriscore_data)
    assert correlation_analysis.data.equals(merged_data)
    assert correlation_analysis.columns_to_keep == columns_to_keep
    assert correlation_analysis.columns_of_interest == columns_of_interest
    assert correlation_analysis.filtered_data.equals(
        merged_data[columns_to_keep]
    )


def test_correlation_matrix(test_data, columns_to_keep, columns_of_interest):
    """
    Test the correlation_matrix method
    
    Parameters
    ----------
    test_data : DataFrame
        DataFrame with the data to analyze
    columns_to_keep : list
        List of columns to keep in the data
    columns_of_interest : list
        List of columns of interest for the correlation

    Returns
    -------
    None
    """
    correlation_analysis = CorrelationAnalysis(
        columns_to_keep,
        columns_of_interest,
        data=test_data
    )
    corr_matrix = correlation_analysis.correlation_matrix()
    expected_corr_matrix = test_data[columns_of_interest].corr()
    pd.testing.assert_frame_equal(corr_matrix, expected_corr_matrix)


@patch('matplotlib.pyplot.show')
@patch('seaborn.heatmap')
def test_plot_correlation_matrix(
    mock_heatmap,
    mock_show,
    test_data,
    columns_to_keep,
    columns_of_interest
):
    """
    Test the plot_correlation_matrix method 
    
    Parameters
    ----------
    mock_heatmap : MagicMock
        Mock object for the seaborn.heatmap function
    mock_show : MagicMock
        Mock object for the plt.show function
    test_data : DataFrame
        DataFrame with the data to analyze
    columns_to_keep : list
        List of columns to keep in the data
    columns_of_interest : list
        List of columns of interest for the correlation
                
    Returns
    -------
    None
    """
    correlation_analysis = CorrelationAnalysis(
        columns_to_keep,
        columns_of_interest,
        data=test_data
    )
    correlation_analysis.plot_correlation_matrix()
    # check that the heatmap was called with the correct arguments
    corr_matrix = test_data[columns_of_interest].corr()
    mock_heatmap.assert_called_once()
    args, kwargs = mock_heatmap.call_args
    pd.testing.assert_frame_equal(args[0], corr_matrix)
    assert kwargs['annot'] == True
    assert kwargs['cmap'] == 'coolwarm'
    assert kwargs['fmt'] == '.2f'
    # Check that plt.show was called
    mock_show.assert_called_once_with(block=False)
