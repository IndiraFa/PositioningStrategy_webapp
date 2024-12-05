import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import logging

logger = logging.getLogger("db.streamlit_todb")

class Database:
    def __init__(self):
        """
        Initialise une instance de connexion à la base de données en utilisant SQLAlchemy.
        Les configurations sont récupérées depuis les secrets Streamlit.
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

    def fetch_data(self, query):
        """
        Exécute une requête SQL et retourne les résultats dans un DataFrame.

        Parameters:
        - query: str, la requête SQL

        Returns:
        - pd.DataFrame: Les résultats de la requête ou None en cas d'erreur.
        """
        try:
            logger.debug(f"Executing query: {query}")
            data = pd.read_sql_query(query, self.engine)
            logger.info(f"Result: {data}")
            return data
        except Exception as e:
            logger.debug(f"An error occurred while executing the query: {e}")
            # st.error(f"An error occurred while executing the query: {e}")
            return None

    def fetch_multiple(self, *queries):
        """
        Exécute plusieurs requêtes SQL et retourne leurs résultats.

        Parameters:
        - *queries: liste des requêtes SQL à exécuter

        Returns:
        - tuple: Les DataFrames résultants pour chaque requête (None si une requête échoue).
        """
        results = []
        for query in queries:
            if query:
                logger.debug(f"Executing query: {query}")
                df = self.fetch_data(query)
                if isinstance(df, pd.DataFrame):
                    results.append(df)
                else:
                    logger.error(f"Query failed, did not return a DataFrame: {query}")
                    results.append(None)
            else:
                results.append(None)
        return tuple(results)

    def close_connection(self):
        """
        Ferme la connexion à la base de données.
        """
        self.engine.dispose()
        logger.debug("Database connection closed.")
