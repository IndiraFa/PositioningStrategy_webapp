import os
import sys
import logging
import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.express as px
from PIL import Image
from sqlalchemy import create_engine
import tags_nutriscore_correlation 

# Configure the logging module
logging.basicConfig(
    level=logging.INFO,  
    # format of the log messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler("app.log"),  # save the logs in a file
        logging.StreamHandler()  # show the logs in the console
    ]
)

# Create a logger object
logger = logging.getLogger("app_logger")
logger.info("App tags")
# charger les informations de connexion à partir de secrets.toml
db_host = st.secrets["connections"]["postgresql"]["host"]
db_database = st.secrets["connections"]["postgresql"]["database"]
db_username = st.secrets["connections"]["postgresql"]["username"]
db_password = st.secrets["connections"]["postgresql"]["password"]
db_port = st.secrets["connections"]["postgresql"]["port"]
db_url = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"

# Create a connection to the database
# engine = create_engine(db_url)
# with engine.connect() as connection:
#     query = "SELECT * FROM your_table LIMIT 10;"
#     df = pd.read_sql(query, connection)

# @st.cache_data
# set path to the root folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
dir_test = os.path.join(os.path.dirname(PARENT_DIR), 'tests/tags')

st.set_page_config(layout="wide")
st.markdown(
        "<h1 style='color:purple; text-align: center;'>Tag analysis</h1>",
        unsafe_allow_html=True
    )
# st.title("Tag analysis")
st.markdown( 
    """
    <div style="text-align: justify;">
    This tab is dedicated to searching for recipes with one or more specific labels. 
    They are keywords that designate the nature or type, or the main method of the recipes, 
    for example: 'vegetarian', 'dinner', 'course' (see the word cloud below).
    The analysis of the labels allows to understand the correlation between the labels and 
    the nutriscore of the recipes. So you can choose your satisfied recipes below our studies."
    </div>
    """,
    unsafe_allow_html=True
)

st.text("---------------------------------")

left, right = st.columns([0.6, 0.4])
with right:
    # st.pyplot(plt)
    img = Image.open(os.path.join(CURRENT_DIR,'tagscloud.png'))
    st.image(img, 
            caption='Word cloud of tags', use_column_width=True)

with left:
    st.markdown(
        """ 
        <div style="text-align: justify;">
        We invite you to choose one or more tags that interest you in order
        to obtain information on the associated recipes and their nutriscore. 
        You can also manually enter your tags if you cannot find your tag 
        in the proposed list.
        </div>
        """,
        unsafe_allow_html=True
    )   


    # get the tags from the user
    options = ['low carb', 'low protein', 'course', 'vegetarian', 'other']
    selected_options = st.multiselect(
        'Select one or many options. Choose other if you want to entry manually', options
    )

    if ('other' in selected_options):
        custom_input = st.text_input('Entry your tags here (using only comma to separate tags):')
        st.write(f'You entered: {custom_input}')
        tags_input = custom_input
    else:
        tags_input = ', '.join(selected_options)
        st.write(f'There are your {len(selected_options)} tags: {selected_options}')
        

#-------------------------------------------------
# config color map for pie chart after processing tags
color_map = {
    'A': '#1c682c',
    'B': '#3cb455',
    'C': '#f1c232',
    'D': '#e69138',
    'E': '#f44336'
}

