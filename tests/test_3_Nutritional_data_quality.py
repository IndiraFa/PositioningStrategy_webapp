import sys
import os
import pytest
import importlib.util
from unittest.mock import patch
import pandas as pd
import matplotlib.pyplot as plt

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


@pytest.fixture
def mock_fetch_data():
    with patch('module_3_Nutritional_data_quality.fetch_data_from_db') as mock:
        yield mock


@pytest.fixture
def mock_linear_regression_nutrition():
    with patch(
        'module_3_Nutritional_data_quality.LinearRegressionNutrition'
    ) as mock:
        yield mock


# # Example test to verify the functionality of the Streamlit page
# def test_page_load(mock_fetch_data):
#     """Test to verify that the page loads correctly"""
#     # Test if the module 3_Nutritional_data_quality loads without error
#     assert module_3_Nutritional_data_quality is not None


# def test_get_cached_data(mock_fetch_data):
#     mock_fetch_data.return_value = pd.DataFrame({'id': [1, 2, 3]})
#     query = "SELECT * FROM test_table"
#     result = module_3_Nutritional_data_quality.get_cached_data({}, query)
#     assert not result.empty





def test_write_linear_regression_results():
    with patch('streamlit.write') as mock_write:
        module_3_Nutritional_data_quality.write_linear_regression_results(
            [0.5, 0.3],
            1.2, 0.05, 0.8
        )
        assert mock_write.call_count == 4


def test_get_intervals_per_g():
    intervals_df = pd.DataFrame({
        'protein_%': [10],
        'total_fat_%': [20],
        'carbs_%': [30]
    }, index=['Lower Bound']).T
    result = module_3_Nutritional_data_quality.get_intervals_per_g(
        50, 70, 260, intervals_df
    )
    assert 'Calories per gram of Protein' in result.index
    assert 'Calories per gram of Fat' in result.index
    assert 'Calories per gram of Carbohydrates' in result.index


def test_get_values():
    df = pd.DataFrame({
        'Calories per gram of Protein': [4.06],
        'Calories per gram of Carbohydrates': [4.06],
        'Calories per gram of Fat': [8.84]
    }, index=['Value'])
    result = module_3_Nutritional_data_quality.get_values(df)
    assert result == [4.06, 4.06, 8.84]


def test_get_errors():
    values = [4.06, 4.06, 8.84]
    intervals_df = pd.DataFrame({
        'Lower Bound': [3.5, 3.5, 8.0],
        'Upper Bound': [4.5, 4.5, 9.0]
    }, index=[
        'Calories per gram of Protein',
        'Calories per gram of Carbohydrates',
        'Calories per gram of Fat'
    ])
    result = module_3_Nutritional_data_quality.get_errors(values, intervals_df)
    assert len(result) == 3


def test_plot_confidence_intervals():
    values_ref = [4.06]
    values = [4.06]
    errors = [[0.56], [0.44]]
    fig = module_3_Nutritional_data_quality.plot_confidence_intervals(
        values_ref, values, 'Protein', errors
    )
    assert isinstance(fig, plt.Figure)


def test_display_header():
    with patch('streamlit.markdown') as mock_markdown, \
        patch('streamlit.write') as mock_write:
        module_3_Nutritional_data_quality.display_header()
        assert mock_markdown.call_count == 3
        assert mock_write.call_count == 1


def test_display_linear_regression(mock_linear_regression_nutrition):
    mock_lr_instance = mock_linear_regression_nutrition.return_value 
    mock_lr_instance.linear_regression.return_value = (
        0.05, 0.8, 1.2, 
        pd.DataFrame(
            {'Coefficient': [0.5, 0.3, 0.4]},
            index=['total_fat_%', 'protein_%', 'carbs_%']
        ),
        pd.DataFrame({'y_test': [1.2, 2.3, 3.3]}, index=[0, 1, 2]),
        pd.DataFrame({'y_pred': [1.1, 2.1, 3.1]}, index=[0, 1, 2])
    )
    with patch('streamlit.write') as mock_write, \
        patch('streamlit.pyplot') as mock_pyplot:
        module_3_Nutritional_data_quality.display_linear_regression(
            mock_lr_instance
        )
        assert mock_write.call_count == 8
        assert mock_pyplot.call_count == 1


