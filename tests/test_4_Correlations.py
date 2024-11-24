import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch
import importlib.util
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                 '../src'))
)
# importing modules from 4_Correlations.py that has a name not supported 
# in python (starts with a number)
spec = importlib.util.spec_from_file_location(
    "correlations",
    os.path.join(os.path.dirname(__file__),
                 '../src/pages/4_Correlations.py')
)
correlations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(correlations)


@pytest.fixture
def mock_filtered_data():
    return pd.DataFrame({
        'id': [1, 2, 3],
        'dv_calories_%': [10, 20, 30],
        'dv_total_fat_%': [5, 10, 15],
        'dv_sugar_%': [5, 10, 15],
        'dv_sodium_%': [5, 10, 15],
        'dv_protein_%': [5, 10, 15],
        'dv_sat_fat_%': [5, 10, 15],
        'dv_carbs_%': [5, 10, 15],
        'nutriscore': [10, 20, 30],
        'minutes': [30, 60, 90],
        'n_steps': [5, 10, 15],
        'n_ingredients': [5, 10, 15]
    })


@pytest.fixture
def mock_interaction_data():
    return pd.DataFrame({
        'user_id': [1, 2, 3],
        'recipe_id': [10, 20, 30],
        'date': ['2021-01-01', '2021-01-02', '2021-01-03'],
        'rating': [5, 10, 15],
        'review': ['Good', 'Very good', 'Excellent'],
    })


@pytest.fixture
def mock_nutriscore_data():
    return pd.DataFrame({
        'id': [1, 2, 3],
        'dv_calories_%': [10, 20, 30],
        'dv_total_fat_%': [5, 10, 15],
        'dv_sugar_%': [5, 10, 15],
        'dv_sodium_%': [5, 10, 15],
        'dv_protein_%': [5, 10, 15],
        'dv_sat_fat_%': [5, 10, 15],
        'dv_carbs_%': [5, 10, 15],
        'nutriscore': [10, 20, 30],
        'label': ['A', 'B', 'C']
    })


@patch('streamlit.markdown')
def test_display_header(mock_markdown):
    correlations.display_header()
    assert mock_markdown.call_count > 0


@patch('streamlit.write')
@patch('streamlit.pyplot')
@patch('streamlit.multiselect')
def test_display_recipe_correlation(
    mock_multiselect,
    mock_pyplot,
    mock_write,
    mock_filtered_data
):
    mock_multiselect.return_value = [
        'dv_calories_%', 'dv_total_fat_%', 'dv_sugar_%', 'dv_sodium_%',
        'dv_protein_%', 'dv_sat_fat_%', 'dv_carbs_%', 'nutriscore',
        'minutes', 'n_steps', 'n_ingredients'
    ]
    correlations.display_recipe_correlation(mock_filtered_data)
    assert mock_write.call_count > 0
    assert mock_pyplot.call_count > 0


@patch('streamlit.write')
@patch('streamlit.pyplot')
@patch('streamlit.multiselect')
@patch('streamlit.dataframe')
def test_display_interaction_correlation(
    mock_dataframe,
    mock_multiselect,
    mock_pyplot,
    mock_write,
    mock_interaction_data,
    mock_nutriscore_data
):
    mock_multiselect.return_value = [
        'review_count', 'rating_count', 'average_rating', 'nutriscore'
    ]
    correlations.display_interaction_correlation(
        mock_interaction_data,
        mock_nutriscore_data
    )
    assert mock_write.call_count > 0
    assert mock_pyplot.call_count > 0
    assert mock_dataframe.call_count > 0


@patch.object(correlations, 'fetch_data_from_db')
@patch.object(correlations, 'display_header')
@patch.object(correlations, 'display_recipe_correlation')
@patch.object(correlations, 'display_interaction_correlation')
def test_main(
    mock_display_interaction_correlation,
    mock_display_recipe_correlation,
    mock_display_header,
    mock_fetch_data_from_db,
    mock_filtered_data,
    mock_interaction_data,
    mock_nutriscore_data
):
    mock_fetch_data_from_db.return_value = (
        mock_filtered_data,
        mock_interaction_data,
        mock_nutriscore_data,
        None
    )
    correlations.main()
    assert mock_display_header.call_count == 1
    assert mock_display_recipe_correlation.call_count == 1
    assert mock_display_interaction_correlation.call_count == 1