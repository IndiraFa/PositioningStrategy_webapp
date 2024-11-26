import sys
import os
import pandas as pd
import plotly.express as px
import streamlit as st
import toml
import psycopg2
import logging
from streamlit_todb import fetch_data_from_db, configs_db


# Add the directory containing preprocess.py to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set the page layout to wide
st.set_page_config(layout="wide, centered")

# Read connection information from secrets.toml
secrets = toml.load('secrets.toml')
postgresql_config = secrets['connections']['postgresql']

def main():
    formatted_data, raw_data, normalized_data, outliers_data, \
        nutrition_noOutliers, prefiltre_data= fetch_data_from_db(
        configs_db,
        query1,
        query2,
        query3,
        query4,
        query5,
        query6
    )


    # Journal configuration (logging)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Connection to the PostgreSQL database
        logger.info("Connection to the PostgreSQL database ...")

        # Define the queries to read data from the database
        formatted_data_query = 'SELECT * FROM "Formatted_data"'
        raw_data_query = 'SELECT * FROM "raw_recipes"'
        normalized_data_query = 'SELECT * FROM "nutrition_withOutliers"'
        outliers_data_query = 'SELECT * FROM "outliers"'
        nutrition_noOutliers_query = 'SELECT * FROM "nutrition_noOutliers"'
        prefiltre_data_query = 'SELECT * FROM "prefiltre_data"'


        # Calculate the number of outliers
        outliers_size = outliers_data.shape[0]
        logger.info(f"Outliers size data : {outliers_size} lines.")

    except Exception as e:
        logger.error(f"An error occured : {e}")


###############################################################################
        #Introduction

        st.markdown("""
        <h1 style="color:purple;">
        Nutritional Data Analysis and Outlier Detection
        </h1>

        Welcome to this interactive application! Its purpose is to explore a 
        set of nutritional data extracted from a PostgreSQL database.  
        Through this interface, you can visualize data, understand processing 
        steps, and identify outliers.

        <div style="border: 2px solid black; padding: 10px; border-radius: 
                    5px;">
            <h3>Page Structure:</h3>
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
        
        Take your time to explore each step to better understand nutritional 
                    data processing!  
        """, unsafe_allow_html=True)

###############################################################################
        # Loading and exploring raw data.

        st.write('\n Here is a preview of the data:')
        st.write(raw_data.head())

        st.write('''
        The data in the nutrition column is first extracted from the table 
                following this schema: \n
                [calories, total_fat, sugar, sodium, protein, saturated_fat,
                carbohydrates] 
                ''')
        with st.expander("Note:"):
            st.markdown('''
            Except for calories, other values are expressed as percentages. \n
                        ''')

###############################################################################
    # Analyzing formatted data adjusted to daily nutritional needs.

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
###############################################################################
    # Outlier identification using: Manual filters based on predefined 
    # thresholds.

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
        thresholds_df = pd.DataFrame(list(thresholds.items()), \
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
###############################################################################
    # Graphical visualization for better understanding of distributions.

        # Dropdown menu to select a column
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

###############################################################################
    # Conclusion

        st.markdown("""
            <div style="border: 2px solid #0044cc; padding: 15px; 
                    border-radius: 10px; background-color: #f1f8ff; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #0044cc;">Conclusion</h2>
                <p style="font-size: 18px;">
                    Nutritional data analysis and outlier detection are key 
                    steps to ensure the reliability of the information used 
                    in dietary assessments.
                </p>
                <ul style="font-size: 18px;">
                    <li>Through manual filtering and statistical methods, 
                    we successfully identified and removed inconsistent data.
                    </li>
                    <li>Using the available tools, we explored various 
                    distributions to better understand the dataset.</li>
                </ul>
                <p style="font-size: 18px;">
                    This approach ensures the quality of the recipes 
                    in our dataset.
                </p>
            </div>
        """, unsafe_allow_html=True)
###############################################################################

    if __name__ == '__main__':
        main()
