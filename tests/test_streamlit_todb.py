import sys
import os
import pytest
import pandas as pd
import streamlit as st
from unittest.mock import patch, MagicMock
# to be able to import the module from the src folder
sys.path.insert(0, os.path.abspath(os.path.join
                                   (os.path.dirname(__file__), '../src')
                                   ))
from streamlit_todb import fetch_data_from_db, main


@pytest.fixture
def mock_data():
    return pd.DataFrame({
        'id': [1, 2, 3],
        'dv_calories_%': [10, 20, 30],
        'dv_total_fat_%': [5, 10, 15],
        'dv_sugar_%': [5, 10, 15],
        'dv_sodium_%': [5, 10, 15],
        'dv_protein_%': [5, 10, 15],
        'dv_sat_fat_%': [5, 10, 15],
        'dv_carbs_%': [5, 10, 15],
        'nutriscore': [10, 20, 30],
        'minutes': [30, 60, 90],
        'n_steps': [5, 10, 15],
        'n_ingredients': [5, 10, 15]
    })



@patch('psycopg2.connect')
@patch('pandas.read_sql_query')
def test_fetch_data_from_db(mock_read_sql_query, mock_connect, mock_data):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_read_sql_query.return_value = mock_data

    query1 = "SELECT * FROM table1;"
    query2 = "SELECT * FROM table2;"
    query3 = "SELECT * FROM table3;"
    query4 = "SELECT * FROM table4;"

    configs_db = {
        "db_host": "localhost",
        "db_port": "5432",
        "db_user": "test_user",
        "db_password": "test_password",
        "db_name": "test_database"
    }

    data1, data2, data3, data4 = fetch_data_from_db(
        configs_db,
        query1,
        query2,
        query3,
        query4
    )

    # Assertions
    mock_connect.assert_called_once_with(
        host=configs_db["db_host"],
        port=configs_db["db_port"],
        user=configs_db["db_user"],
        password=configs_db["db_password"],
        dbname=configs_db["db_name"]
    )
    assert mock_read_sql_query.call_count == 4
    pd.testing.assert_frame_equal(data1, mock_data)
    pd.testing.assert_frame_equal(data2, mock_data)
    pd.testing.assert_frame_equal(data3, mock_data)
    pd.testing.assert_frame_equal(data4, mock_data)


@patch('streamlit_todb.fetch_data_from_db')
@patch('builtins.print')
def test_main(mock_print, mock_fetch_data_from_db, mock_data):
    # Mock the fetch_data_from_db function
    mock_fetch_data_from_db.return_value = (mock_data, mock_data, mock_data, None)

    main()

    # Assertions
    assert mock_fetch_data_from_db.call_count == 1
    assert mock_print.call_count == 3
    pd.testing.assert_frame_equal(mock_fetch_data_from_db.return_value[0], mock_data)
    pd.testing.assert_frame_equal(mock_fetch_data_from_db.return_value[1], mock_data)
    pd.testing.assert_frame_equal(mock_fetch_data_from_db.return_value[2], mock_data)
