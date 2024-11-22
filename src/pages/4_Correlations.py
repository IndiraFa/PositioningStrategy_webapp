import streamlit as st
import sys
import os
import seaborn as sns
import matplotlib.pyplot as plt
from recipe_correlation_analysis import CorrelationAnalysis
from interaction_correlation_analysis import InteractionData, LabelAnalysis
from streamlit_todb import fetch_data_from_db, configs_db

st.set_page_config(layout="centered")

# SQL queries
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


def display_header():
    """
    Display the header of the page.

    Returns:
    - None
    """
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


def display_recipe_correlation(filtered_data):
    """
    Display the correlation analysis of the recipes.

    Parameters:
    - filtered_data: DataFrame, the filtered data.

    Returns:
    - None
    """
    st.write(
        """
        ## 🍜 + ⏳ + 📊
        ## Correlation between characterics of recipes and their nutritional 
        ## score 
        """
    )

    st.write("""
             We analyzed xxxxxx
    """, unsafe_allow_html=True)

    columns_to_keep_recipe = [
        'id',
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

    columns_of_interest_recipe = [
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
    selected_columns = st.multiselect(
        "Select columns for correlation matrix",
        columns_of_interest_recipe,
        default=columns_of_interest_recipe
    )

    correlation_analysis = CorrelationAnalysis(
        columns_to_keep_recipe,
        selected_columns,
        data=filtered_data
    )

    if selected_columns:
        plt.figure(figsize=(12, 8))
        corr_matrix = correlation_analysis.correlation_matrix()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Matrice de corrélation')
        st.pyplot(plt)
    else:
        st.write("Please select at least one column.")


def display_interaction_correlation(interaction_data, nutriscore_data):
    """
    Display the correlation analysis of the interactions.

    Parameters:
    - interaction_data: DataFrame, the interaction data.
    - nutriscore_data: DataFrame, the nutriscore data.

    Returns:
    - None
    """
    st.write(
        """
        ## ⭐️⭐️⭐️⭐️⭐️ + 📊
        ## Correlation between interactions and nutritional score of the 
        ## recipes.
        """
    )
    st.write(
        """We computed for each recipe the number of interactions 
             (reviews + ratings), number of reviews, number of ratings and the 
             average rating, along with the Nutriscore.
        """
    )
    int_data = InteractionData(data=interaction_data)
    label_analysis = LabelAnalysis()

    columns_to_keep_interaction = [
        'id',
        'interaction_count',
        'review_count',
        'rating_count',
        'average_rating',
        'nutriscore',
        'label'
    ]
    # interaction_df = int_data.interactions_df()
    merged_data = int_data.merge_interaction_nutriscore(
        nutriscore_data,
        columns_to_keep_interaction
    )
    label_analysis_result = label_analysis.label_analysis(merged_data)

    columns_of_interest_interaction = [
        'interaction_count',
        'review_count',
        'rating_count',
        'average_rating',
        'nutriscore'
    ]

    selected_columns_2 = st.multiselect(
        "Select columns for correlation matrix",
        columns_of_interest_interaction,
        default=[
            'review_count',
            'rating_count',
            'average_rating',
            'nutriscore'
        ]
    )

    if selected_columns_2:
        matrix = int_data.interaction_correlation_matrix(
            merged_data,
            selected_columns_2
        )
        plt.figure(figsize=(12, 8))
        sns.heatmap(matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Matrice de corrélation')
        st.pyplot(plt)

    st.dataframe(label_analysis_result)

    st.write(
        """D-labeled recipes have the best average rating (followed closely by 
        C and B-labelled recipes). They also have the best interaction/recipe 
        ratio, followed by E-labelled recipes. Although these varaitions are 
        only by XXXXX% this is a sign that recipes published on the website 
        should not be selected solely on their Nutriscore, because users also
        enjoy recipes with a lower Nutriscore.
        """
    )


def main():
    filtered_data, interaction_data, nutriscore_data, _ = fetch_data_from_db(
        configs_db,
        query1,
        query2,
        query3
    )
    display_header()
    "---"
    display_recipe_correlation(filtered_data)
    "---"
    display_interaction_correlation(interaction_data, nutriscore_data)


if __name__ == "__main__":
    main()
