import logging
import pandas as pd
import streamlit as st
from core.db_manager import execute_query
from utils.queries import QUERIES

logger = logging.getLogger("utils.cache_manager")

@st.cache_data
def get_shared_data():
    """
    Fetch and cache data for multiple queries.

    Returns:
        dict: A dictionary containing multiple DataFrames for different queries.
    """
    data = {}
    for key, query in QUERIES.items():
        logger.debug(f"Query Cached: {query}")
        try:
            data[key] = execute_query(query)
        except Exception as e:
            logger.error(f"Error fetching data for {key}: {e}")
            st.error(f"Error fetching data for {key}: {e}")
            data[key] = pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur
    return data
