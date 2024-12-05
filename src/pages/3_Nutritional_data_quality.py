import sys
import os
import streamlit as st
import pandas as pd
import logging
import numpy as np
import matplotlib.pyplot as plt
from db.db_instance import db_instance
from db.streamlit_todb import Database
from linear_regression_nutrition import (
    LinearRegressionNutrition,
    calories_per_gram
)
st.set_page_config(layout="centered")

logger = logging.getLogger("pages.Nutritional_data_quality")


@st.cache_data
def get_cached_data(_db_instance: Database, query: str):
    """
    Fetch data from the database and cache it.

    Args:
        db_instance: Instance of the database connection.
        query (str): SQL query to execute.

    Returns:
        pd.DataFrame: Fetched data.
    """
    logger.debug("Fetching data from the database")
    data = _db_instance.fetch_data(query)
    return data


def write_linear_regression_results(coefficients, intercept, mse, r2):
    st.write(coefficients)
    st.write(f"Intercept: {intercept:.2f}")
    st.write(f"Mean Squared Error: {mse:.2f}")
    st.write(f"R^2 Score: {r2:.2f}")


def get_intervals_per_g(
        daily_g_proteins,
        daily_g_fat,
        daily_g_carbs,
        intervals_df
):
    intervals_per_g_df = intervals_df.copy()
    intervals_per_g_df.loc['Calories per gram of Protein'] = (
        intervals_df.loc['protein_%'] * 100 / daily_g_proteins
    )
    intervals_per_g_df.loc['Calories per gram of Fat'] = (
        intervals_df.loc['total_fat_%']*100/daily_g_fat
    )
    intervals_per_g_df.loc['Calories per gram of Carbohydrates'] = (
        intervals_df.loc['carbs_%']*100/daily_g_carbs
    )
    return intervals_per_g_df


def get_values(df):
    nutrients = [
        'Calories per gram of Protein',
        'Calories per gram of Carbohydrates',
        'Calories per gram of Fat'
    ]
    return [df.loc['Value', nutrient] for nutrient in nutrients]


def get_errors(values, intervals_per_g_df):
    nutrients = [
        'Calories per gram of Protein',
        'Calories per gram of Carbohydrates',
        'Calories per gram of Fat']
    return [
        [
            values[i] - intervals_per_g_df.loc[nutrient, 'Lower Bound'],
            intervals_per_g_df.loc[nutrient, 'Upper Bound'] - values[i]
        ] for i,
        nutrient in enumerate(nutrients)
    ]


def plot_confidence_intervals(values_ref, values, nutrient, errors):
    fig, ax = plt.subplots()
    ax.scatter(
        [nutrient], values_ref[0], color='black', label='Reference Value'
    )
    ax.errorbar(
        [nutrient], values[0], yerr=[[errors[0][0]], [errors[1][0]]], 
        fmt='o', capsize=5, capthick=2, ecolor='red', color='blue', 
        label='Calculated Value'
    )
    ax.set_xlabel('Nutrient')
    ax.set_ylabel('Calories per Gram')
    ax.set_title(
        f'{nutrient} Calories per Gram with Confidence Intervals '
        'calculated from the data'
    )
    ax.legend()
    return fig


