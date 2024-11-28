import os
import sys
import streamlit as st
import plotly.express as px
import pandas as pd
import logging
from streamlit_todb import fetch_data_from_db, configs_db
from nutriscore_analysis import (
    nutriscore_analysis,
    shapiro_test,
    ks_test,
    ad_test,
    skewness,
    kurtosis
)

st.set_page_config(layout="wide")

logger = logging.getLogger("app.Homepage")

# SQL queries

query1 = """
SELECT * FROM "NS_withOutliers";
"""

query2 = """
SELECT * FROM "NS_noOutliers";
"""


@st.cache_data
def get_cached_data(configs_db, query1, query2):
    """
    Get the data from the database and cache it.

    Args:
    - configs_db (dict): Database configuration
    - query1 (str): SQL query to fetch data with outliers
    - query2 (str): SQL query to fetch data without outliers

    Returns:
    - data_with_outliers (pd.DataFrame): Data with outliers
    - data_no_outliers (pd.DataFrame): Data without outliers
    """
    logger.info("Fetching data from the database")
    return fetch_data_from_db(configs_db, query1, query2)


def dropna_nutriscore_data(data):
    """
    Drop the rows with missing values in the 'nutriscore' column.
    
    Args:
    - data (pd.DataFrame): Data to clean

    Returns:
    - data_nona (pd.DataFrame): Data without missing values in 
    the 'nutriscore' column
    """
    data_nona = data.dropna(subset=['nutriscore'])
    return data_nona


def display_header():
    """
    Display the header of the page.

    Returns:
    - None
    """
    logger.info("Displaying the header of the homepage")
    st.markdown(
        "<h1 style='color:purple;'>Positioning strategy for Mangetamain</h1>",
        unsafe_allow_html=True
    )

    st.write(
            """
            We built a Nutrition Score based on daily value intake 
            recommendations to explore for Mangetamain the opportunity to 
            position itself as a healthy food brand. 
            <br>
            The method of calculation of the Nutriscore is described 
            in the **Appendix** section. Details on the outliers removal
            are available in the **Outliers** section.
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
                of the website
            </p>
        </div>
        """, unsafe_allow_html=True)


def analyze_data(data_with_outliers, data_no_outliers):
    """
    Analyze the data and return results on the Nutri-Score distribution (mean,
    median, max, min), skewness and kurtosis.

    Args:
    - data_with_outliers (pd.DataFrame): Data with outliers
    - data_no_outliers (pd.DataFrame): Data without outliers

    Returns:
    - results (pd.DataFrame): Analysis
    
    """
    logger.info("Analyzing the data")
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


