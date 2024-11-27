import sys
import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import logging
import importlib.util

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')
))

# Import the module to test
spec = importlib.util.spec_from_file_location(
    "nutriscore_analysis",
    os.path.join(os.path.dirname(__file__), '../src/nutriscore_analysis.py')
)
nutriscore_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nutriscore_analysis)

@pytest.fixture
def mock_plot():
    with patch('nutriscore_analysis.Plot') as mock:
        yield mock

def test_nutriscore_analysis():
    data = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    result = nutriscore_analysis.nutriscore_analysis(data)
    assert result == (2.5, 2.5, 4, 1)

def test_shapiro_test():
    data = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    result = nutriscore_analysis.shapiro_test(data, 'nutriscore')
    assert isinstance(result, tuple)

def test_ks_test():
    data = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    result = nutriscore_analysis.ks_test(data, 'nutriscore')
    assert isinstance(result, tuple)

def test_ad_test():
    data = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    result = nutriscore_analysis.ad_test(data, 'nutriscore')
    assert isinstance(result, tuple)

def test_skewness():
    data = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    result = nutriscore_analysis.skewness(data, 'nutriscore')
    assert isinstance(result, float)

def test_kurtosis():
    data = pd.DataFrame({'nutriscore': [1, 2, 3, 4]})
    result = nutriscore_analysis.kurtosis(data, 'nutriscore')
    assert isinstance(result, float)

def test_label_percentage():
    data = pd.DataFrame({'label': ['A', 'B', 'A', 'C']})
    result = nutriscore_analysis.label_percentage(data, 'A')
    assert result == 0.5

@patch('nutriscore_analysis.pd.read_csv')
@patch('nutriscore_analysis.Plot')
def test_main(mock_plot, mock_read_csv):
    mock_read_csv.return_value = pd.DataFrame(
        {'nutriscore': [1, 2, 3, 4],
        'label': ['A', 'B', 'C', 'D']}
    )
    mock_plot_instance = MagicMock()
    mock_plot.return_value = mock_plot_instance

    with patch('builtins.print') as mock_print:
        nutriscore_analysis.main()
        assert mock_print.call_count > 0
