import streamlit as st
import pandas as pd
import sys
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from recipe_correlation_analysis import correlation_matrix
from recipe_correlation_analysis import filtered_data
from interaction_correlation_analysis import merged_data, label_analysis_result

st.set_page_config(layout="centered")

#allows to import packages from the parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.markdown(
    "<h1 style='color:purple;'>Correlation analysis</h1>",
    unsafe_allow_html=True
)

# ajouter la conclusion de l'analyse de corrélation : pour améliorer la 
# crédibilité du site, mettre en place un système de vérification des données 
# nutritionnelles ou de calcul automatisé. 
st.write(
    """
    ## Correlation between characterics of recipes and their nutritional score
    """
)

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


st.write(
    """
    ## Correlation between interactions and nutritional score of the recipes.
         We computed for each recipe the number of interactions 
         (reviews + ratings), number of reviews, number of ratings and the 
         average rating, along with the Nutriscore.
         """
)

st.dataframe(merged_data)

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
    default=columns_of_interest
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
