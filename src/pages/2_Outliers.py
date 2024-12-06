import pandas as pd
import plotly.express as px
import streamlit as st
import toml
import logging
from db.db_instance import db_instance
from db.streamlit_todb import Database

logger = logging.getLogger("pages.Outliers")
# Set the page layout to wide
st.set_page_config(layout="wide")

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


def display_introduction():
    """
    Displays the introduction and structure of the page in the 
    Streamlit application.
    """

    logger.debug("Displaying the introduction to the application.")
    st.markdown("""
    <h1 style="color:purple;">
    Nutritional Data Analysis and Outlier Detection
    </h1>

    In this page the purpose is to explore a set of nutritional data extracted
                 from a PostgreSQL database. Through this interface, you can
                 visualize data, understand processing steps, and identify
                 outliers.

    
    Take your time to explore each step to better understand nutritional 
    data processing!  
    """, unsafe_allow_html=True)
    logger.debug("Introduction displayed successfully.")


def load_and_explore_raw_data(raw_data):
    """
    Loads and explores raw data.

    Args:
        raw_data (DataFrame): Raw data extracted from the database.
    """
        
    logger.debug("Loading and exploring raw data.")
    st.write('\n Preview of the data:')
    st.write(raw_data.head())
    st.write(
        '''
        Data from the nutrition column are first extracted from the table 
        following this schema:\n
        [calories, total_fat, sugar, sodium, protein, saturated_fat, 
        carbohydrates]
        '''
    )
    with st.expander("Note:"):
        st.markdown('''
        Except for calories, other values are expressed as percentages. \n
                    ''')
    logger.debug("Raw data loaded and explored successfully.")

def analyze_formatted_data(formatted_data, normalized_data):
    """
    Analyzes formatted and adjusted data.

    Args:
        formatted_data (DataFrame): Formatted data.
        normalized_data (DataFrame): Data normalized to daily values.
    """
        
    logger.debug("Display Analyzing formatted data and normalized data.")
    st.write('Preview of formatted data:')
    st.write(formatted_data.head())

    st.markdown('''
    Our data refers to 1 portion and has been adjusted, in percentage 
                terms, to daily values of 2000 calories for an adult.
                ''')
    st.latex(r'''
    \text{daily value} = \frac{\text{portion value}}{2000} \times 100
            ''')

    st.write('Preview of adjusted data:')
    st.write(normalized_data.head())

    st.markdown(f'''
        Observing the adjusted data, we can initially identify some 
                outliers.
                ''')
    logger.debug("Display Analyzing formatted data and normalized data successfully.")

def identify_outliers_with_manual_filters():
    """
    Identifies outliers using manual filtering.
    """
        
    logger.debug("Display Outliers identified with manual filters.")
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
    logger.debug("Display Outliers identified with manual filters successfully.")

def apply_z_score_method(outliers_size):
    """
    Applies the Z-score method to detect outliers.

    Args:
        outliers_size (int): Number of outliers identified.
    """

    logger.debug("Display Z-score method applied.")
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
    logger.debug("Display Z-score method applied successfully.")


def visualize_data_distribution(normalized_data: pd.DataFrame, prefiltre_data: pd.DataFrame,
 nutrition_noOutliers: pd.DataFrame):
    """
    Visualizes data distribution using interactive graphs.

    Args:
        normalized_data (DataFrame): Unfiltered data.
        prefiltre_data (DataFrame): Pre-filtered data.
        nutrition_noOutliers (DataFrame): Data without outliers.
    """
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
    logger.debug("Graphical visualization of data distributions displayed successfully.")

def display_conclusion():
    """
    Displays the conclusion of the analysis in the application.
    """
        
    logger.debug("Displaying the conclusion.")

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
            <p>The interactive visualization allows for better understanding
                 of distributions of various nutritional values across
                 different categories of food recipes. The data cleaning steps,
                 including manual filtering and Z-score method, ensure better
                 quality of the data for further analysis.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    logger.debug("Conclusion displayed successfully.")


def main():
    # SQL Queries
    QUERIES = {
        "formatted_data": 'SELECT * FROM "Formatted_data";',
        "raw_data": 'SELECT * FROM "raw_recipes";',
        "normalized_data": 'SELECT * FROM "nutrition_withOutliers";',
        "outliers_data": 'SELECT * FROM "outliers";',
        "nutrition_noOutliers": 'SELECT * FROM "nutrition_noOutliers";',
        "prefiltre_data": 'SELECT * FROM "prefiltre_data";',
    }

    # Récupérer les données de la base
    data = get_cached_data(db_instance, QUERIES)
    if not data or not all(isinstance(df, pd.DataFrame) and not df.empty for df in data.values()):
        st.error("Unable to load data. Please check the database connection.")
        return

    # Obtenir les différentes tables
    formatted_data = data.get("formatted_data")
    logger.info(formatted_data)
    raw_data = data.get("raw_data")
    logger.info(raw_data)
    normalized_data = data.get("normalized_data")
    logger.info(normalized_data)
    outliers_data = data.get("outliers_data")
    logger.info(outliers_data)
    nutrition_noOutliers = data.get("nutrition_noOutliers")
    prefiltre_data = data.get("prefiltre_data")

    # Calculer le nombre d'outliers
    outliers_size = outliers_data.shape[0]
    logger.info(f"Number of outliers: {outliers_size}")


    # Appels les fonctions d'affichage
    display_introduction()
    display_conclusion()
    "---"
    load_and_explore_raw_data(raw_data)
    analyze_formatted_data(formatted_data, normalized_data)
    identify_outliers_with_manual_filters()
    apply_z_score_method(outliers_size)
    visualize_data_distribution(normalized_data, prefiltre_data, nutrition_noOutliers)
    
    logger.debug("Main function executed successfully.")

if __name__ == "__main__":
    main()

logger.info("Outliers page fully loaded.")
