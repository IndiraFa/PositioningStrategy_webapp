import os
import streamlit as st
import plotly.express as px
import pandas as pd
import logging
from core.config_logging import configure_logging
from core.asset_manager import get_asset_path
from db.db_instance import db_instance
from db.db_instance import Database
from nutriscore_analysis import (
    nutriscore_analysis,
    shapiro_test,
    ks_test,
    ad_test,
    skewness,
    kurtosis
)
st.set_page_config(layout="wide")

configure_logging()
logger = logging.getLogger("HomePage")

logger.info("Starting the application")

@st.cache_data
def get_cached_data(_db_instance: Database, query1:str, query2:str):
    """
    Get the data from the database and cache it.

    Parameters
    ----------
    db_instance (Database): Instance of the class Database to perform
    the queries
    query1 (str): SQL query to fetch data with outliers
    query2 (str): SQL query to fetch data without outliers

    Returns
    -------
    data_with_outliers (pd.DataFrame): Data with outliers
    data_no_outliers (pd.DataFrame): Data without outliers
    """
    logger.debug("Fetching data from the database using db_instance")
    try:
        data_with_outliers = db_instance.fetch_data(query1)
        data_no_outliers = db_instance.fetch_data(query2)
        return data_with_outliers, data_no_outliers
    except Exception as e:
        logger.error(f"An error occurred while fetching data: {e}")
        return None, None

def dropna_nutriscore_data(data):
    """
    Drop rows with missing values in the 'nutriscore' column.

    Args:
        data (pd.DataFrame): Data to clean

    Returns:
        pd.DataFrame: Cleaned data without missing 'nutriscore' values
    """
    return data.dropna(subset=['nutriscore'])


