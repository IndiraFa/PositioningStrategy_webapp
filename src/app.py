import streamlit as st
import pandas as pd
import plotly.express as px
from nutriscore_analysis import (
    nutriscore_analysis,
    shapiro_test,
    ks_test,
    ad_test,
    skewness,
    kurtosis
)
from utils.config_logging import configure_logging

# Initialize logging
logger = configure_logging()


def main():
    logger.info("Streamlit App is starting")

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
        We built a Nutrition Score based on daily value intaked recommandations
        to explore for Mangetamain the opportunity to position itself as a 
        healthy food brand. The method is described in the Appendix section.
        """
    )
    st.page_link("pages/6_Appendix.py", label="Appendix")

    data_with_outliers = pd.read_csv(
        './datasets/nutrition_table_nutriscore_with_outliers.csv'
        )
    data_with_outliers = data_with_outliers.dropna(subset=['nutriscore'])
    data_no_outliers = pd.read_csv(
        './datasets/nutrition_table_nutriscore_no_outliers.csv'
        )
    data_no_outliers = data_no_outliers.dropna(subset=['nutriscore'])

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
        st.write("without outliers ..... analysis to be completed")

    st.subheader("Analysis of the Nutri-Score distribution")

    analysis = st.selectbox(
        "Select the test for a normal distribution of the Nutriscore",
        ["Shapiro-Wilk", "Kolmogorov-Smirnov", "Anderson-Darling"],
        key=3
    )

    if analysis == "Shapiro-Wilk":
        st.write("**Shapiro-Wilk test**")

        shapiro_test_with_outliers = shapiro_test(
            data_with_outliers, 'nutriscore'
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
            f"The Kolmogorov-Smirnov test for the Nutri-Score with outliers is "
            f"{ks_test_with_outliers}"
        )

        ks_test_no_outliers = ks_test(data_no_outliers, 'nutriscore')
        st.write(
            f"The Kolmogorov-Smirnov test for the Nutri-Score without outliers "
            f"is {ks_test_no_outliers}"
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
            f"The Anderson-Darling test for the Nutri-Score without outliers is "
            f"{ad_test_no_outliers}"
        )

    st.write(
        """
        **All tests show that the Nutri-Score is not normally distributed.**
        (NB : the Shapiro-Wilk test is more accurate for N<5000)
        """
    )

    st.divider()

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

        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)

        st.image('scale.png', width=600)

    with col4:
        fig = px.pie(
            data_no_outliers,
            names='label',
            title='Nutri-Score Label Distribution without outliers',
            color='label',
            color_discrete_map=color_map
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)

        st.write(
            """
            Overall, the recipes show good nutritional quality, with around 90%
            of label A, B and C. Getting rid of the outliers even improved the
             good to bad nutritional quality ratio.
             """
        )


if __name__ == "__main__":
    main()
