import psycopg2
import pandas as pd
import streamlit as st

configs_db = {
    "db_host": st.secrets["connections"]["postgresql"]["host"],
    "db_port": st.secrets["connections"]["postgresql"]["port"],
    "db_user": st.secrets["connections"]["postgresql"]["username"],
    "db_password": st.secrets["connections"]["postgresql"]["password"],
    "db_name": st.secrets["connections"]["postgresql"]["database"]
}

def fetch_data_from_db(configs_db,
                       query1=None,
                       query2=None,
                       query3=None, query4=None
):
    """
    Connect to the database, execute queries, and fetch data into DataFrames.

    Parameters:
    - configs_db: dict, the database configurations
    - query1: str, optional, the first SQL query
    - query2: str, optional, the second SQL query
    - query3: str, optional, the third SQL query
    - query4: str, optional, the fourth SQL query
    Returns:
    - data1: DataFrame, the result of the first query (or None if not provided)
    - data2: DataFrame, the result of the second query (or None if not 
    provided)
    - data3: DataFrame, the result of the third query (or None if not provided)
    - data4: DataFrame, the result of the fourth query (or None if not 
    provided)
    """
    try:
        conn = psycopg2.connect(
            host=configs_db["db_host"],
            port=configs_db["db_port"],
            user=configs_db["db_user"],
            password=configs_db["db_password"],
            dbname=configs_db["db_name"]
        )

        # logger.info("Successfully connected to the database")

        data1 = pd.read_sql_query(query1, conn) if query1 else None
        data2 = pd.read_sql_query(query2, conn) if query2 else None
        data3 = pd.read_sql_query(query3, conn) if query3 else None
        data4 = pd.read_sql_query(query4, conn) if query4 else None

        # logger.info("Successfully read the data from the database")

        conn.close()
        # logger.info("Connection to the database closed")

        return data1, data2, data3, data4

    except Exception as e:
        # logger.error(f"An error occurred: {e}")
        st.error("An error occurred while connecting to the database")
        return None, None, None, None
    
def fetch_data_from_db_v2(query):
    """
    Connect to the database, execute a query, and fetch data into a DataFrame.

    Parameters:
    - configs_db: dict, the database configurations
    - query: str, the SQL query

    Returns:
    - data: DataFrame, the result of the query
    """
    try:
        conn = psycopg2.connect(
            host=configs_db["db_host"],
            port=configs_db["db_port"],
            user=configs_db["db_user"],
            password=configs_db["db_password"],
            dbname=configs_db["db_name"]
        )

        data = pd.read_sql_query(query, conn)

        conn.close()
        return data

    except Exception as e:
        st.error("An error occurred while connecting to the database")
        return None
def main():
    query1 = """
    SELECT 
        ns.id,
        ns."dv_calories_%",
        ns."dv_total_fat_%",
        ns."dv_sugar_%",
        ns."dv_sodium_%",
        ns."dv_protein_%",
        ns."dv_sat_fat_%",
        ns."dv_carbs_%",
        ns."nutriscore",
        rr."minutes",
        rr."n_steps",
        rr."n_ingredients"
    FROM "raw_recipes" rr 
    INNER JOIN "NS_noOutliers" ns 
    ON rr.id=ns.id;"""

    query2 = """
    SELECT * FROM "RAW_interactions";
    """

    query3 = """
    SELECT * FROM "NS_noOutliers";
    """

    data1, data2, data3, _ = fetch_data_from_db(
        configs_db,
        query1,
        query2,
        query3
    )

    if data1 is not None:
        print(data1.head())
    if data2 is not None:
        print(data2.head())
    if data3 is not None:
        print(data3.head())

if __name__ == '__main__':
    main()
