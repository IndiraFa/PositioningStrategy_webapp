import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import importlib.util
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                '../src'))
)

# Import the Homepage module
spec = importlib.util.spec_from_file_location(
    "Homepage",
    os.path.join(os.path.dirname(__file__), '../src/Homepage.py')
)
Homepage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Homepage)


@pytest.fixture
def mock_fetch_data():
    """
    Mock the fetch_data_from_db function
    """
    with patch('Homepage.fetch_data_from_db') as mock:
        yield mock


@patch("Homepage.Database.fetch_data") 
def test_get_cached_data(mock_fetch_data):
    """
    Test the get_cached_data function.
    """
    mock_fetch_data.side_effect = [
        pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}), 
        pd.DataFrame({"col1": [5, 6], "col2": [7, 8]}), 
    ]

    db_instance = MagicMock()
    query1 = 'SELECT * FROM "NS_withOutliers"'
    query2 = 'SELECT * FROM "NS_noOutliers"'
    result_with_outliers, result_no_outliers = \
        Homepage.get_cached_data(db_instance, query1, query2)

    assert len(result_with_outliers) == 2
    assert len(result_no_outliers) == 2
    assert mock_fetch_data.call_count == 2

class MockDatabase:
    def fetch_data(self, query):
        if "NS_withOutliers" in query:
            return pd.DataFrame({"label": [1, 2], "col2": [3, 4], "nutriscore": [50, 60]})
        elif "NS_noOutliers" in query:
            return pd.DataFrame({"label": [5, 6], "col2": [7, 8], "nutriscore": [55, 65]})
        else:
            return pd.DataFrame()


def test_dropna_nutriscore_data():
    """
    Test the dropna_nutriscore_data function

    Returns:
        None
    """
    data = pd.DataFrame({'nutriscore': [1, 2, None, 4]})
    result = Homepage.dropna_nutriscore_data(data)
    assert result.shape[0] == 3


@patch('streamlit.markdown')
@patch('streamlit.write')
@patch('streamlit.page_link')
def test_display_header(mock_page_link, mock_write, mock_markdown):
    """
    Test the display_header function

    Args:
        mock_page_link (fixture): Mock the page_link function
        mock_write (fixture): Mock the write function
        mock_markdown (fixture): Mock the markdown function

    Returns:
        None
    """
    Homepage.display_header()
    mock_markdown.assert_called()
    mock_write.assert_called()


def test_analyze_data():
    """
    Test the analyze_data function
    
    Returns:
        None
    """
    data_with_outliers = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    data_no_outliers = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    result = Homepage.analyze_data(data_with_outliers, data_no_outliers)
    assert 'Mean' in result.columns
    assert 'Median' in result.columns
    assert 'Max' in result.columns
    assert 'Min' in result.columns
    assert 'Skewness' in result.columns
    assert 'Kurtosis' in result.columns


@patch('streamlit.slider')
@patch('streamlit.plotly_chart')
@patch('streamlit.divider')
@patch('streamlit.write')
@patch('streamlit.subheader')
def test_display_histograms(
    mock_subheader,
    mock_write,
    mock_divider,
    mock_plotly_chart,
    mock_slider
):
    """
    Test the display_histograms function

    Args:
        mock_subheader (fixture): Mock the subheader function
        mock_write (fixture): Mock the write function
        mock_divider (fixture): Mock the divider function
        mock_plotly_chart (fixture): Mock the plotly_chart function
        mock_slider (fixture): Mock the slider function

    Returns:
        None
    """
    data_with_outliers = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    data_no_outliers = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    results = pd.DataFrame({
        'Mean': [2.5, 2.5],
        'Median': [2.5, 2.5],
        'Max': [4, 4],
        'Min': [1, 1],
        'Skewness': [0, 0],
        'Kurtosis': [-1.2, -1.2]
    })
    mock_slider.return_value = 28
    Homepage.display_histograms(data_with_outliers, data_no_outliers, results)
    mock_subheader.assert_called()
    mock_write.assert_called()
    mock_divider.assert_called()
    mock_plotly_chart.assert_called()
    mock_slider.assert_called()


@patch('streamlit.selectbox')
@patch('streamlit.write')
@patch('streamlit.divider')
@patch('Homepage.shapiro_test')
@patch('Homepage.ks_test')
@patch('Homepage.ad_test')
def test_display_distribution_analysis(
    mock_ad_test,
    mock_ks_test,
    mock_shapiro_test,
    mock_divider,
    mock_write,
    mock_selectbox
):
    """
    Test the display_distribution_analysis function

    Args:
        mock_ad_test (fixture): Mock the ad_test function
        mock_ks_test (fixture): Mock the ks_test function
        mock_shapiro_test (fixture): Mock the shapiro_test function
        mock_divider (fixture): Mock the divider function
        mock_write (fixture): Mock the write function
        mock_selectbox (fixture): Mock the selectbox function

    Returns:
        None
    """
    data_with_outliers = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    data_no_outliers = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    mock_selectbox.return_value = "Shapiro-Wilk"
    mock_shapiro_test.return_value = (0.9, 0.05)
    Homepage.display_distribution_analysis(
        data_with_outliers,
        data_no_outliers
    )
    mock_selectbox.assert_called()
    mock_write.assert_called()
    mock_divider.assert_called()


@patch('streamlit.plotly_chart')
@patch('streamlit.image')
@patch('streamlit.write')
@patch('streamlit.subheader')
def test_display_label_distribution(
    mock_subheader,
    mock_write,
    mock_image,
    mock_plotly_chart
):
    """
    Test the display_label_distribution function

    Args:
        mock_subheader (fixture): Mock the subheader function
        mock_write (fixture): Mock the write function
        mock_image (fixture): Mock the image function
        mock_plotly_chart (fixture): Mock the plotly_chart function

    Returns:
        None
    """
    data_with_outliers = pd.DataFrame({'label': ['A', 'B', 'C', 'D', 'E']})
    data_no_outliers = pd.DataFrame({'label': ['A', 'B', 'C', 'D', 'E']})
    Homepage.display_label_distribution(data_with_outliers, data_no_outliers)
    mock_subheader.assert_called()
    mock_image.assert_called()
    mock_plotly_chart.assert_called()
