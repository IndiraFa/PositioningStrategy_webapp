import streamlit as st
import pandas as pd
import logging
from core.asset_manager import get_asset_path
from db.db_instance import db_instance

logger = logging.getLogger("pages.appendix")


st.set_page_config(layout="centered")


@st.cache_data
def get_cached_data(_db_instance, query):
    """
    Get data from the database using the db_instance object

    Parameters
    ----------
    _db_instance: db_instance
        The database instance object

    query: str
        The query to fetch the data from the database

    Returns
    -------
    pd.DataFrame
        The data fetched from the database
    """
    logger.debug("Fetching data from the database using db_instance")
    try:
        return db_instance.fetch_data(query)
    except Exception as e:
        logger.error(f"An error occurred while fetching data: {e}")
        return None


def display_header():
    """
    Display the header of the page, with the title "Appendix"

    Returns
    -------
    None
    """
    st.markdown(
        "<h1 style='color:purple;'>Appendix</h1>",
        unsafe_allow_html=True
    )
    logger.debug("Header displayed")


def display_nutriscore_description():
    """
    Display the description of the Nutriscore calculation

    Returns
    -------
    None
    """
    st.write(
        """
        ## Nutriscore calculation
        We built a Nutrition Score based on **daily value intake
        recommandations** 
        (ref) and on available data from the recipes.<br>
        Starting from the **maximum value of 14**, the Nutri-Score decreases as
         the nutritional quality of the recipe decreases.<br>
        The **% of calories** that represents a recipe is based on the declared
         number of calories **per portion**.
        The **other nutrients** were **normalized by the daily intake 
        recommandations** (as if the recipe represented the full 2000 kcal 
        per day).
        In order to have a good Nutriscore, the recipe should have the 
        following characteristics:<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- a reasonable amount of calories per 
            portion (a portion should not exceed 37% of the daily intake of 
            2000 calories)
            <br>
            &nbsp;&nbsp;&nbsp;&nbsp;- a low amount of sugar<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- a low amount of saturated fat<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- a low amount of sodium<br>
            &nbsp;&nbsp;&nbsp;&nbsp;- enough protein<br>
        """,
        unsafe_allow_html=True,
    )
    logger.debug("Nutriscore description displayed")


def display_nutriscore_grid():
    """
    Display a text description of the Nutriscore calculation grid then display
    the grid itself and the letter grade scale.

    Returns
    -------
    None
    """
    csv_file_path = get_asset_path("data/nutrient_table.csv")
    df = pd.read_csv(csv_file_path)

    st.write("### Nutriscore calculation grid")
    st.write(
        """
        The Nutriscore is calculated as follows based on the grid below:<br>
        for each nutrient category, if the value is below the first line, no 
        point is substracted. If the value is between the first and the second 
        line, 1 point is substracted. If the value is between the second and 
        the third line, 1.25 points are substracted, etc. For each nutrient 
        category, there is a maximum value after which no extra point is 
        substracted.
        For proteins, we look at minus the value.
        """,
        unsafe_allow_html=True,
    )
    logger.debug("Nutriscore description displayed")
    st.dataframe(df)
    logger.debug("Nutriscore grid displayed")
    st.write(
        """
        For an easier interpretation, the Nutriscore is then converted into a 
        letter grade from A to E, with A being the best grade and E the worst 
        grade.
        """
    )
    st.image(get_asset_path("images/scale.png"))
    logger.debug("Nutriscore letter grade scale displayed")


def display_example_calculation(df2: pd.DataFrame):
    """
    Display an example of the Nutriscore calculation for a specific recipe.

    Parameters
    ----------
    df2: pd.DataFrame
        The DataFrame containing the nutritional values of the recipe

    Returns
    -------
    None
    """
    st.write("### Example of Nutriscore calculation")
    st.write(
        """
        This is an example of the calculation of the Nutriscore for the recipe 
        of the Creamy chicken curry with the following nutritional values:
        """
    )
    logger.debug("Example of Nutriscore calculation displayed")
    recipe_id = 137434  
    specific_row = df2.loc[df2["id"] == recipe_id]
    st.dataframe(specific_row)
    logger.debug(f"Nutritional values displayed : {specific_row}")
    st.write(
        """
        **Calculation**: Nutriscore = 14 - 0 (calories) - 0 (saturated fat) - 
        2 (sugar) - 1 (sodium) - 0 (protein) = **11**<br>
        **The label of the Nutriscore is B.**
        """,
        unsafe_allow_html=True,
    )
    logger.debug("Example of Nutriscore calculation displayed")


def display_references():
    """
    Display the references used for the Nutriscore calculation

    Returns
    -------
    None
    """
    st.write(
        """
        ### References

        [1] Method for calculating the official Nutriscore in France :
        https://docs.becpg.fr/fr/utilization/score5C.html<br>
        [2] Daily recommendations for the main nutrients :
        https://eur-lex.europa.eu/legal-content/FR/TXT/PDF/?uri=CELEX:02011R1169-20180101<br>
        """,
        unsafe_allow_html=True,
    )
    logger.debug("References displayed")


def main():
    """
    Main function to display the appendix of the project

    Returns
    -------
    None
    """
    logger.info("Openning Appendix")
    query = 'SELECT * FROM "NS_withOutliers"'
    data_with_outliers = get_cached_data(db_instance, query)

    display_header()
    display_nutriscore_description()
    display_nutriscore_grid()
    display_example_calculation(data_with_outliers)
    display_references()
    logger.info("Appendix page fully displayed")


if __name__ == "__main__":
    main()
