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
# Import module 6_Appendix.py
spec = importlib.util.spec_from_file_location(
    "module_6_Appendix",
    os.path.join(os.path.dirname(__file__),
                 '../src/pages/6_Appendix.py')
)
module_6_Appendix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module_6_Appendix)

# @pytest.fixture
# def mock_fetch_data():
#     with patch.object(module_6_Appendix, 'fetch_data_from_db') as mock:
#         yield mock

# def test_get_cached_data(mock_fetch_data):
#     # Mock the return value of fetch_data_from_db
#     mock_fetch_data.return_value = (
#         pd.DataFrame(),
#         pd.DataFrame(),
#         pd.DataFrame(),
#         pd.DataFrame(),
#         pd.DataFrame(),
#         pd.DataFrame()
#     )
#     configs_db = {}
#     query = 'SELECT * FROM "NS_withOutliers"'
#     result = module_6_Appendix.get_cached_data(configs_db, query)
#     assert len(result) == 6

@patch('streamlit.markdown')
def test_display_header(mock_markdown):
    module_6_Appendix.display_header()
    mock_markdown.assert_called_once_with(
        "<h1 style='color:purple;'>Appendix</h1>",
        unsafe_allow_html=True
    )

@patch('streamlit.write')
def test_display_nutriscore_description(mock_write):
    module_6_Appendix.display_nutriscore_description()
    assert mock_write.called

@patch('pandas.read_csv')
@patch('streamlit.write')
@patch('streamlit.dataframe')
@patch('streamlit.image')
def test_display_nutriscore_grid(
    mock_image,
    mock_dataframe,
    mock_write,
    mock_read_csv
):
    mock_read_csv.return_value = pd.DataFrame()
    module_6_Appendix.display_nutriscore_grid()
    assert mock_read_csv.called
    assert mock_write.called
    assert mock_dataframe.called
    assert mock_image.called

@patch('streamlit.write')
@patch('streamlit.dataframe')
def test_display_example_calculation(mock_dataframe, mock_write):
    df2 = pd.DataFrame({
        'id': [137434],
        'calories': [200],
        'saturated_fat': [5],
        'sugar': [10],
        'sodium': [300],
        'protein': [20]
    })
    module_6_Appendix.display_example_calculation(df2)
    assert mock_write.called
    assert mock_dataframe.called

@patch('streamlit.write')
def test_display_references(mock_write):
    module_6_Appendix.display_references()
    assert mock_write.called

@patch.object(module_6_Appendix, 'display_header')
@patch.object(module_6_Appendix, 'display_nutriscore_description')
@patch.object(module_6_Appendix, 'display_nutriscore_grid')
@patch.object(module_6_Appendix, 'display_example_calculation')
@patch.object(module_6_Appendix, 'display_references')
@patch.object(module_6_Appendix, 'get_cached_data')
def test_main(
    mock_get_cached_data,
    mock_display_references,
    mock_display_example_calculation,
    mock_display_nutriscore_grid,
    mock_display_nutriscore_description,
    mock_display_header
):
    # Mock the return value of get_cached_data to return 6 values
    mock_get_cached_data.return_value = (
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame()
    )
    module_6_Appendix.main()
    assert mock_display_header.called
    assert mock_display_nutriscore_description.called
    assert mock_display_nutriscore_grid.called
    assert mock_display_example_calculation.called
    assert mock_display_references.called
