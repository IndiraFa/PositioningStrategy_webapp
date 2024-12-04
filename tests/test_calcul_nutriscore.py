import pytest
import pandas as pd
import toml
import os
import sys

# Add the 'src' folder to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                             '..', 'src')))

from sqlalchemy import create_engine, text
from unittest.mock import patch, MagicMock
from calcul_nutriscore import NutriScore, Plot
from streamlit_todb import fetch_data_from_db, configs_db

# SQL Queries
query1 = 'SELECT * FROM "nutrition_withOutliers"'
query2 = 'SELECT * FROM "nutrient_table"'
query3 = 'SELECT * FROM "NS_withOutliers"'

# Data loading
nutrition_withOutliers, nutrient_table, NS_withOutliers, _, _, _ = \
    fetch_data_from_db(configs_db, query1, query2, query3)


# Fixtures
@pytest.fixture
def sample_data():
    """Fixture for the sample data."""
    return nutrition_withOutliers


@pytest.fixture
def sample_grille():
    """
    Fixture for the nutrient table (grille).
    """
    return nutrient_table


@pytest.fixture
def sample_configs():
    """
    Fixture for the database configuration.
    """
    configs = configs_db.copy()  # Copy the existing configuration
    configs['grillecolname'] = [
        'dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 
        'dv_protein_%'
    ]
    return configs


@pytest.fixture
def db_connection():
    """
    Fixture for creating a database connection using secrets.toml.
    """
    try:
        secrets = toml.load(".streamlit/secrets.toml")
    except FileNotFoundError:
        pytest.fail("The secrets.toml file is missing.")
    except toml.TomlDecodeError:
        pytest.fail("The secrets.toml file contains a format error.")

    db_config = secrets["connections"]["postgresql"]
    db_url = f"postgresql://{db_config['username']}:{db_config['password']}@" \
             f"{db_config['host']}:{db_config['port']}/{db_config['database']}"

    engine = create_engine(db_url)
    with engine.connect() as conn:
        yield conn


# Tests for NutriScore

@patch.object(NutriScore, 'calcul_nutriscore')
@patch.object(NutriScore, 'set_scorelabel')
def test_init(mock_set_scorelabel, mock_calcul_nutriscore):
    """
    Test the __init__ method of the NutriScore class.

    The method should initialize the attributes and call the calcul_nutriscore
    and set_scorelabel methods.

    Parameters
    ----------
    mock_set_scorelabel : MagicMock
        Mock object for the set_scorelabel method.
    mock_calcul_nutriscore : MagicMock
        Mock object for the calcul_nutriscore method.

    Returns
    -------
    None
    """
    # Mock return values for the methods
    mock_calcul_nutriscore.return_value = 'mock_nutriscore'
    mock_set_scorelabel.return_value = 'mock_label'

    # Sample data for testing
    data = {'sample': 'data'}
    grille = {'sample': 'grille'}
    configs = {'sample': 'configs'}

    # Create an instance of NutriScore
    nutriscore_instance = NutriScore(data, grille, configs)

    # Assertions to check if the attributes are correctly initialized
    assert nutriscore_instance.data == data
    assert nutriscore_instance.grille == grille
    assert nutriscore_instance.configs == configs

    # Assertions to check if the methods are called and return the correct 
    # values
    mock_calcul_nutriscore.assert_called_once()
    mock_set_scorelabel.assert_called_once()
    assert nutriscore_instance.nutriscore == 'mock_nutriscore'
    assert nutriscore_instance.nutriscore_label == 'mock_label'