def display_header():
    """
    Display the header of the page.

    Returns:
        None
    """
    logger.debug("Displaying the header of the homepage")
    st.markdown(
        "<h1 style='color:purple;'>Positioning strategy for Mangetamain</h1>",
        unsafe_allow_html=True
    )

    st.write(
        """
        Welcome to our Nutrition Score web application!\
              This tool is designed to help 
        Mangetamain explore its potential as a leading \
            healthy food brand by evaluating 
        nutritional quality based on daily value intake recommendations. 
        <br><br>
        Learn more about how the NutriScore is calculated\
              in the **Appendix** section, 
        and find details on our approach to outlier removal\
              in the **Outliers** section.
        """,
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
            <p>The analysis of the Nutriscore shows that Mangetamain already 
                has the potential to build a strong brand around healthy food.
                <br>
                Around 90% of the recipes have a Nutriscore of A, B or C, which
                is a good indicator of the nutritional quality of the recipes 
                of the website.
            </p>
        </div>
        """, unsafe_allow_html=True)


def analyze_data(data_with_outliers: pd.DataFrame,\
                  data_no_outliers: pd.DataFrame):
    """
    Analyze the data and return results on Nutri-Score distribution (mean,
    median, max, min), skewness, and kurtosis.

    Args:
        data_with_outliers (pd.DataFrame): Data with outliers
        data_no_outliers (pd.DataFrame): Data without outliers

    Returns:
        pd.DataFrame: Analysis results
    """
    logger.debug("Analyzing the data")
    nutriscore_with_outliers_mean, nutriscore_with_outliers_median, \
        nutriscore_with_outliers_max, nutriscore_with_outliers_min = \
        nutriscore_analysis(data_with_outliers)
    skewness_with_outliers = skewness(data_with_outliers, 'nutriscore')
    kurtois_with_outliers = kurtosis(data_with_outliers, 'nutriscore')

    nutriscore_no_outliers_mean, nutriscore_no_outliers_median, \
        nutriscore_no_outliers_max, nutriscore_no_outliers_min = \
        nutriscore_analysis(data_no_outliers)
    skewness_no_outliers = skewness(data_no_outliers, 'nutriscore')
    kurtosis_no_outliers = kurtosis(data_no_outliers, 'nutriscore')

    results = pd.DataFrame({
        'Mean': [nutriscore_with_outliers_mean, nutriscore_no_outliers_mean],
        'Median': [
            nutriscore_with_outliers_median,
            nutriscore_no_outliers_median
        ],
        'Max': [nutriscore_with_outliers_max, nutriscore_no_outliers_max],
        'Min': [nutriscore_with_outliers_min, nutriscore_no_outliers_min],
        'Skewness': [skewness_with_outliers, skewness_no_outliers],
        'Kurtosis': [kurtois_with_outliers, kurtosis_no_outliers]
    }, index=['With outliers', 'Without outliers'])
    logger.debug(f"Analysis results: {results}")
    return results


def display_histograms(data_with_outliers: pd.DataFrame,
                        data_no_outliers:pd.DataFrame,
                              results: pd.DataFrame):
    """
    Display histograms of the Nutri-Score distribution.

    Args:
        data_with_outliers (pd.DataFrame): Data with outliers
        data_no_outliers (pd.DataFrame): Data without outliers
        results (pd.DataFrame): Analysis results

    Returns:
        None
    """
    logger.debug("Displaying histograms")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Nutri-Score based on the full dataset")

        bins_with_outliers = st.slider(
            "Select the number of bins", 4, 100, 28, key=1
        )
        fig = px.histogram(
            data_with_outliers,
            x='nutriscore',
            nbins=bins_with_outliers,
            title='Nutri-Score Distribution',
            color_discrete_sequence=['#741B47']
        )
        fig.update_layout(
            xaxis_title='Nutri-Score',
            yaxis_title='Frequency',
            template='plotly_white',
            bargap=0.1,
            xaxis=dict(range=[0, 14]),
            yaxis=dict(range=[0, 45000])
        )
        st.plotly_chart(fig)

        st.divider()

        st.write(results)

    with col2:
        st.subheader("Nutri-Score based on the dataset without outliers")

        bins_no_outliers = st.slider(
            "Select the number of bins", 4, 100, 28, key=2
        )
        fig = px.histogram(
            data_no_outliers,
            x='nutriscore',
            nbins=bins_no_outliers,
            title='Nutri-Score Distribution',
            color_discrete_sequence=['#C27BA0']
        )
        fig.update_layout(
            xaxis_title='Nutri-Score',
            yaxis_title='Frequency',
            template='plotly_white',
            bargap=0.1,
            xaxis=dict(range=[0, 14]),
            yaxis=dict(range=[0, 45000])
        )
        st.plotly_chart(fig)

        st.divider()
        st.write("""
            - The Nutri-Score distribution follows a bell-shaped curve,
                  with minimum and maximum values ranging from 0 to 14. 
            These bounds result from the methodology used to calculate
                  the Nutri-Score.
            <br>
            - The mean and median are approximately 8.5, which is higher
                  than the theoretical average of 7.5, indicating an overall 
            positive shift in Nutri-Score values.
            <br>
            - The distribution is slightly right-skewed (skewness = 0.13),
                  meaning the majority of values are concentrated towards 
            the lower end of the scale.
            <br>
            - The kurtosis value of 2.7 suggests the distribution has heavier
                  tails and a sharper peak compared to a normal distribution.
            <br>
            - When outliers are removed, the mean and median diverge further,
                  while the skewness and kurtosis move closer to 0, 
            indicating a slight adjustment towards a normal distribution.
        """, unsafe_allow_html=True)


    

def display_distribution_analysis(data_with_outliers: pd.DataFrame,
                                   data_no_outliers: pd.DataFrame):
    """
    Display the normality analysis of the Nutri-Score using Shapiro-Wilk, 
    Kolmogorov-Smirnov, and Anderson-Darling tests.

    Args:
        data_with_outliers (pd.DataFrame): Data with outliers.
        data_no_outliers (pd.DataFrame): Data without outliers.

    Returns:
        None
    """
    logger.debug("Displaying distribution analysis")
    st.subheader("Analysis of the Nutri-Score Distribution")

    analysis = st.selectbox(
        "Select the normality test for the Nutri-Score:",
        ["Shapiro-Wilk", "Kolmogorov-Smirnov", "Anderson-Darling"],
        key=3
    )

    if analysis == "Shapiro-Wilk":
        st.write("**Shapiro-Wilk Test**")
        shapiro_with_outliers = shapiro_test(data_with_outliers, 'nutriscore')
        shapiro_no_outliers = shapiro_test(data_no_outliers, 'nutriscore')

        st.write(
            f"Shapiro-Wilk test for the Nutri-Score with outliers: "
            f"{shapiro_with_outliers}"
        )
        st.write(
            f"Shapiro-Wilk test for the Nutri-Score without outliers: "
            f"{shapiro_no_outliers}"
        )

    elif analysis == "Kolmogorov-Smirnov":
        st.write("**Kolmogorov-Smirnov Test**")
        ks_with_outliers = ks_test(data_with_outliers, 'nutriscore')
        ks_no_outliers = ks_test(data_no_outliers, 'nutriscore')

        st.write(
            f"Kolmogorov-Smirnov test for the Nutri-Score with outliers: "
            f"{ks_with_outliers}"
        )
        st.write(
            f"Kolmogorov-Smirnov test for the Nutri-Score without outliers: "
            f"{ks_no_outliers}"
        )

    elif analysis == "Anderson-Darling":
        st.write("**Anderson-Darling Test**")
        ad_with_outliers = ad_test(data_with_outliers, 'nutriscore')
        ad_no_outliers = ad_test(data_no_outliers, 'nutriscore')

        st.write(
            f"Anderson-Darling test for the Nutri-Score with outliers: "
            f"{ad_with_outliers}"
        )
        st.write(
            f"Anderson-Darling test for the Nutri-Score without outliers: "
            f"{ad_no_outliers}"
        )

    st.write(
        "**Summary:** All tests indicate that the Nutri-Score is not normally distributed. "
        "Note: The Shapiro-Wilk test is recommended for sample sizes smaller than 5000."
    )

    st.divider()



def display_label_distribution(
        data_with_outliers: pd.DataFrame, data_no_outliers: pd.DataFrame):
    """
    Display the label distribution of the Nutri-Score.
    
    Parameters
    ----------
    data_with_outliers (pd.DataFrame): Data with outliers
    data_no_outliers (pd.DataFrame): Data without outliers

    Returns
    ---------
    None
    """
    logger.debug("Displaying label distribution")
    st.subheader("Nutri-Score label distribution")

    color_map = {
        'A': '#1c682c',
        'B': '#3cb455',
        'C': '#f1c232',
        'D': '#e69138',
        'E': '#f44336'
    }
    
    col3, col4 = st.columns(2)

    with col3:
        fig = px.pie(
            data_with_outliers,
            names='label',
            title='Nutri-Score Label Distribution with outliers',
            color='label',
            color_discrete_map=color_map
        )

        fig.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig)


    with col4:
        fig = px.pie(
            data_no_outliers,
            names='label',
            title='Nutri-Score Label Distribution without outliers',
            color='label',
            color_discrete_map=color_map
        )

        fig.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig)

    SCALE = "images/scale.png"
    st.image(get_asset_path(SCALE), width=600)

    st.markdown(
        """
        <div style="border: 2px solid #cccccc;
          padding: 15px;
            border-radius: 10px;
              background-color: #f9f9f9;">
            <p style="font-size: 16px; line-height: 1.6; margin: 0;">
            Overall, the recipes show good nutritional quality, 
            with around 90% of label A, B and C. Getting rid of
            the outliers even improved the good to bad nutritional 
            quality ratio, many outliers having a low Nutriscore 
            (see details in the next section).
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    """
    Main function to run the analysis of the Nutri-Score.

    Returns
    ------
    None
    """

    query1 = """
    SELECT * FROM "NS_withOutliers";
    """

    query2 = """
    SELECT * FROM "NS_noOutliers";
    """
    logger.info("Starting displaying Homepage")
    data_with_outliers, data_no_outliers = get_cached_data(
        db_instance,query1,query2,
    )
    display_header()
    "---"
    results = analyze_data(data_with_outliers, data_no_outliers)
    display_histograms(data_with_outliers, data_no_outliers, results)
    display_distribution_analysis(data_with_outliers, data_no_outliers)
    display_label_distribution(data_with_outliers, data_no_outliers)

if __name__ == "__main__":
    try:
        main()
    finally:
        db_instance.close_connection()
