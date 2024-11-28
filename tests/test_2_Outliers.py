import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import importlib.util

# Add the source path to import necessary modules
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
)

# Import the 2_Outliers module for testing
spec = importlib.util.spec_from_file_location(
    "module_2_Outliers",  
    os.path.join(os.path.dirname(__file__), '../src/pages/2_Outliers.py') 
)
module_2_Outliers = importlib.util.module_from_spec(spec)
sys.modules["module_2_Outliers"] = module_2_Outliers 
spec.loader.exec_module(module_2_Outliers)


# Define mocks for testing
@pytest.fixture
def mock_fetch_data():
    with patch.object(module_2_Outliers, 'fetch_data_from_db') as mock:
        yield mock

# Test the data caching functionality
def test_get_cached_data(mock_fetch_data):
    mock_fetch_data.return_value = (
        pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
        pd.DataFrame(), pd.DataFrame()
    )
    configs_db = {}
    result = module_2_Outliers.get_cached_data(
        configs_db, "query1", "query2", "query3", "query4", "query5", "query6"
    )
    assert len(result) == 6

# Test the introduction display functionality
def test_display_introduction():
    with patch('streamlit.markdown') as mock_markdown:
        module_2_Outliers.display_introduction()
        mock_markdown.assert_called()
        assert "<h1 style=\"color:purple;\">" in mock_markdown.call_args[0][0]

# Test raw data loading and exploration
def test_load_and_explore_raw_data():
    with patch('streamlit.write') as mock_write:
        mock_raw_data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        module_2_Outliers.load_and_explore_raw_data(mock_raw_data)
        mock_write.assert_called()

# Test formatted data analysis
def test_analyze_formatted_data():
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

# Test manual outlier detection using thresholds
def test_identify_outliers_with_manual_filters():
    with patch('streamlit.markdown') as mock_markdown, \
        patch('streamlit.expander') \
            as mock_expander:
        module_2_Outliers.identify_outliers_with_manual_filters()
        mock_markdown.assert_called()
        mock_expander.assert_called()

# Test Z-score method for outlier detection
def test_apply_z_score_method():
    with patch('streamlit.markdown') as mock_markdown, \
        patch('streamlit.expander') \
            as mock_expander:
        module_2_Outliers.apply_z_score_method(645)
        mock_markdown.assert_called()
        mock_expander.\
            assert_called_with("Note: Click to display more information")

# Test data distribution visualization
def test_visualize_data_distribution():
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

# Test conclusion display functionality
def test_display_conclusion():
    with patch('streamlit.markdown') as mock_markdown:
        module_2_Outliers.display_conclusion()
        mock_markdown.assert_called()
        assert "<div style=\"border: 2px solid purple;" \
            in mock_markdown.call_args[0][0]

# Test the main workflow through the main function
def test_main(mock_fetch_data):
    # Create mock data
    mock_formatted_data = MagicMock(spec=pd.DataFrame)
    mock_raw_data = MagicMock(spec=pd.DataFrame)
    mock_normalized_data = MagicMock(spec=pd.DataFrame)
    mock_outliers_data = MagicMock(spec=pd.DataFrame)
    mock_nutrition_noOutliers = MagicMock(spec=pd.DataFrame)
    mock_prefiltre_data = MagicMock(spec=pd.DataFrame)

    # Configure the mock to return the fake data
    mock_fetch_data.return_value = (
        mock_formatted_data,
        mock_raw_data,
        mock_normalized_data,
        mock_outliers_data,
        mock_nutrition_noOutliers,
        mock_prefiltre_data
    )

    # Execute the main function
    with patch('module_2_Outliers.display_introduction') as mock_intro, \
         patch('module_2_Outliers.load_and_explore_raw_data') as mock_explore,\
         patch('module_2_Outliers.analyze_formatted_data') as mock_analyze, \
         patch('module_2_Outliers.identify_outliers_with_manual_filters') \
            as mock_manual, \
         patch('module_2_Outliers.apply_z_score_method') as mock_zscore, \
         patch('module_2_Outliers.visualize_data_distribution') \
            as mock_visualize, \
         patch('module_2_Outliers.display_conclusion') as mock_conclusion:
        module_2_Outliers.main()

        #Verify that all functions were called
        mock_intro.assert_called_once()
        mock_explore.assert_called_once()
        mock_analyze.assert_called_once()
        mock_manual.assert_called_once()
        mock_zscore.assert_called_once()
        mock_visualize.assert_called_once()
        mock_conclusion.assert_called_once()