def display_histograms(data_with_outliers, data_no_outliers, results):
    """
    Display histograms of the Nutri-Score distribution.

    Args:
    - data_with_outliers (pd.DataFrame): Data with outliers
    - data_no_outliers (pd.DataFrame): Data without outliers
    - results (pd.DataFrame): Analysis results

    Returns:
    - None
    """
    logger.info("Displaying histograms")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Nutri-Score based on the full data set")

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
        st.subheader("Nutri-Score based on the data set without outliers")

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
                 - The distribution of the Nutri-Score is bell-shaped, with min 
                 and max values between 0 and 14 as a consequence of the method
                    used to calculate the Nutri-Score. 
                 <br>
                 - The mean and median are around 8.5, which is better than the 
                 theoretical average value of 7.5 for the calculated
                 Nutriscore.
                 <br>
                 - The distribution is slightly right-skewed (skewness = 0.13) 
                 which is characteristic of a distribution with a mass 
                 concentrated on the left side. 
                <br>
                 - The kurtosis is 2.7, which indicates that
                    the distribution has heavier tails and a sharper peak than a
                    normal distribution. 
                 <br>
                 - Without outliers, the mean and median are further apart. 
                 The skewness and kurtosis are closer to 0, which indicates
                 a slight adustment towards the normal distrubution.""",
                 unsafe_allow_html=True
        )
        st.divider()
    

def display_distribution_analysis(data_with_outliers, data_no_outliers):
    """
    Display the normal distribution analysis of the Nutri-Score : Shapiro-Wilk,
    Kolmogorov-Smirnov and Anderson-Darling tests.

    Args:
    - data_with_outliers (pd.DataFrame): Data with outliers
    - data_no_outliers (pd.DataFrame): Data without outliers

    Returns:
    - None
    """
    logger.info("Displaying distribution analysis")
    st.subheader("Analysis of the Nutri-Score distribution")

    analysis = st.selectbox(
        "Select the test for a normal distribution of the Nutriscore",
        ["Shapiro-Wilk", "Kolmogorov-Smirnov", "Anderson-Darling"],
        key=3
    )

    if analysis == "Shapiro-Wilk":
        st.write("**Shapiro-Wilk test**")

        shapiro_test_with_outliers = shapiro_test(
            data_with_outliers,
            'nutriscore'
        )
        st.write(
            f"The Shapiro-Wilk test for the Nutri-Score with outliers is "
            f"{shapiro_test_with_outliers}"
        )

        shapiro_test_no_outliers = shapiro_test(data_no_outliers, 'nutriscore')
        st.write(
            f"The Shapiro-Wilk test for the Nutri-Score without outliers is "
            f"{shapiro_test_no_outliers}"
        )
    
    elif analysis == "Kolmogorov-Smirnov":
        st.write("**Kolmogorov-Smirnov test**")

        ks_test_with_outliers = ks_test(data_with_outliers, 'nutriscore')
        st.write(
            f"The Kolmogorov-Smirnov test for the Nutri-Score \
                with outliers is "
            f"{ks_test_with_outliers}"
        )

        ks_test_no_outliers = ks_test(data_no_outliers, 'nutriscore')
        st.write(
            f"The Kolmogorov-Smirnov test for the Nutri-Score without \
                outliers is "
            f"{ks_test_no_outliers}"
        )

    elif analysis == "Anderson-Darling":
        st.write("**Anderson-Darling test**")

        ad_test_with_outliers = ad_test(data_with_outliers, 'nutriscore')
        st.write(
            f"The Anderson-Darling test for the Nutri-Score with outliers is "
            f"{ad_test_with_outliers}"
        )

        ad_test_no_outliers = ad_test(data_no_outliers, 'nutriscore')
        st.write(
            f"The Anderson-Darling test for the Nutri-Score without \
                outliers is "
            f"{ad_test_no_outliers}"
        )

    st.write(
        "**All tests show that the Nutri-Score is not normally distributed.** "
        "(NB : the Shapiro-Wilk test is more accurate for N<5000)"
    )

    st.divider()


def display_label_distribution(data_with_outliers, data_no_outliers):
    """
    Display the label distribution of the Nutri-Score.
    
    Args:
    - data_with_outliers (pd.DataFrame): Data with outliers
    - data_no_outliers (pd.DataFrame): Data without outliers

    Returns:
    - None
    """
    logger.info("Displaying label distribution")
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
        st.image(os.path.join(current_dir,"scale.png"), width=600)

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

        st.write(
            """
            Overall, the recipes show good nutritional quality, 
            with around 90% of label A, B and C. Getting rid of
              the outliers even improved the good to bad nutritional 
              quality ratio, many outliers having a low Nutriscore 
              (see details in the next section).
            """
        )


def main():
    """
    Main function to run the analysis of the Nutri-Score.

    Returns:
    - None
    """
    logger.info("Starting main function")
    data_with_outliers, data_no_outliers, _, _, _, _ = \
        get_cached_data(
            configs_db,
            query1,
            query2,
        )
    display_header()
    "---"
    results = analyze_data(data_with_outliers, data_no_outliers)
    display_histograms(data_with_outliers, data_no_outliers, results)
    display_distribution_analysis(data_with_outliers, data_no_outliers)
    display_label_distribution(data_with_outliers, data_no_outliers)
    logger.info("Finished main function")


if __name__ == "__main__":
    main()
