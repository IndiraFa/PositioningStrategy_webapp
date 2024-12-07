import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from recipe_correlation_analysis import CorrelationAnalysis
from interaction_correlation_analysis import InteractionData, LabelAnalysis
from db.db_instance import db_instance
from db.db_instance import Database
import logging

logger = logging.getLogger("pages.Correlations")
st.set_page_config(layout="centered")

@st.cache_data
def get_cached_data(_db_instance: Database, queries):
    """
    Fetch data from the database and cache the results.

    Args:
        db_instance: Instance of the database connection.
        queries (dict): Dictionary of SQL queries.

    Returns:
        dict: Dictionary of DataFrames containing the fetched data.
    """
    try:
        logger.info("Fetching data from the database")
        results = _db_instance.fetch_multiple(*queries.values())
        logger.info(f"Result: {results}")
        return {key: df for key, df in zip(queries.keys(), results)}
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        st.error("Error while fetching data from the database.")
        return {}

def display_header():
    """
    Display the header of the page.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    logger.debug("Displaying the header of the page")
    st.markdown(
        "<h1 style='color:purple;'>Correlation analysis</h1>",
        unsafe_allow_html=True
    )

    st.write(
            """
            We then explored the linear correlation between :
            - the calculated nutritional
             score and the characteristics of the recipes. 
            - the calculated nutritional score and the interactions of the 
            users (reviews and scores)
            """
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
    logger.debug("Displaying the key takeaways")
    st.markdown("""
        <div class="container_with_border">
            <h3>💡 Key takeaways</h3>
            <p>- This analysis shows some correlations between the nutritional 
                data that are expected and to the chemical composition of each 
                nutrient.</p>
            <br>
            <p>- The correlations between the Nutriscore and the nutritional 
                data are in line with the way the Nutriscore was calculated 
                (as a linear combination of nutritional variables).</p>
            <br>
            <p>- No correlation is seen with the number of ingredients, of 
                steps or the preparation time.</p>
            <br>
            <p>- Finally, no strong correlation were observed with the 
            interactions of the users of the website. Nevertheless, the lowest
                lablest have the best interaction per recipe ratio, and we can 
                conclude that all kinds of recipes are enjoyed, no matter their 
            Nutriscore.</p>
            <p><b>We recommend Mangetamain to keep a variety of recipes on the 
                website, even if they want to promote healthy eating, beacause
                lower nutriscore recipes may drive trafic and interaction.
                </b></p> 
        </div>
        """, unsafe_allow_html=True)


def display_recipe_correlation(filtered_data: pd.DataFrame):
    """
    Display the correlation analysis of the recipes.

    Parameters
    ----------
    filtered_data: DataFrame
        The filtered data.

    Returns
    -------
    None
    """
    logger.debug("Displaying the correlation analysis of the recipes")
    st.write(
        """
        ## 🍜 + ⏳ + 📊
        <h2>Correlation between characterics of recipes and their nutritional 
        score</h2>
        """, 
        unsafe_allow_html=True
    )

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
        "Select the columns to display in the correlation matrix",
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
    logger.debug(
        "Displaying the key takeaways of the recipe correlation analysis"
    )
    st.write("""
        We can see on this heatmap the linear correlations between 
        different characteristics of the recipes:
        <br>
        - There is an <b>expected positive correlation</b> between the 
        number of 
        ingredients (<i>n_ingredients</i>) and the number of steps 
        (<i>n_steps</i>) of the recipe (0.43), but <b>surprisingly no 
        correlation</b> between these variables and the preparation time 
        (<i>minutes</i>).
        <br>
        - The Nutriscore is <b>positively</b> correlated with the percentage of 
        recommanded daily protein intake (<i>dv_protein_%</i>, 0.24), and 
        <b>negatively</b> correlated with the percentage of recommanded daily 
        intake of sugar (<i>dv_sugar_%</i>, -0.36), saturated fat 
        (<i>dv_sat_fat_%</i>, 0.25), sodium (<i>dv_sodium_%</i>, -0.44)and 
             calories per 
        portion(<i>dv_calories_%</i>, -0.11), because of the way the Nutriscore 
        is calculated (see Appendix for the formula)
        - The total fat (<i>dv_total_fat_%</i>) and the saturated fat 
             (<i>dv_sat_fat_%</i>) are also <b>positively</b> correlated 
             (0.69) which is due to the fact that the total fat includes the 
             saturated fat.
         - The <b>same</b> goes for the carbohydrates (<i>dv_carbs_%</i>) and 
             the sugar (<i>dv_sugar_%</i>), which are positively correlated 
             (0.58).
        - A non intuitive strong correlation is the <b>negative</b> correlation
              between the carbohydrates (<i>dv_carbs_%</i>) and the total fat 
             (<i>dv_total_fat_%</i>) (-0.73). 
    """, unsafe_allow_html=True)


def display_interaction_correlation(
        interaction_data: pd.DataFrame, nutriscore_data: pd.DataFrame):
    """
    Display the correlation analysis of the interactions.

    Parameters
    ----------
    interaction_data: DataFrame
        The interaction data.
    nutriscore_data: DataFrame
        The nutriscore data.

    Returns
    ------
    None
    """
    logger.debug("Displaying the correlation analysis of the interactions")
    st.write(
        """
        ## ⭐️⭐️⭐️⭐️⭐️ + 📊
        <h2>Correlation between interactions and nutritional score of the  
        recipes</h2>
        """,
        unsafe_allow_html=True
    )
    st.write(
        """We computed for each recipe the number of reviews 
        (<i>review_count</i>), number of ratings (<i>rating_count</i>) 
        number of interactions (<i>interaction_count = reviews_count + 
        ratings_count</i>), and the average rating (<i>average_rating</i>), 
        along with the Nutriscore.
        """, 
        unsafe_allow_html=True
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
    logger.debug("Merging the interaction data with the nutriscore data")
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
        "Select the columns to display in the correlation matrix",
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
        plt.title('Correlation matrix')
        st.pyplot(plt)

    st.write(
        """
        - There is a perfect linear correlation between the number of reviews, 
        the number of ratings and the number of interactions. This is due to 
        the fact that all recipes that have a rating also have a review and 
        vice versa.
        <br>
        - There is no correlation between the Nutriscore and any of these 
        features.
        """, 
        unsafe_allow_html=True
    )
    logger.debug(
        f"diplaying the label analysis results {label_analysis_result}")
    st.dataframe(label_analysis_result)

    st.write(
        """The average rating is similar for all the labels, but 
        <b>D-labeled recipes have the best interaction/recipe 
        ratio</b>, followed by E-labelled recipes. It represents an <b>increase
        of +27% of interactions/recipe</b> between A-labelled recipes and 
        D-labelled recipes. This is a strong sign that recipes published on the
          website should not be selected solely on their Nutriscore, because 
          <b>users also enjoy recipes with a lower Nutriscore</b>.
        """,
        unsafe_allow_html=True
    )


def main():
    """
    Main function to display the correlation analysis page.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    QUERIES = {
        "filtered_data": """
            SELECT 
                ns.id,
                ns."dv_calories_%%",
                ns."dv_total_fat_%%",
                ns."dv_sugar_%%",
                ns."dv_sodium_%%",
                ns."dv_protein_%%",
                ns."dv_sat_fat_%%",
                ns."dv_carbs_%%",
                ns."nutriscore",
                rr."minutes",
                rr."n_steps",
                rr."n_ingredients"
            FROM "raw_recipes" rr 
            INNER JOIN "NS_noOutliers" ns 
            ON rr.id=ns.id;
        """,
        "raw_interactions": """
            SELECT * FROM "RAW_interactions";
        """,
        "nutriscore": """
            SELECT * FROM "NS_noOutliers";
        """
    }
    logger.info("Starting the correlation analysis page")
    data = get_cached_data(db_instance, QUERIES)

    filtered_data = data.get("filtered_data")
    interaction_data = data.get("raw_interactions")
    nutriscore_data = data.get("nutriscore")
    display_header()
    "---"
    display_recipe_correlation(filtered_data)
    "---"
    display_interaction_correlation(interaction_data, nutriscore_data)
    logger.info("Finished displaying the correlation analysis page")


if __name__ == "__main__":
    main()