st.subheader(f"Visualisation of the recipes with {selected_options}")
if tags_input: 
    try:
        all_recipes, all_recipes_proccessed, highest_recipes = tags_nutriscore_correlation.main(tags_input)
        # divide the streamlit page into two columns
        col1, col2 = st.columns(2)
        with col1:
        # this column will be used to display the results
        #-------------------------------------------------
            if all_recipes.shape[0] > 0:
                st.markdown(f'Top 10 recipes randomly with **{tags_input}** having highest nutriscore:')
                st.dataframe(highest_recipes[['name','nutriscore','label']].head(10), hide_index=True)
                st.markdown(f'<div style="text-align: right;"><i>{all_recipes.shape[0]} recipes in total</i></div>', 
                            unsafe_allow_html=True)
            else:
                st.write('No recipe found with these tags')
        with col2:
            # boxplot 
            fig = px.box(all_recipes, x='label', y='nutriscore', 
                         title=f'<i>Boxplot of nutriscore of recipes having {selected_options} and their labels</i>',
                         category_orders={'label': ['A', 'B', 'C', 'D', 'E']},
                         width=500, height=400)
            st.plotly_chart(fig)
            # commentaire sur le boxplot
            st.write('...')

        st.subheader(f'Label study with {selected_options} in the recipes')
        st.markdown('This section is used to ...', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            labels = ['A', 'B', 'C', 'D', 'E']
            choix = st.radio('Select 1 label that you want to study:', labels)
            df_choix = all_recipes_proccessed[all_recipes_proccessed['label'] == choix]
            df_choix.rename(columns={'dv_calories_%':'calories', 
                                     'dv_protein_%':'protein',
                                     'dv_sat_fat_%':'satured fat',
                                     'dv_total_fat_%':'total fat',
                                     'dv_carbs_%':'carbohydrates',
                                     'dv_sugar_%':'sugar',
                                     'dv_sodium_%':'sodium'
                                     }, inplace=True)
            
            # st.markdown(f"The number of recipes with the {choix} label is {df_choix.shape[0]}"
            #         "\nNow the statistical description of these recipes is:")
            
            dfsort_stats = df_choix.drop(columns=['id', 'name', 'label']).describe().T[['mean','std','min','max']]
            st.table(dfsort_stats.round(2))
            st.write(f'And top 10 recipes having {choix} label and tags selected')
            st.dataframe(df_choix[['name', 'nutriscore']].head(10), hide_index=True)

        with col2:
            
            # this column will be used to display the plot of the results
            dfsort_stats = dfsort_stats.drop('nutriscore', axis=0)
            fig = px.pie(
                dfsort_stats, values='mean', names=dfsort_stats.index, 
                title='Nutrition distribution of the recipes with the selected label',
                color=dfsort_stats.index)    
            fig.update_layout(legend_title_text='Nutrition',
                              legend=dict(orientation="v", yanchor="bottom", y=0.2, xanchor="center", x=0.2),
                              )
            st.plotly_chart(fig)
            st.write('...')

        # st.dataframe(top3_recipes['name'])
    except Exception as e:
        st.write("An error occurred: ", e)
    
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    st.subheader("ANOVA TEST")

    st.markdown(
        """
        <div style="text-align: justify;">
        This section is used to do the ANOVA test between the nutriscore of the selected labels from selected tag recipes'
        \nThe null hypothesis is that the means of the nutriscore of the selected labels are equal
        """, unsafe_allow_html=True
        )

    labels = ['A', 'B', 'C', 'D', 'E']
    choices = []
    
    for label in labels:
        num = st.checkbox(f'{label}')
        if num:
            choices.append(label)
    if len(choices) < 2:
        st.write('Please select at least 2 labels to perform the ANOVA test')
        st.stop()
    else:
        df_choix = all_recipes_proccessed[all_recipes_proccessed['label'].isin(choices)]
        grouped_data = [group['nutriscore'].values for name, group in df_choix.groupby('label')]
        f_statistic, p_value = stats.f_oneway(
            *grouped_data
        )
        st.markdown(
            f"""
            --- ANOVA test results --- 
            \nF-statistic = {f_statistic:.2f} \np-value = {p_value:.2f} 
            """, unsafe_allow_html=True
            )
        if p_value < 0.05:
            st.write("The p-value is less than 0.05, we reject the null hypothesis")
        else:
            st.write("The p-value is greater than 0.05, we fail to reject the null hypothesis")

st.text("---------------------------------")
st.markdown(
        "<h2 style='color:black; text-align: center;'>Conclusion</h2>",
        unsafe_allow_html=True
    )
st.markdown(
    """
    <div style="text-align: justify;">
    In this section, we have presented the analysis of the recipes with the selected tags. 
    We have shown the top 10 recipes with the highest nutriscore and the statistical description of 
    the recipes with the selected label. We have also performed the ANOVA test to compare the nutriscore 
    of the selected labels. 
    </div>
    """,
    unsafe_allow_html=True
)