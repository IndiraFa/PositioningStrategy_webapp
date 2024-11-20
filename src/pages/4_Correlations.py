import streamlit as st
import pandas as pd
import sys
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import psycopg2

from recipe_correlation_analysis import correlation_matrix
from interaction_correlation_analysis import (
    interactions_df, 
    interactions_and_nutriscore_df,
    label_analysis
)

st.set_page_config(layout="centered")

# allows to import packages from the parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from utils.config_logging import configure_logging
# logger = configure_logging()


try:
    db_host = st.secrets["connections"]["postgresql"]["host"]
    db_port = st.secrets["connections"]["postgresql"]["port"]
    db_user = st.secrets["connections"]["postgresql"]["username"]
    db_password = st.secrets["connections"]["postgresql"]["password"]
    db_name = st.secrets["connections"]["postgresql"]["database"]

    # logger.info("Connecting to the database ...")

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        dbname=db_name
    )

    # logger.info("Successfully connected to the database")

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

    filtered_data = pd.read_sql_query(query1, conn)
    interaction_data = pd.read_sql_query(query2, conn)
    nutriscore_data = pd.read_sql_query(query3, conn)

    # logger.info("Successfully read the data from the database")

    conn.close()
    # logger.info("Connection to the database closed")

except Exception as e:
    # logger.error(f"An error occurred: {e}")
    st.error("An error occurred while connecting to the database")

result = interactions_df(interaction_data)
merged_data = interactions_and_nutriscore_df(result, nutriscore_data)
label_analysis_result = label_analysis(merged_data)


st.markdown(
    "<h1 style='color:purple;'>Correlation analysis</h1>",
    unsafe_allow_html=True
)

css_styles = """
    <style>
    .container_with_border {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: calc(1em - 1px);
        background-color: #f3e5f5;
    }
    .container_with_border h3 {
        color: purple;
    }
    .container_with_border p {
        color: black;
    }
    </style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

st.markdown("""
    <div class="container_with_border">
        <h3>💡 Key takeaways</h3>
        <p>xxxxxx.</p>
    </div>
    """, unsafe_allow_html=True)


"---"

st.write(
    """
    ## 🍜 + ⏳ + 📊
    ## Correlation between characterics of recipes and their nutritional score 
    """
)

st.write("""
         We analyzed xxxxxx
""", unsafe_allow_html=True)


columns_of_interest = [
    'dv_calories_%',
    'dv_total_fat_%',
    'dv_sugar_%',
    'dv_sodium_%',
    'dv_protein_%',
    'dv_sat_fat_%',
    'dv_carbs_%',
    'nutriscore',
    'minutes',
    'n_steps',
    'n_ingredients'
] 

# Sélectionner les colonnes pour la matrice de corrélation
selected_columns = st.multiselect(
    "Select columns for correlation matrix",
    columns_of_interest,
    default=columns_of_interest
)

# Calculer la matrice de corrélation pour les colonnes sélectionnées
if selected_columns:
    matrix = correlation_matrix(filtered_data, selected_columns)

    # Créer la heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Matrice de corrélation')

    # Afficher la heatmap dans Streamlit
    st.pyplot(plt)
else:
    st.write("Please select at least one column.")

"---"
st.write(
    """
    ## ⭐️⭐️⭐️⭐️⭐️ + 📊
    ## Correlation between interactions and nutritional score  of the recipes.
    """
)
st.write(
    """We computed for each recipe the number of interactions 
         (reviews + ratings), number of reviews, number of ratings and the 
         average rating, along with the Nutriscore.
    """
)

# st.dataframe(merged_data)

columns_of_interest = [
    'interaction_count',
    'review_count',
    'rating_count',
    'average_rating',
    'nutriscore'
]

selected_columns_2 = st.multiselect(
    "Select columns for correlation matrix",
    columns_of_interest,
    default=[
        'review_count',
        'rating_count',
        'average_rating',
        'nutriscore'
    ]
)

if selected_columns_2:
    matrix = correlation_matrix(merged_data, selected_columns_2)

    plt.figure(figsize=(12, 8))
    sns.heatmap(matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Matrice de corrélation')
    st.pyplot(plt)
else:
    st.write("Please select at least one column.")

st.dataframe(label_analysis_result)

st.write(
    """D-labeled recipes have the best average rating (followed closely by 
    C and B-labelled recipes). They also have the best interaction/recipe 
    ratio, followed by E-labelled recipes. Although these varaitions are only 
    by XXXXX% this is a sign that recipes published on the website should 
    not be selected solely on their Nutriscore, because users also enjoy 
    recipes with a lower Nutriscore.
    """
)
