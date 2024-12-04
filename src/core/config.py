import streamlit as st

# Database configuration using Streamlit secrets
DB_CONFIG = {
    "db_host": st.secrets["connections"]["postgresql"]["host"],
    "db_port": st.secrets["connections"]["postgresql"]["port"],
    "db_user": st.secrets["connections"]["postgresql"]["username"],
    "db_password": st.secrets["connections"]["postgresql"]["password"],
    "db_name": st.secrets["connections"]["postgresql"]["database"]
}