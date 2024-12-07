import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import importlib.util
from io import StringIO

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                 '../src'))
)
# Import module 2_Outliers.py
spec = importlib.util.spec_from_file_location(
    "module_2_Outliers",
    os.path.join(os.path.dirname(__file__),
                 '../src/pages/2_Outliers.py')
)
module_2_Outliers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_2_Outliers)


@pytest.fixture
def mock_fetch_data():
    """
    Fixture to mock the 'fetch_data_from_db' method of the 2_Outliers module.
    This is used in tests that require mocked data fetching from the database.
    """
    with patch.object(module_2_Outliers, 'fetch_data_from_db') as mock:
        yield mock


def test_display_introduction():
    """
    Test the display_introduction function to ensure that it renders
    the introduction markdown with the correct HTML style.
    """
    with patch('streamlit.markdown') as mock_markdown:
        module_2_Outliers.display_introduction()
        mock_markdown.assert_called()
        assert "<h1 style=\"color:purple;\">" in mock_markdown.call_args[0][0]

def test_load_and_explore_raw_data():
    """
    Test the load_and_explore_raw_data function to ensure it renders
    the raw data correctly using streamlit.write.
    """
    with patch('streamlit.write') as mock_write:
        mock_raw_data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        module_2_Outliers.load_and_explore_raw_data(mock_raw_data)
        mock_write.assert_called()

def test_analyze_formatted_data():
    """
    Test the analyze_formatted_data function to verify that it processes
    the data correctly and calls streamlit.write and streamlit.latex.
    """
    with patch('streamlit.write') as mock_write, patch('streamlit.latex') \
            as mock_latex:
        mock_formatted_data = pd.DataFrame({'col1': [1], 'col2': [2]})
        mock_normalized_data = pd.DataFrame({'col3': [3], 'col4': [4]})
        module_2_Outliers.analyze_formatted_data(mock_formatted_data,
                                                 mock_normalized_data)
        mock_write.assert_called()
        mock_latex.assert_called_with(
            '\n    \\text{daily value} = \\frac{\\text{portion value}}{2000} '
            '\\times 100\n            '
        )

def test_identify_outliers_with_manual_filters():
    """
    Test the identify_outliers_with_manual_filters function to ensure it
    triggers the correct markdown and expander elements in streamlit.
    """
    with patch('streamlit.markdown') as mock_markdown, \
        patch('streamlit.expander') \
            as mock_expander:
        module_2_Outliers.identify_outliers_with_manual_filters()
        mock_markdown.assert_called()
        mock_expander.assert_called()

def test_apply_z_score_method():
    """
    Test the apply_z_score_method function to ensure that it applies
    the Z-score method correctly and triggers the expected markdown and 
    expander.
    """
    with patch('streamlit.markdown') as mock_markdown, \
        patch('streamlit.expander') \
            as mock_expander:
        module_2_Outliers.apply_z_score_method(645)
        mock_markdown.assert_called()
        mock_expander.assert_called_with(
            "Note: Click to display more information"
        )

def test_visualize_data_distribution():
    """
    Test the visualize_data_distribution function to ensure it renders
    histograms, box plots, and charts with the correct data.
    """
    with patch('streamlit.selectbox', return_value='Calories distribution'), \
         patch('streamlit.radio', return_value='Filtered data'), \
         patch('streamlit.slider', return_value=(1500, 2000)), \
         patch('plotly.express.histogram') as mock_hist, \
         patch('plotly.express.box') as mock_box, \
         patch('streamlit.plotly_chart') as mock_chart:
        mock_normalized_data = pd.DataFrame({'dv_calories_%': [1500, 1800]})
        mock_prefiltre_data = pd.DataFrame({'dv_calories_%': [1200, 1700]})
        mock_nutrition_noOutliers = pd.DataFrame({'dv_calories_%':\
                                                   [1000, 1600]})
        module_2_Outliers.visualize_data_distribution(mock_normalized_data,
                                                    mock_prefiltre_data,
                                                    mock_nutrition_noOutliers)
        mock_hist.assert_called()
        mock_box.assert_called()
        mock_chart.assert_called()



def test_display_conclusion():
    with patch('streamlit.markdown') as mock_markdown:
        
        # Appel de la fonction à tester
        module_2_Outliers.display_conclusion()
        
        # Vérification que markdown a bien été appelé avec le CSS et le contenu HTML
        assert mock_markdown.call_count == 2  # Vérifie que markdown a été appelé 2 fois (pour CSS et HTML)
        