def display_header():
    st.markdown(
        "<h1 style='color:purple;'>Quality of nutritional data</h1>",
        unsafe_allow_html=True
        )

    st.write("""
            <h2>Nutritional data is essential for the calculation of the 
            Nutri-Score.</h2>
            Values are filled in by the users and can be incorrect.
            We performed a linear regression to estimate the quality of the 
            nutritional data we worked with. The linear regression model was 
            trained on the nutritional values of the recipes (amount of 
             protein, total amount of fat and carbohydrates) and the calories 
             per portion because the linear relationship between them is known. 
             [1] 
            We used the data set without outliers to include the first 
            preprocessing steps.
    """, unsafe_allow_html=True)

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
            <p>This analysis shows that the nutritional data is not always 
                reliable and does not match reference values.
                In order to improve the credibility of the website, Mangetamain 
                could add an automated system to verify the coherence of the 
                nutritional values of a recipe, or even an automated 
                calculation tool.</p>
        </div>
        """, unsafe_allow_html=True)


def display_linear_regression(lr_nutrition):

    st.write("#### Linear regression")

    st.write("""
            The linear regression allows to estimate the parameters b0, 
            b1, b2, b3 of the model where 
            calories = b0 + b1*total_fat_% + b2*protein_% + b3*carbs_% :
            """, unsafe_allow_html=True
            )

    mse, r2, intercept, coefficients, y_test, y_pred = (
        lr_nutrition.linear_regression()
    )

    write_linear_regression_results(coefficients, intercept, mse, r2)

    lr_nutrition.plot_linear_regression(y_test, y_pred)
    st.pyplot(plt)

    st.write("""
            With the linear regression we can calculate the amount of calories 
            per gram of each nutrient **obtained from the data and the model.**
            """,
            unsafe_allow_html=True
            )
    coefficients_per_g = calories_per_gram(coefficients)
    st.write(coefficients_per_g)


def display_confidence_interval_test(lr_nutrition):
    st.write("""
            #### Confidence interval tests
            So, how good is the data ? We performed confidence interval tests, 
            with a parametrable confidence level, using the bootstrap method on 
            the obtained coefficients to check if they are significantly 
            different from the reference values.
            """
            )

    conf_level = st.slider(
        "Select the confidence level, and please be patient 🚧",
        0.6,
        0.99,
        0.9,
        key=1
        )

    confidence_intervals = lr_nutrition.bootstrap_confidence_interval(
        num_bootstrap_samples=500, 
        confidence_level=conf_level
        )
    intervals_df = pd.DataFrame(
        confidence_intervals,
        index=['Lower Bound', 'Upper Bound']
        ).T

    st.write(f"Confidence interval at {conf_level} confidence level")
    # recommended values for a 2000 kcal diet
    intervals_per_g_df = get_intervals_per_g(50, 70, 260, intervals_df)

    st.table(intervals_per_g_df)

    references = {
        'Calories per gram of Protein': [4.06],
        'Calories per gram of Carbohydrates': [4.06],
        'Calories per gram of Fat': [8.84],
    }
    df = pd.DataFrame(references, index=['Value'])

    _, _, _, coefficients, _, _ = (
        lr_nutrition.linear_regression()
    )
    coefficients_per_g = calories_per_gram(coefficients)

    values_ref = get_values(df)
    values = get_values(coefficients_per_g)
    errors = get_errors(values, intervals_per_g_df)
    errors = np.array(errors).T

    fig1 = plot_confidence_intervals(values_ref, values, 'Protein', errors)
    st.pyplot(fig1)

    fig2 = plot_confidence_intervals(
        values_ref, values, 'Carbohydrates', errors
    )
    st.pyplot(fig2)

    fig3 = plot_confidence_intervals(values_ref, values, 'Fat', errors)
    st.pyplot(fig3)

    st.write("""
            The confidence intervals show that the coefficients are 
             significantly different from the reference values, even with the 
             highest confidence level.""",
            unsafe_allow_html=True
            )

    st.write("#### Reference values")

    st.write("""
            [1] Amount of calories per gram of fat, carbohydrate and protein : 
            https://www.nal.usda.gov/programs/fnic#:~:text=Frequently%20Asked%20Questions%20(FAQs),provides%209%20calories%20per%20gram.
            """)

    st.table(df)


def main():
    logger.info("Starting the 3_Nutritional_data_quality")
    query = """
        SELECT 
            ns.id,
            fd.calories,
            fd."total_fat_%%",
            fd."sugar_%%",
            fd."sodium_%%",
            fd."protein_%%",
            fd."sat_fat_%%",
            fd."carbs_%%" 
        FROM "Formatted_data" fd 
        INNER JOIN "NS_noOutliers" ns 
        ON fd.id = ns.id;
    """

    print(type(query))


    # Fetch data from the database using db_instance
    filtered_data = get_cached_data(db_instance, query)

    features = ['total_fat_%', 'protein_%', 'carbs_%']
    target = 'calories'

    logger.info("Doing the linear regression")
    lr_nutrition = LinearRegressionNutrition(
            filtered_data,
            target,
            features
        )
    display_header()
    display_linear_regression(lr_nutrition)
    display_confidence_interval_test(lr_nutrition)



if __name__ == "__main__":
    main()
