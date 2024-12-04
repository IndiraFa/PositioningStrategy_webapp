import sys
import os
import pandas as pd
import plotly.express as px
import streamlit as st
import toml
import psycopg2
import logging

# Add the directory containing preprocess.py to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from streamlit_todb import fetch_data_from_db, configs_db

# Set the page layout to wide
st.set_page_config(layout="wide")


# Define the queries to read data from the database
FORMATTED_DATA_QUERY = 'SELECT * FROM "Formatted_data"'
RAW_DATA_QUERY = 'SELECT * FROM "raw_recipes"'
NORMALIZED_DATA_QUERY = 'SELECT * FROM "nutrition_withOutliers"'
OUTLIERS_DATA_QUERY = 'SELECT * FROM "outliers"'
NUTRITION_NO_OUTLIERS_QUERY = 'SELECT * FROM "nutrition_noOutliers"'
PREFILTRE_DATA_QUERY = 'SELECT * FROM "prefiltre_data"'

@st.cache_data
def get_cached_data(configs_db, query1, query2,
                    query3, query4, query5, query6):
    return fetch_data_from_db(configs_db, query1, query2, query3, query4, 
                              query5, query6)


def display_introduction():
    st.markdown("""
    <h1 style="color:purple;">
    Nutritional Data Analysis and Outlier Detection
    </h1>

    Welcome to this interactive application! Its purpose is to explore a 
    set of nutritional data extracted from a PostgreSQL database.  
    Through this interface, you can visualize data, understand processing 
    steps, and identify outliers.

    <div style="display: flex; justify-content: center; padding: 10px;">
        <div style="border: 2px solid purple; padding: 20px; background-color:\
             #f2e6ff; border-radius: 10px; width: 50%;">
            <h3 style="color: purple;">
            Page Structure:
            </h3>
            <ul>
                <li>Loading and exploring raw data.</li>
                <li>Analyzing formatted data adjusted to daily nutritional 
                    needs.</li>
                <li>Outlier identification using:
                    <ul>
                        <li><strong>Manual filters based on predefined 
                            thresholds.</strong></li>
                        <li><strong>Z-score statistical method.</strong></li>
                    </ul>
                </li>
                <li>Graphical visualization for better understanding of 
                    distributions.</li>
            </ul>
        </div>
    </div>
    
    Take your time to explore each step to better understand nutritional 
    data processing!  
    """, unsafe_allow_html=True)


def load_and_explore_raw_data(raw_data):
    st.write('\n Here is a preview of the data:')
    st.write(raw_data.head())
    st.write('''
    The data in the nutrition column is first extracted from the table 
            following this schema: \n
            [calories, total_fat, sugar, sodium, protein, saturated_fat,\
            carbohydrates] 
            ''')
    with st.expander("Note:"):
        st.markdown('''
        Except for calories, other values are expressed as percentages. \n
                    ''')

def analyze_formatted_data(formatted_data, normalized_data):
    st.write('Formatted data:')
    st.write(formatted_data.head())

    st.markdown('''
    Our data refers to a portion and has been adjusted, in percentage 
                terms, to daily values of 2000 calories for an adult.
                ''')
    st.latex(r'''
    \text{daily value} = \frac{\text{portion value}}{2000} \times 100
            ''')

    st.write('Adjusted data:')
    st.write(normalized_data.head())

    st.markdown(f'''
        Observing the adjusted data, we can initially identify some 
                outliers.
                ''')

def identify_outliers_with_manual_filters():
    st.markdown(f'''    
        We proceeded with data cleaning by removing outliers in two \
                steps: \n
        - <u>Step 1: Manual filtering by applying thresholds beyond which 
                outliers are identified.</u> \n   
        ''', unsafe_allow_html=True)

    # Display the filtering thresholds table
    thresholds = {
        'dv_calories_%': 5000,
        'dv_total_fat_%': 5000,
        'dv_sugar_%': 5000,
        'dv_sodium_%': 5000,
        'dv_protein_%': 2000,
        'dv_sat_fat_%': 2000,
        'dv_carbs_%': 5000
    }
    thresholds_df = pd.DataFrame(list(thresholds.items()), 
                                 columns=['Nutrient', 'Threshold'])

    table_html = thresholds_df.to_html(index=False)

    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            {table_html}
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("Note: Click to display more information"):
        st.write('''
        Number of recipes removed after applying thresholds = 645 
        ''')