def test_main():
    with patch.object(
        module_2_Outliers, "get_cached_data"
        ) as mock_get_cached_data, \
        patch.object(
            module_2_Outliers, "display_introduction"
            ) as mock_display_introduction, \
        patch.object(
            module_2_Outliers, "load_and_explore_raw_data"
        ) as mock_load_and_explore_raw_data, \
        patch.object(
            module_2_Outliers, "analyze_formatted_data"
        ) as mock_analyze_formatted_data, \
        patch.object(
            module_2_Outliers, "identify_outliers_with_manual_filters"
        ) as mock_identify_outliers_with_manual_filters, \
        patch.object(
            module_2_Outliers, "apply_z_score_method"
        ) as mock_apply_z_score_method, \
        patch.object(
            module_2_Outliers, "visualize_data_distribution"
        ) as mock_visualize_data_distribution, \
        patch.object(
            module_2_Outliers, "display_conclusion"
        ) as mock_display_conclusion, \
        patch.object(
            module_2_Outliers.st, "error"
        ) as mock_st_error:
        
        mock_get_cached_data.return_value = {
            "formatted_data": pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}),
            "raw_data": pd.DataFrame({"col1": [5, 6], "col2": [7, 8]}),
            "normalized_data": pd.DataFrame(
                {"col1": [9, 10], "col2": [11, 12]}
            ),
            "outliers_data": pd.DataFrame(
                {"col1": [13, 14], "col2": [15, 16]}
            ),
            "nutrition_noOutliers": pd.DataFrame(
                {"col1": [17, 18], "col2": [19, 20]}
            ),
            "prefiltre_data": pd.DataFrame(
                {"col1": [21, 22], "col2": [23, 24]}
            ),
        }

        module_2_Outliers.main()

        mock_display_introduction.assert_called_once()
        mock_load_and_explore_raw_data.assert_called_once_with(
            mock_get_cached_data.return_value["raw_data"]
        )
        mock_analyze_formatted_data.assert_called_once_with(
            mock_get_cached_data.return_value["formatted_data"],
            mock_get_cached_data.return_value["normalized_data"]
        )
        mock_identify_outliers_with_manual_filters.assert_called_once()
        mock_apply_z_score_method.assert_called_once_with(
            mock_get_cached_data.return_value["outliers_data"].shape[0]
        )
        mock_visualize_data_distribution.assert_called_once_with(
            mock_get_cached_data.return_value["normalized_data"],
            mock_get_cached_data.return_value["prefiltre_data"],
            mock_get_cached_data.return_value["nutrition_noOutliers"]
        )
        mock_display_conclusion.assert_called_once()

        mock_st_error.assert_not_called()



def test_main_edge_cases():
    with patch.object(
        module_2_Outliers, "get_cached_data"
        ) as mock_get_cached_data, \
        patch.object(
            module_2_Outliers, "display_introduction"
        ) as mock_display_introduction, \
        patch.object(
            module_2_Outliers, "load_and_explore_raw_data"
        ) as mock_load_and_explore_raw_data, \
        patch.object(
            module_2_Outliers, "analyze_formatted_data"
        ) as mock_analyze_formatted_data, \
        patch.object(
            module_2_Outliers, "identify_outliers_with_manual_filters"
        ) as mock_identify_outliers_with_manual_filters, \
        patch.object(
            module_2_Outliers, "apply_z_score_method"
        ) as mock_apply_z_score_method, \
        patch.object(
            module_2_Outliers, "visualize_data_distribution"
        ) as mock_visualize_data_distribution, \
        patch.object(
            module_2_Outliers, "display_conclusion"
        ) as mock_display_conclusion, \
        patch.object(
            module_2_Outliers.st, "error"
        ) as mock_st_error:
        
        mock_get_cached_data.return_value = {}

        module_2_Outliers.main()

        mock_st_error.assert_called_once_with(
            "Unable to load data. Please check the database connection."
        )

        mock_display_introduction.assert_not_called()
        mock_load_and_explore_raw_data.assert_not_called()
        mock_analyze_formatted_data.assert_not_called()
        mock_identify_outliers_with_manual_filters.assert_not_called()
        mock_apply_z_score_method.assert_not_called()
        mock_visualize_data_distribution.assert_not_called()
        mock_display_conclusion.assert_not_called()

        mock_get_cached_data.return_value = {
            "formatted_data": pd.DataFrame(),
            "raw_data": pd.DataFrame(),
            "normalized_data": pd.DataFrame(),
            "outliers_data": pd.DataFrame(),
            "nutrition_noOutliers": pd.DataFrame(),
            "prefiltre_data": pd.DataFrame(),
        }

        module_2_Outliers.main()

        mock_st_error.assert_called_with(
            "Unable to load data. Please check the database connection."
        )

        mock_display_introduction.assert_not_called()
        mock_load_and_explore_raw_data.assert_not_called()
        mock_analyze_formatted_data.assert_not_called()
        mock_identify_outliers_with_manual_filters.assert_not_called()
        mock_apply_z_score_method.assert_not_called()
        mock_visualize_data_distribution.assert_not_called()
        mock_display_conclusion.assert_not_called()

        mock_get_cached_data.return_value = {
            "formatted_data": pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}),
            "raw_data": pd.DataFrame({"col1": [5, 6], "col2": [7, 8]}),
            "normalized_data": pd.DataFrame(
                {"col1": [9, 10], "col2": [11, 12]}
            ),
            "outliers_data": pd.DataFrame(
                {"col1": [13, 14], "col2": [15, 16]}
            ),
            "nutrition_noOutliers": pd.DataFrame(
                {"col1": [17, 18], "col2": [19, 20]}
            ),
            "prefiltre_data": pd.DataFrame(
                {"col1": [21, 22], "col2": [23, 24]}
            ),
        }

        module_2_Outliers.main()

        mock_display_introduction.assert_called_once()
        mock_load_and_explore_raw_data.assert_called_once_with(
            mock_get_cached_data.return_value["raw_data"]
        )
        mock_analyze_formatted_data.assert_called_once_with(
            mock_get_cached_data.return_value["formatted_data"],
            mock_get_cached_data.return_value["normalized_data"]
        )
        mock_identify_outliers_with_manual_filters.assert_called_once()
        mock_apply_z_score_method.assert_called_once_with(
            mock_get_cached_data.return_value["outliers_data"].shape[0]
        )
        mock_visualize_data_distribution.assert_called_once_with(
            mock_get_cached_data.return_value["normalized_data"],
            mock_get_cached_data.return_value["prefiltre_data"],
            mock_get_cached_data.return_value["nutrition_noOutliers"]
        )
        mock_display_conclusion.assert_called_once()

