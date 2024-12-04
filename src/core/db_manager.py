from core.config import DB_CONFIG
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st


logger = logging.getLogger("core.db_manager")

@st.cache_resource
def get_db_engine():
    """
    Create a cached SQLAlchemy engine.

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    db_url = (
        f"postgresql://{DB_CONFIG['db_user']}:{DB_CONFIG['db_password']}@"
        f"{DB_CONFIG['db_host']}:{DB_CONFIG['db_port']}/{DB_CONFIG['db_name']}"
    )
    logger.debug(f"Connexion Url: {db_url}")
    return create_engine(db_url)


@st.cache_data
def execute_query(query):
    """
    Execute a SQL query and cache the results.

    Args:
        query (str): SQL query to execute.

    Returns:
        DataFrame: Results of the query.
    """
    engine = get_db_engine()  # Utilise le moteur de connexion global
    try:
        with engine.connect() as connection:
            logger.debug(f"Query executed: {query}")
            result = pd.read_sql(query, connection)
            logger.debug(f"Result of query: {result}")
        return result
    except SQLAlchemyError as e:
        logger.error(f"An error occurred while executing the query: {e}")
        st.error(f"An error occurred while executing the query: {e}")
        return None