def test_display_confidence_interval_test(mock_linear_regression_nutrition):
    mock_lr_instance = mock_linear_regression_nutrition.return_value
    mock_lr_instance.bootstrap_confidence_interval.return_value = {
        'protein_%': [3.5, 4.5],
        'total_fat_%': [8.0, 9.0],
        'carbs_%': [3.5, 4.5]
    }
    mock_lr_instance.linear_regression.return_value = (
        0.05, 0.8, 1.2, 
        pd.DataFrame(
            {'Coefficient': [0.5, 0.3, 0.4]},
            index=['total_fat_%', 'protein_%', 'carbs_%']
        ),
        pd.DataFrame({'y_test': [1.2, 2.3, 3.3]}, index=[0, 1, 2]),
        pd.DataFrame({'y_pred': [1.1, 2.1, 3.1]}, index=[0, 1, 2])
    )
    with patch('streamlit.write') as mock_write, patch('streamlit.slider') \
        as mock_slider, patch('streamlit.table') as mock_table, \
            patch('streamlit.pyplot') as mock_pyplot, \
         patch('module_3_Nutritional_data_quality.get_intervals_per_g') \
            as mock_get_intervals_per_g, \
         patch('module_3_Nutritional_data_quality.get_values') \
            as mock_get_values, \
         patch('module_3_Nutritional_data_quality.get_errors') \
            as mock_get_errors, \
         patch('module_3_Nutritional_data_quality.plot_confidence_intervals') \
            as mock_plot_confidence_intervals:
        
        mock_slider.return_value = 0.9
        mock_get_intervals_per_g.return_value = pd.DataFrame({
            'Calories per gram of Protein': [4.06],
            'Calories per gram of Carbohydrates': [4.06],
            'Calories per gram of Fat': [8.84]
        }, index=['Value'])
        mock_get_values.side_effect = [[4.06, 4.06, 8.84], [4.06, 4.06, 8.84]]
        mock_get_errors.return_value = [
            [0.56, 0.44], [0.56, 0.44], [0.56, 0.44]
        ]
        mock_plot_confidence_intervals.return_value = plt.figure()

        module_3_Nutritional_data_quality.display_confidence_interval_test(
            mock_lr_instance
        )
        
        assert mock_write.call_count == 5
        assert mock_slider.call_count == 1
        assert mock_table.call_count == 2
        assert mock_pyplot.call_count == 3


@patch.object(module_3_Nutritional_data_quality, 'get_cached_data')
@patch.object(module_3_Nutritional_data_quality, 'display_header')
@patch.object(module_3_Nutritional_data_quality, 'display_linear_regression')
@patch.object(module_3_Nutritional_data_quality, 'display_confidence_interval_test')
@patch.object(module_3_Nutritional_data_quality, 'LinearRegressionNutrition')
def test_main(mock_LinearRegressionNutrition, mock_display_confidence_interval_test, mock_display_linear_regression, mock_display_header, mock_get_cached_data):
    # Simuler le retour de get_cached_data avec un DataFrame valide
    mock_filtered_data = pd.DataFrame({
        'id': [1, 2, 3],
        'total_fat_%': [10, 20, 30],
        'protein_%': [5, 10, 15],
        'carbs_%': [30, 40, 50],
        'calories': [100, 200, 300]
    })

    # Configurer le mock de get_cached_data pour renvoyer un DataFrame simulé
    mock_get_cached_data.return_value = mock_filtered_data

    # Simuler le comportement de la classe LinearRegressionNutrition
    mock_lr_instance = mock_LinearRegressionNutrition.return_value
    mock_lr_instance.fit.return_value = None  # Si nécessaire, mockez la méthode `fit`

    # Appeler la fonction main
    module_3_Nutritional_data_quality.main()

    # Vérifications : assurer que les fonctions d'affichage sont appelées
    mock_display_header.assert_called_once()
    mock_display_linear_regression.assert_called_once()
    mock_display_confidence_interval_test.assert_called_once()

    # Vérification que la classe LinearRegressionNutrition a été instanciée avec les bons arguments
    mock_LinearRegressionNutrition.assert_called_once_with(mock_filtered_data, 'calories', ['total_fat_%', 'protein_%', 'carbs_%'])

