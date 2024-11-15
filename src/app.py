import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from nutriscore_analysis import (
    nutriscore_analysis,
    shapiro_test,
    ks_test,
    ad_test,
    skewness,
    kurtosis
)
from utils.config_logging import configure_logging
from utils.data_loader import download_data

# Initialize logging
logger = configure_logging()

# Constants
DATA_WITH_OUTLIERS_PATH = 'src/datasets/nutrition_table_nutriscore_with_outliers.csv'
DATA_NO_OUTLIERS_PATH = 'src/datasets/nutrition_table_nutriscore_no_outliers.csv'
COLOR_MAP = {
    'A': '#1c682c',
    'B': '#3cb455',
    'C': '#f1c232',
    'D': '#e69138',
    'E': '#f44336'
}

def load_data(file_path, subset_column='nutriscore'):
    """Loads CSV data and drops rows with missing values in the specified column."""
    try:
        data = pd.read_csv(file_path)
        return data.dropna(subset=[subset_column])
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return pd.DataFrame()  # Return empty DataFrame if there's an error

def display_header():
    """Displays the main header and description for the app."""
    st.set_page_config(layout="wide")
    st.markdown(
        "<h1 style='color:purple;'>Positioning strategy for Mangetamain</h1>",
        unsafe_allow_html=True
    )
    st.header(
        """
        The analysis of the Nutriscore shows that Mangetamain already has 
        the potential to build a strong brand around healthy food.
        """
    )
    st.write(
        """
        We built a Nutrition Score based on daily value intake recommendations
        to explore for Mangetamain the opportunity to position itself as a 
        healthy food brand. The method is described in the Appendix section.
        """
    )
    st.page_link("pages/6_Appendix.py", label="Appendix")

def display_histogram(data, title, color, xaxis_range=(0, 14), yaxis_range=(0, 45000)):
    """Displays a histogram for Nutri-Score with custom bins."""
    bins = st.slider("Select the number of bins", 4, 100, 28)
    fig = px.histogram(
        data,
        x='nutriscore',
        nbins=bins,
        title=title,
        color_discrete_sequence=[color]
    )
    fig.update_layout(
        xaxis_title='Nutri-Score',
        yaxis_title='Frequency',
        template='plotly_white',
        bargap=0.1,
        xaxis=dict(range=xaxis_range),
        yaxis=dict(range=yaxis_range)
    )
    st.plotly_chart(fig)

def display_pie_chart(data, title):
    """Displays a pie chart for Nutri-Score label distribution."""
    fig = px.pie(
        data,
        names='label',
        title=title,
        color='label',
        color_discrete_map=COLOR_MAP
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig)

def perform_statistical_analysis(data_with_outliers, data_no_outliers):
    """Performs statistical analysis and displays results for each dataset."""
    results = pd.DataFrame({
        'Mean': [nutriscore_analysis(data_with_outliers)[0], nutriscore_analysis(data_no_outliers)[0]],
        'Median': [nutriscore_analysis(data_with_outliers)[1], nutriscore_analysis(data_no_outliers)[1]],
        'Max': [nutriscore_analysis(data_with_outliers)[2], nutriscore_analysis(data_no_outliers)[2]],
        'Min': [nutriscore_analysis(data_with_outliers)[3], nutriscore_analysis(data_no_outliers)[3]],
        'Skewness': [skewness(data_with_outliers, 'nutriscore'), skewness(data_no_outliers, 'nutriscore')],
        'Kurtosis': [kurtosis(data_with_outliers, 'nutriscore'), kurtosis(data_no_outliers, 'nutriscore')]
    }, index=['With outliers', 'Without outliers'])
    st.write(results)

def main():
    logger.info("Streamlit App is starting")
    display_header()

    data_with_outliers = load_data(DATA_WITH_OUTLIERS_PATH)
    data_no_outliers = load_data(DATA_NO_OUTLIERS_PATH)

    # Analysis Results
    perform_statistical_analysis(data_with_outliers, data_no_outliers)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nutri-Score based on the full data set")
        display_histogram(data_with_outliers, "Nutri-Score Distribution with Outliers", '#741B47')
    
    with col2:
        st.subheader("Nutri-Score based on the data set without outliers")
        display_histogram(data_no_outliers, "Nutri-Score Distribution without Outliers", '#C27BA0')
    
    st.subheader("Nutri-Score label distribution")
    col3, col4 = st.columns(2)
    with col3:
        display_pie_chart(data_with_outliers, "Nutri-Score Label Distribution with outliers")
        st.image('scale.png', width=600)
    with col4:
        display_pie_chart(data_no_outliers, "Nutri-Score Label Distribution without outliers")

    st.subheader("Analysis of the Nutri-Score distribution")
    analysis = st.selectbox(
        "Select the test for a normal distribution of the Nutriscore",
        ["Shapiro-Wilk", "Kolmogorov-Smirnov", "Anderson-Darling"]
    )

    test_functions = {
        "Shapiro-Wilk": shapiro_test,
        "Kolmogorov-Smirnov": ks_test,
        "Anderson-Darling": ad_test
    }
    if analysis in test_functions:
        st.write(f"**{analysis} test**")
        for label, dataset in zip(["with outliers", "without outliers"], [data_with_outliers, data_no_outliers]):
            test_result = test_functions[analysis](dataset, 'nutriscore')
            st.write(f"The {analysis} test for the Nutri-Score {label} is {test_result}")

    st.write(
        "**All tests show that the Nutri-Score is not normally distributed.** "
        "(Note: the Shapiro-Wilk test is more accurate for N<5000)"
    )

if __name__ == "__main__":
    main()
