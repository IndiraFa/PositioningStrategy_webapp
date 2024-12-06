import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import logging

logger = logging.getLogger("db.streamlit_todb")

class Database:
    def __init__(self):
        """
        Initialize a database connection using SQLAlchemy.
        Configurations are retrieved from Streamlit secrets.
        """
        configs = {
            "db_host": st.secrets["connections"]["postgresql"]["host"],
            "db_port": st.secrets["connections"]["postgresql"]["port"],
            "db_user": st.secrets["connections"]["postgresql"]["username"],
            "db_password": st.secrets["connections"]["postgresql"]["password"],
            "db_name": st.secrets["connections"]["postgresql"]["database"]
        }
        self.engine = create_engine(
            f"postgresql://{configs['db_user']}:{configs['db_password']}@"
            f"{configs['db_host']}:{configs['db_port']}/{configs['db_name']}"
        )
        logger.info("Database connection initialized")

    def fetch_data(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the results in a DataFrame.

        Parameters:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The query results as a DataFrame, or None if an error occurs.
        """
        try:
            logger.debug(f"Executing query: {query}")
            data = pd.read_sql_query(query, self.engine)
            logger.info(f"Query executed successfully: {query}")
            return data
        except Exception as e:
            logger.error(f"An error occurred while executing the query: {e}")
            return None

    def fetch_multiple(self, *queries: str) -> tuple:
        """
        Execute multiple SQL queries and return their results.

        Parameters:
            *queries (str): A variable number of SQL queries to execute.

        Returns:
            tuple: A tuple of DataFrames for each query (None for any query that fails).
        """
        results = []
        for query in queries:
            if query:
                logger.debug(f"Executing query: {query}")
                df = self.fetch_data(query)
                if isinstance(df, pd.DataFrame):
                    results.append(df)
                else:
                    logger.error(f"Query failed: {query}")
                    results.append(None)
            else:
                results.append(None)
        return tuple(results)

    def close_connection(self) -> None:
        """
        Close the database connection.
        """
        self.engine.dispose()
        logger.debug("Database connection closed.")
