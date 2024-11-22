import sys
import os
import pytest
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from unittest.mock import patch
# to be able to import the module from the src folder
sys.path.insert(0, os.path.abspath(os.path.join
                                   (os.path.dirname(__file__), '../src')
                                   ))
from interaction_correlation_analysis import InteractionData, LabelAnalysis

# Test the InteractionData class


@pytest.fixture
def test_interaction_data():
    """
    This fixture returns a DataFrame with the following columns:
    - user_id: user id
    - recipe_id: recipe id
    - date: date of the interaction
    - rating: rating of the recipe
    - review: review of the recipe
    """
    return pd.DataFrame({
        'user_id': [1, 2, 3, 4],
        'recipe_id': [1, 2, 3, 3],
        'date': ['2020-01-01', '2020-01-02', '2020-01-03', '2020-01-04'],
        'rating': [5, 4, 3, 2],
        'review': ['Good', 'Very good', 'Excellent', 'Bad']
    })


@pytest.fixture
def test_nutriscore_data():
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
        'id': [1, 3],
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
def test_merged_data():
    """
    This fixture returns a DataFrame with the following columns:
    - recipe_id: recipe id
    - interaction_count: number of interactions
    - review_count: number of reviews
    - rating_count: number of ratings
    - average_rating: average rating
    - nutriscore: nutriscore of the recipe
    - label: label of the recipe
    """
    return pd.DataFrame({
        'id': [1, 3],
        'interaction_count': [1, 2],
        'review_count': [1, 2],
        'rating_count': [1, 2],
        'average_rating': [5.0, 2.5],
        'nutriscore': ['12.0', '9.2'],
        'label': ['A', 'B']
    })


@pytest.fixture
def columns_to_keep():
    """
    This fixture returns a list of columns to keep in the data
    """
    return [
        'id',
        'interaction_count',
        'review_count',
        'rating_count',
        'average_rating',
        'nutriscore',
        'label'
    ]


@pytest.fixture
def columns_of_interest():
    """
    This fixture returns a list of columns of interest for the correlation
    """
    return ['interaction_count', 'average_rating', 'nutriscore']


def test_interactions_df(test_interaction_data):
    """
    Test the interactions_df method of the InteractionData class
    """
    interaction_data = InteractionData(data=test_interaction_data)
    result = interaction_data.interactions_df()
    assert isinstance(result, pd.DataFrame), "The output is not a DataFrame"
    expected_result = pd.DataFrame({
        'recipe_id': [1, 2, 3],
        'interaction_count': [1, 1, 2],
        'review_count': [1, 1, 2],
        'rating_count': [1, 1, 2],
        'average_rating': [5.0, 4.0, 2.5]
    })
    pd.testing.assert_frame_equal(result, expected_result), \
        "The output is not correct"


def test_merge_interaction_nutriscore(
        test_interaction_data,
        test_nutriscore_data,
        columns_to_keep,
        test_merged_data
):
    """
    Test the merge_interaction_nutriscore method of the InteractionData class
    """
    interaction_data = InteractionData(data=test_interaction_data)
    result = interaction_data.merge_interaction_nutriscore(
        test_nutriscore_data,
        columns_to_keep
    )
    assert isinstance(result, pd.DataFrame), "The output is not a DataFrame"
    expected_result = test_merged_data
    pd.testing.assert_frame_equal(result, expected_result), \
        "The output is not correct"


def test_interaction_correlation_matrix(
        test_interaction_data,
        test_nutriscore_data,
        columns_to_keep,
        columns_of_interest,
        test_merged_data
):
    """
    Test the interaction_correlation_matrix method of the InteractionData class
    """
    interaction_data = InteractionData(data=test_interaction_data)
    merged_data = interaction_data.merge_interaction_nutriscore(
        test_nutriscore_data,
        columns_to_keep
    )
    result = interaction_data.interaction_correlation_matrix(
        merged_data,
        columns_of_interest
    )
    assert isinstance(result, pd.DataFrame), "The output is not a DataFrame"
    
    expected_result = test_merged_data[columns_of_interest].corr()

    pd.testing.assert_frame_equal(result, expected_result), \
        "The output is not correct"


def test_plot_interaction_correlation_matrix(
        test_merged_data,
        columns_of_interest
):
    """
    Test the plot_interaction_correlation_matrix method of the 
    InteractionData class
    """
    interaction_data = InteractionData(data=test_merged_data)

    with patch.object(plt, 'show') as mock_show:
        with patch.object(sns, 'heatmap') as mock_heatmap:
            interaction_data.plot_interaction_correlation_matrix(
                test_merged_data,
                columns_of_interest
            )
            mock_heatmap.assert_called_once()
            args, kwargs = mock_heatmap.call_args
            assert 'annot' in kwargs and kwargs['annot'] is True
            assert 'cmap' in kwargs and kwargs['cmap'] == 'coolwarm'
            assert 'fmt' in kwargs and kwargs['fmt'] == '.2f'
            mock_show.assert_called_once()


# Test the LabelAnalysis class
@pytest.fixture
def test_label_data():
    """
    This fixture returns a DataFrame with the following columns:
    - label: label of the recipe
    - interaction_count: number of interactions
    - review_count: number of reviews
    - rating_count: number of ratings
    - average_rating: average rating
    """
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6],
        'label': ['A', 'B', 'C', 'A', 'B', 'E'],
        'interaction_count': [1, 2, 3, 4, 5, 6],
        'review_count': [1, 2, 3, 4, 5, 6],
        'rating_count': [1, 2, 3, 4, 5, 6],
        'average_rating': [5.0, 4.0, 3.0, 2.0, 1.0, 0.0]
    })


def test_label_analysis(test_label_data):
    """
    Test the label_analysis method of the LabelAnalysis class
    """
    label_analysis = LabelAnalysis()
    result = label_analysis.label_analysis(data=test_label_data)
    assert isinstance(result, pd.DataFrame), "The output is not a DataFrame"

    expected_result = pd.DataFrame({
        'label': ['A', 'B', 'C', 'E'],
        'average_rating': [3.5, 2.5, 3.0, 0.0],
        'interaction_count': [5, 7, 3, 6],
        'recipe_count': [2, 2, 1, 1],
        'interaction_recipe_ratio': [2.5, 3.5, 3.0, 6.0]
    })

    pd.testing.assert_frame_equal(result, expected_result), \
        "The output is not correct"
