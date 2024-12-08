import pytest
import pandas as pd
import toml
import os
import sys
from sqlalchemy import create_engine, text
import unittest
from unittest.mock import patch, MagicMock
# Add the 'src' folder to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                             '..', 'src')))

from calcul_nutriscore import NutriScore, Plot, main
from db.db_instance import db_instance

query1 = 'SELECT * FROM "nutrition_withOutliers"'
query2 = 'SELECT * FROM "nutrient_table"'
query3 = 'SELECT * FROM "NS_withOutliers"'

nutrient_table = db_instance.fetch_data(query2)
NS_withOutliers = db_instance.fetch_data(query3)


# Fixtures
@pytest.fixture
def sample_data():
    """Fixture for the sample data."""
    data = {
        'id': [1, 2, 3, 4],
        'dv_calories_%': [10, 15, 20, 12],
        'dv_total_fat_%': [5, 7, 8, 6],
        'dv_sugar_%': [6, 8, 9, 7],
        'dv_sodium_%': [2, 3, 1, 4],
        'dv_protein_%': [3, 2, 4, 5],
        'dv_sat_fat_%': [4, 5, 6, 3],
        'dv_carbs_%': [10, 9, 8, 7]
    }

    df = pd.DataFrame(data)
    return df


@pytest.fixture
def sample_grille():
    """
    Fixture for the nutrient table (grille).
    """
    data_grille = {
        'points': [0, 1, 1.25],
        'dv_calories_%': [37, 43, 49],
        'dv_sat_fat_%': [95, 114, 133],
        'dv_sugar_%': [84, 101, 114],
        'dv_sodium_%': [76, 89, 101],
        'dv_protein_%': [-91, -73, -55]
    }
    df_grille = pd.DataFrame(data_grille)
    return df_grille


@pytest.fixture
def sample_configs():
    """
    Fixture for the database configuration.
    """
    configs = {
            'nutritioncolname': [
                'calories',
                'total_fat_%',
                'sugar_%',
                'sodium_%',
                'protein_%',
                'sat_fat_%',
                'carbs_%'
            ],
            'grillecolname': [
                'dv_calories_%',
                'dv_sat_fat_%',
                'dv_sugar_%',
                'dv_sodium_%',
                'dv_protein_%'
            ],
            'dv_calories': 2000
        }
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


# # Tests for NutriScore

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
    mock_calcul_nutriscore.return_value = 'mock_nutriscore'
    mock_set_scorelabel.return_value = 'mock_label'

    data = {'sample': 'data'}
    grille = {'sample': 'grille'}
    configs = {'sample': 'configs'}

    nutriscore_instance = NutriScore(data, grille, configs)

    assert nutriscore_instance.data == data
    assert nutriscore_instance.grille == grille
    assert nutriscore_instance.configs == configs

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
    assert not result['nutriscore'].isnull().any(), \
        "NutriScore contains NaN values."
    assert result['nutriscore'].dtype == float, \
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
    assert count_ns > 0, \
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

    plot_instance = Plot(data, title, xlabel, ylabel, output_path)

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

class TestNutriScoreCalculation(unittest.TestCase):

    @patch('calcul_nutriscore.create_engine')
    @patch('calcul_nutriscore.toml.load')
    @patch('calcul_nutriscore.NutriScore')
    @patch('calcul_nutriscore.Plot')
    def test_main_function(self,
                            MockPlot,
                              MockNutriScore,
                                mock_toml_load,
                                  mock_create_engine):
        """
        Test the main function of the NutriScore calculation script.

        The main function should read the database configuration from the
        secrets.toml file, create a database connection, fetch the necessary
        data, and call the NutriScore and Plot classes.

        Parameters
        ----------
        MockPlot : MagicMock
            Mock object for the Plot class.
        MockNutriScore : MagicMock

        mock_toml_load : MagicMock
            Mock object for the toml.load function.
        mock_create_engine : MagicMock
            Mock object for the create_engine function.
        ----------
        """

        # Mock secrets.toml
        mock_toml_load.return_value = {
            'connections': {
                'postgresql': {
                    'username': 'user',
                    'password': 'pass',
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'test_db'
                }
            }
        }

        # Mock create_engine and database connection
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_create_engine.return_value = mock_engine

        # Mock DataFrames for SQL queries
        mock_conn.execute.return_value = None
        mock_conn.fetchall.return_value = None
        mock_df_raw_recipes = pd.DataFrame({'id': [1, 2],
                                             'name': ['Recipe1', 'Recipe2']})
        mock_df_nutrient_table = pd.DataFrame({'id': [1, 2],
                                                'nutrient': [10, 20]})
        mock_df_normalized_data = pd.DataFrame({'id': [1, 2],
                                                 'normalized': [0.5, 0.8]})

        with patch('pandas.read_sql_query',
                    side_effect=[mock_df_raw_recipes,
                                  mock_df_nutrient_table,
                                    mock_df_normalized_data]):
            # Mock NutriScore instance
            mock_nutri_score_instance = MagicMock()
            MockNutriScore.return_value = mock_nutri_score_instance

            # Mock Plot class
            mock_plot_instance = MagicMock()
            MockPlot.return_value = mock_plot_instance

            # Call the main function
            main()

            # Assertions
            mock_toml_load.assert_called_once()
            mock_create_engine.assert_called_once_with(
                'postgresql://user:pass@localhost:5432/test_db'
            )
            mock_nutri_score_instance.stock_database.assert_called_once()
            MockPlot.assert_called()
