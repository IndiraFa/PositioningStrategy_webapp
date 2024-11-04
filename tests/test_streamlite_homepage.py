import sys
import os
import pandas as pd
import plotly.express as px
import pytest

# Add the directory containing the modules to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_read_csv():
    # Test reading the CSV file
    try:
        nutriscore_data = pd.read_csv('./nutrition_table_nutriscore.csv')
        assert 'nutriscore' in nutriscore_data.columns
    except FileNotFoundError:
        pytest.fail("The CSV file was not found.")
    except Exception as e:
        pytest.fail(f"Error reading the CSV file: {e}")

def test_dropna():
    # Test dropping NaN values
    nutriscore_data = pd.read_csv('./nutrition_table_nutriscore.csv')
    nutriscore_data = nutriscore_data['nutriscore'].dropna()
    assert nutriscore_data.isna().sum() == 0

def test_plotly_histogram():
    # Test generating the histogram with Plotly
    nutriscore_data = pd.read_csv('./nutrition_table_nutriscore.csv')
    nutriscore_data = nutriscore_data['nutriscore'].dropna()
    fig = px.histogram(
        nutriscore_data, 
        x='nutriscore', 
        nbins=28,
        title='Nutri-Score Distribution',
        color_discrete_sequence=['#636EFA']
    )
    assert fig is not None
    assert fig.data[0].type == 'histogram'
    assert fig.layout.title.text == 'Nutri-Score Distribution'