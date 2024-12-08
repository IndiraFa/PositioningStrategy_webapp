import pytest
import os
import sys
from sqlalchemy import create_engine
from unittest.mock import MagicMock, patch
import pandas as pd
# Add the 'src' directory to the system path for importing modules
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
)

from db.streamlit_todb import Database



@pytest.fixture
def mock_database():
    """
    Fixture to provide a mock instance of the Database class.
    """
    with patch("db.streamlit_todb.create_engine") as mock_create_engine:
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Simuler un moteur SQLAlchemy avec des méthodes compatibles
        mock_engine.connect.return_value = MagicMock()  # Simule une connexion
        mock_engine.execute.return_value = MagicMock()  # Simule une exécution de requête
        
        yield Database()


def test_fetch_data_success(mock_database):
    """
    Test fetch_data method when the query executes successfully.
    """
    query = "SELECT * FROM test_table;"
    mock_result = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
    
    # Mock `pandas.read_sql_query`
    with patch("pandas.read_sql_query", return_value=mock_result) as mock_read_sql:
        result = mock_database.fetch_data(query)
        
        # Vérifier que la méthode est appelée avec les bons arguments
        mock_read_sql.assert_called_once_with(query, mock_database.engine)
        
        # Vérifier le type et le contenu du résultat
        assert isinstance(result, pd.DataFrame)
        assert result.equals(mock_result)


def test_fetch_data_failure(mock_database):
    """
    Test fetch_data method when the query fails.
    """
    query = "SELECT * FROM test_table;"
    
    with patch("pandas.read_sql_query", side_effect=Exception("Query error")) as mock_read_sql:
        result = mock_database.fetch_data(query)
        mock_read_sql.assert_called_once_with(query, mock_database.engine)
        assert result is None


def test_fetch_multiple_success(mock_database):
    """
    Test fetch_multiple method when all queries execute successfully.
    """
    queries = [
        "SELECT * FROM table1;",
        "SELECT * FROM table2;"
    ]
    mock_results = [
        pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]}),
        pd.DataFrame({"col1": [3, 4], "col2": ["C", "D"]}),
    ]

    with patch.object(mock_database, "fetch_data", side_effect=mock_results) as mock_fetch_data:
        results = mock_database.fetch_multiple(*queries)
        assert len(results) == 2
        assert results[0].equals(mock_results[0])
        assert results[1].equals(mock_results[1])

def test_close_connection(mock_database):
    """
    Test close_connection method.
    """
    with patch.object(mock_database.engine, "dispose") as mock_dispose:
        mock_database.close_connection()
        mock_dispose.assert_called_once()

