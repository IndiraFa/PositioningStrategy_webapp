import pandas as pd
import streamlit as st
from core.db_manager import execute_query
from utils.queries import *
import logging

logger = logging.getLogger("utils.cache_manager")

@st.cache_data
def get_data_outliers():
    """
    Fetch and cache data globally.

    Returns:
        tuple: Two Pandas DataFrames (data_with_outliers, data_no_outliers).
    """
    try:
        data_with_outliers = execute_query(query_with_outliers)
        data_no_outliers = execute_query(query_no_outliers)
        return data_with_outliers, data_no_outliers
    except Exception as e:
        logger.error(f"An error occurred while fetching data: {e}")
        st.error(f"An error occurred while fetching data: {e}")
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data
def get_data_rawOutliers():

    try:
        raw_interactions = execute_query(query_raw_interaction)
        return raw_interactions
    except Exception as e:
        logger.error(f"An error occurred while fetching data: {e}")
        st.error(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()


@st.cache_data
def get_filtered_data():
    """_summary_

    Returns:
        _type_: _description_
    """
    try:
        filtered_data = execute_query(query_filtered_data)
        return filtered_data
    except Exception as e:
        logger.error(f"An error occurred while fetching data: {e}")
        st.error(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()
