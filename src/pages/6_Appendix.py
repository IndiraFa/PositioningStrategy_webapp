import os
import sys
import streamlit as st
import pandas as pd
import logging
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
from streamlit_todb import fetch_data_from_db, configs_db


st.set_page_config(layout="centered")

logger = logging.getLogger("app.pages.6_Appendix.log")


@st.cache_data
def get_cached_data(configs_db, query):
    return fetch_data_from_db(configs_db, query)


def display_header():
    st.markdown(
        "<h1 style='color:purple;'>Appendix</h1>",
        unsafe_allow_html=True
    )


def display_nutriscore_description():
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


def display_nutriscore_grid():
    current_dir = os.path.dirname(__file__)
    csv_file_path = os.path.join(current_dir, "..", "nutrient_table.csv")
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
    st.dataframe(df)
    st.write(
        """
        For an easier interpretation, the Nutriscore is then converted into a 
        letter grade from A to E, with A being the best grade and E the worst 
        grade.
        """
    )
    st.image(os.path.join(current_dir, "..", "scale.png"))


def display_example_calculation(df2):
    st.write("### Example of Nutriscore calculation")
    st.write(
        """
        This is an example of the calculation of the Nutriscore for the recipe 
        of the Creamy chicken curry with the following nutritional values:
        """
    )

    recipe_id = 137434  
    specific_row = df2.loc[df2["id"] == recipe_id]
    st.dataframe(specific_row)
    st.write(
        """
        **Calculation**: Nutriscore = 14 - 0 (calories) - 0 (saturated fat) - 
        2 (sugar) - 1 (sodium) - 0 (protein) = **11**<br>
        **The label of the Nutriscore is B.**
        """,
        unsafe_allow_html=True,
    )


def display_references():
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


def main():
    logger.info("Starting the 6_Appendix.py script")

    query = 'SELECT * FROM "NS_withOutliers"'

    df2, _, _, _, _, _ = get_cached_data(configs_db, query)

    display_header()
    display_nutriscore_description()
    display_nutriscore_grid()
    display_example_calculation(df2)
    display_references()


if __name__ == "__main__":
    main()