def test_calcul_nutriscore(sample_data, sample_grille, sample_configs):
    """
    Test the NutriScore calculation logic.

    The method should return a DataFrame with the NutriScore values.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    sample_grille : pd.DataFrame
        Sample nutrient table for testing.
    sample_configs : dict
        Sample database configuration for testing.

    Returns
    -------
    None
    """
    nutri_score = NutriScore(sample_data, sample_grille, sample_configs)
    result = nutri_score.calcul_nutriscore()
    assert 'nutriscore' in result.columns, "NutriScore column is missing."
    assert not result['nutriscore'].isnull().any(),\
        "NutriScore contains NaN values."
    assert result['nutriscore'].dtype == float,\
          "NutriScore should be of type float."


def test_set_scorelabel(sample_data, sample_grille, sample_configs):
    """
    Test the labeling logic based on NutriScore values.

    The method should return a DataFrame with the NutriScore labels.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    sample_grille : pd.DataFrame
        Sample nutrient table for testing.
    sample_configs : dict
        Sample database configuration for testing.

    Returns
    -------
    None
    """
    nutri_score = NutriScore(sample_data, sample_grille, sample_configs)
    result = nutri_score.set_scorelabel()
    assert 'label' in result.columns, "Label column is missing."
    assert set(result['label']).issubset({'A', 'B', 'C', 'D', 'E'}), \
        "Invalid NutriScore labels detected."


def test_stock_database_real(db_connection):
    """
    Test to verify real table sizes in the database.

    The method should check if the sizes of the tables NS_withOutliers and
    nutrition_withOutliers are the same and greater than zero.

    Parameters
    ----------
    db_connection : sqlalchemy.engine.base.Connection
        Database connection object.

    Returns
    -------
    None
    """
    query_count_ns = text('SELECT COUNT(*) FROM "NS_withOutliers"')
    query_count_nutrition = text(
        'SELECT COUNT(*) FROM "nutrition_withOutliers"'
        )

    count_ns = db_connection.execute(query_count_ns).scalar()
    count_nutrition = db_connection.execute(query_count_nutrition).scalar()

    assert count_ns == count_nutrition, (
        f"The size of the table NS_withOutliers ({count_ns}) "
        f"does not match that of nutrition_withOutliers ({count_nutrition})."
    )
    assert count_ns > 0,\
          "The NS_withOutliers table is empty or does not exist."



# Tests for Plot

def test_init_plot():
    """
    Test the __init__ method of the Plot class.
    
    The method should initialize the attributes of the Plot class.

    Returns
    -------
    None
    """
    data = [1, 2, 3, 4, 5]
    title = "Test Title"
    xlabel = "X-Axis"
    ylabel = "Y-Axis"
    output_path = "test.png"

    # Create an instance of Plot
    plot_instance = Plot(data, title, xlabel, ylabel, output_path)

    # Assertions to check if the attributes are correctly initialized
    assert plot_instance.data == data
    assert plot_instance.title == title
    assert plot_instance.xlabel == xlabel
    assert plot_instance.ylabel == ylabel
    assert plot_instance.output_path == output_path


def test_plot_distribution():
    """
    Test the plot distribution function.
    
    The method should plot the distribution of the data and save it to the
    output path.

    Returns
    -------
    None
    """
    data = [1, 2, 3, 4, 5]
    plot = Plot(data, title="Test Title", xlabel="X-Axis", ylabel="Y-Axis", 
                output_path="test.png")
    with patch('matplotlib.pyplot.savefig') as savefig_mock:
        plot.plot_distribution()
        savefig_mock.assert_called_once_with("test.png")


def test_plot_distribution_label():
    """
    Test the label distribution plotting function.
    
    The method should plot the distribution of the labels and save it to the
    output path.

    Returns
    -------
    None
    """
    data = ['A', 'B', 'C', 'D', 'E']
    labels = ['A', 'B', 'C', 'D', 'E']
    plot = Plot(data, title="Test Title", xlabel="X-Axis", ylabel="Y-Axis", 
                output_path="test_label.png")
    with patch('matplotlib.pyplot.savefig') as savefig_mock:
        plot.plot_distribution_label(labels)
        savefig_mock.assert_called_once_with("test_label.png")

