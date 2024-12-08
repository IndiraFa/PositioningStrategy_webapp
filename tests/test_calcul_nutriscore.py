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

    @patch('calcul_nutriscore.db_instance')
    @patch('calcul_nutriscore.NutriScore')
    @patch('calcul_nutriscore.Plot')
    def test_main_function(self, MockPlot, MockNutriScore, mock_db_instance):
        """
        Test the main function of the NutriScore calculation script.

        Parameters
        ----------
        MockPlot : MagicMock
            Mock object for the Plot class.
        MockNutriScore : MagicMock
            Mock object for the NutriScore class.
        mock_db_instance : MagicMock
            Mock object for the database instance singleton.

        Returns
        -------
        None
        """

        # Mock DataFrames returned by db_instance
        mock_df_raw_recipes = pd.DataFrame({'id': [1, 2], 'name': ['Recipe1', 'Recipe2']})
        mock_df_nutrient_table = pd.DataFrame({'id': [1, 2], 'nutrient': [10, 20]})
        mock_df_normalized_data = pd.DataFrame({'id': [1, 2], 'normalized': [0.5, 0.8]})

        mock_db_instance.fetch_data.side_effect = [
            mock_df_raw_recipes,
            mock_df_nutrient_table,
            mock_df_normalized_data
        ]

        # Mock NutriScore instance and behavior
        mock_nutri_score_instance = MagicMock()
        MockNutriScore.return_value = mock_nutri_score_instance

        # Mock Plot instances
        mock_plot_instance = MagicMock()
        MockPlot.return_value = mock_plot_instance

        # Call the main function
        main()

        # Assertions for db_instance
        mock_db_instance.fetch_data.assert_any_call("SELECT * FROM raw_recipes")
        mock_db_instance.fetch_data.assert_any_call("SELECT * FROM nutrient_table")
        mock_db_instance.fetch_data.assert_any_call('SELECT * FROM "nutrition_withOutliers"')

        # Assertions for NutriScore
        MockNutriScore.assert_called_once_with(
            mock_df_normalized_data,
            mock_df_nutrient_table,
            {
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
        )
        mock_nutri_score_instance.stock_database.assert_called_once()

        # Assertions for Plot
        MockPlot.assert_any_call(
            mock_nutri_score_instance.nutriscore['nutriscore'],
            title='NutriScore Distribution',
            xlabel='NutriScore',
            ylabel='Number of Recipes',
            output_path='nutriscore_distribution.png'
        )
        MockPlot.assert_any_call(
            mock_nutri_score_instance.nutriscore_label['label'],
            title='NutriScore Label Distribution',
            xlabel='Labels',
            ylabel='Number of Recipes',
            output_path='nutriscore_label_distribution.png'
        )
        mock_plot_instance.plot_distribution.assert_called_once()
        mock_plot_instance.plot_distribution_label.assert_called_once_with(labels=['A', 'B', 'C', 'D', 'E'])