def apply_z_score_method(outliers_size):
    st.markdown('''
        - <u>Step 2: Applying the Z-score method to identify outliers.
                </u> \n
        ''', unsafe_allow_html=True)

    st.latex(r'''
        \text{outliers} = \frac{\text{values} - \mu}{\sigma} > 3 
                ''')

    with st.expander("Note: Click to display more information"):
        st.write(f'''
        Number of recipes removed after applying thresholds followed by the 
                Z-score method = {outliers_size}
        ''')

def visualize_data_distribution(normalized_data, prefiltre_data,
 nutrition_noOutliers):
    options = {
        'Calories distribution': 'dv_calories_%',
        'Total fat distribution': 'dv_total_fat_%',
        'Sugar distribution': 'dv_sugar_%',
        'Sodium distribution': 'dv_sodium_%',
        'Protein distribution': 'dv_protein_%',
        'Saturated fat distribution': 'dv_sat_fat_%',
        'Carbohydrates distribution': 'dv_carbs_%'
    }
    selected_option = st.selectbox('Data visualization:',
                                    list(options.keys()))

    # Display corresponding graphs
    y_column = options[selected_option]

    # Add an option to select reference data
    data_option = st.radio(
        "Choose the reference data",
        ('Unfiltered data', 'Pre-filtered data', 'Filtered data'),
        index=2
    )

    # Select data based on chosen option
    if data_option == 'Unfiltered data':
        data = normalized_data
    elif data_option == 'Pre-filtered data':
        data = prefiltre_data
    else:
        data = nutrition_noOutliers

    # Add an x-scale slider
    x_min, x_max = st.slider(
        'Select the range of x values',
        min_value=float(data[y_column].min()),
        max_value=float(data[y_column].max()),
        value=(float(data[y_column].min()), float(data[y_column].max()))
    )

    # Filter data based on selected range
    filtered_data = data[(data[y_column] >= x_min) & 
                         (data[y_column] <= x_max)]

    # Use columns to display side-by-side graphs
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### {selected_option}")
        fig = px.histogram(filtered_data, x=y_column,
                            title=selected_option)
        st.plotly_chart(fig)

    with col2:
        st.write(f"### {selected_option} - Box Plot")
        fig_box = px.box(filtered_data, y=y_column, 
                         title=f"Box Plot - {selected_option}")
        st.plotly_chart(fig_box)

    # Calculate the number of valid and invalid recipes
    valid_recipes_count = filtered_data.shape[0]
    invalid_recipes_count = data.shape[0] - valid_recipes_count

    # Display this information in Streamlit
    st.markdown(f"""
    ### Recipe Summary:
    - **Number of valid recipes (within selected range)**: 
                {valid_recipes_count}
    - **Number of invalid recipes (outside range)**:
                {invalid_recipes_count}
    """)

def display_conclusion():
    st.markdown("""
    <div style="border: 2px solid purple; padding: 20px; background-color:
     #f2e6ff; border-radius: 10px;">
        <h3 style="color: purple;">
        Conclusion:
        </h3>
        The interactive visualization allows for better understanding of 
        distributions of various nutritional values across different categories 
        of food recipes. The data cleaning steps, including manual filtering 
        and Z-score method, ensure better quality of the data for 
        further analysis.
    </div>
    """, unsafe_allow_html=True)


def main():
    # Fetch data from the database
    formatted_data, raw_data, normalized_data, outliers_data, \
    nutrition_noOutliers, prefiltre_data = fetch_data_from_db(
        configs_db,
        FORMATTED_DATA_QUERY,
        RAW_DATA_QUERY,
        NORMALIZED_DATA_QUERY,
        OUTLIERS_DATA_QUERY,
        NUTRITION_NO_OUTLIERS_QUERY,
        PREFILTRE_DATA_QUERY
    )

    # Journal configuration (logging)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Connection to the PostgreSQL database
        logger.info("Connection to the PostgreSQL database ...")

        # Calculate the number of outliers
        outliers_size = outliers_data.shape[0]
        logger.info(f"Outliers size data: {outliers_size} lines.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

    # Call the introduction function
    display_introduction()

    # Call the function for loading and exploring raw data
    load_and_explore_raw_data(raw_data)

    # Call the function for analyzing formatted data
    analyze_formatted_data(formatted_data, normalized_data)

    # Call the function for identifying outliers with manual filters
    identify_outliers_with_manual_filters()

    # Call the function for applying Z-score method
    apply_z_score_method(outliers_size)

    # Call the function for graphical visualization of data distributions
    visualize_data_distribution(normalized_data, prefiltre_data, 
                                nutrition_noOutliers)

    # Call the conclusion function
    display_conclusion()

if __name__ == "__main__":
    main()

