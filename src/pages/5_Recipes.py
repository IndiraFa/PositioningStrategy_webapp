import os
import sys
import logging
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
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


# set path to the root folder
current_dir = os.path.dirname(os.path.abspath(__file__))
# PARENT_DIR = os.path.dirname(CURRENT_DIR)
# dir_test = os.path.join(os.path.dirname(PARENT_DIR), 'tests/tags')
current_dir = Path.cwd()



def display_datatable(all_recipes, label_choice='A'):
    df_choix = all_recipes[all_recipes['label'] == label_choice].iloc[:10,:]
    if not df_choix.empty:
        st.dataframe(df_choix[['name','nutriscore','label','tags']], hide_index=True)
    # st.markdown(
    #     f"""<div style="text-align: right;"><i>
    #     {all_recipes.shape[0]} recipes in total
    #     </i></div>
    #     """, 
    #                 unsafe_allow_html=True)

def display_choosing_labels(all_recipes_proccessed, all_recipes):
    st.markdown(
            """
            <div style="text-align: justify;">
            This section is used to study the statistical description of the recipes with the selected label.\n
            You can choose one label to study and see the 10 random recipes having this label.
            </div>
            """,
            unsafe_allow_html=True
        )
    
    col1, col2 = st.columns([0.7, 0.3])
    with col2:
        labels = ['A', 'B', 'C', 'D', 'E'] 
        st.markdown(
            "<p style='font-size:14px;'>"
            "<i>Select specially 1 label that you want to study</i></p>",
            unsafe_allow_html=True
        )
        choix = st.radio('', labels, index=0)
        if choix :
            with col1: 
                display_datatable(all_recipes, choix)
                st.write('...')
        
    # st.markdown(f'Statistical description of the recipes with the {choix} label')
    txt = st.warning(f'Statistical description of the recipes with the {choix} label') 

    df_choix = all_recipes_proccessed[all_recipes_proccessed['label'] == choix]
        
    col11, col12 = st.columns([0.5, 0.5])
    with col11:
        dfsort_stats = display_statistical_description(df_choix, choix)
    with col12:
        display_pie_chart(dfsort_stats)
                
def display_statistical_description(all_recipes_proccessed, choix):
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
    # st.write(f'And top 10 recipes having {choix} label and tags selected')
    # st.dataframe(df_choix[['name', 'nutriscore']].head(10), hide_index=True)
    return dfsort_stats

def display_pie_chart(dfsort_stats):
    dfsort_stats = dfsort_stats.drop('nutriscore', axis=0)
    fig = px.pie(
        dfsort_stats, values='mean', names=dfsort_stats.index, 
        title='Nutrition distribution of the recipes with the selected label',
        color=dfsort_stats.index)    
    fig.update_layout(legend_title_text='Nutrition',
                    legend=dict(orientation="v", yanchor="bottom", y=0.2, xanchor="center", x=0.2),
                    )
    st.plotly_chart(fig)

def select_to_process(all_recipes, all_recipes_proccessed, highest_recipes, tags_input):

    if tags_input: 
        try:
            # all_recipes, all_recipes_proccessed, highest_recipes = tags_nutriscore_correlation.main(tags_input)
            display_boxplot(all_recipes, tags_input)
            # col1, col2 = st.columns([0.7, 0.3])
            # with col1:
            #     display_top10recipes(all_recipes, highest_recipes, tags_input)
            # with col2:
            #     display_choosing_labels(all_recipes_proccessed)
            #     st.write('...')
                
            
            
            st.write('...')

            st.subheader(f'Learning more with label study')
            
            display_choosing_labels(all_recipes_proccessed, all_recipes)

            st.write('...')

            # st.dataframe(top3_recipes['name'])
        except Exception as e:
            st.write("An error occurred: ", e)
    
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
def display_anova_test(all_recipes_proccessed):
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

def display_conclusion():
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

def display_header_intro(position='center'):
    if position == 'center':
        st.markdown(
            "<h1 style='color:purple; text-align: center;'>Tag analysis</h1>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<h1 style='color:purple; text-align: justify;'>Tag analysis</h1>",
            unsafe_allow_html=True
        )

    st.markdown( 
        """
        <div style="text-align: center;">
        This tab is dedicated to searching for recipes with one or more specific tags. 
        They are keywords that designate the nature or type, or the main method of the recipes, 
        for example: 'vegetarian', 'dinner', 'course' (see the word cloud below).
        The analysis of the labels allows to understand the correlation between the tags and 
        the nutriscore of the recipes. So you can choose your satisfied recipes below our studies."
        </div>
        """,
        unsafe_allow_html=True  
    )
def display_header():
    st.markdown(
        "<h1 style='color:purple;'>Tag analysis</h1>",
        unsafe_allow_html=True
        )

    st.write(
        """
       Filled in by users, the labels describe the nature, type or main cooking method of the recipes, 
       e.g 'vegetarian', 'dinner', 'course' (see the word cloud below). 
       We plan to explore the information from these labels that is considered useful for health. 
       We have associated each recipe with a rating and a label, the study will sort 
       the recipes with the selected labels, study the distribution of nutriscores, 
       the highest nutriscores and then focus on the distribution of nutrients according to the label.
       
       Next to the dietary keywords, there are also typical cooking labels like 'preparation', 
       'main ingredient', 'main dish'. Try to find your 'dinner' or 'beginner cook' if you want 
       to cook with your children and choose one with a high rating.
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
            <p>The labels are clearly consistent with our nutriscore calculated on page 2. 
            "Low protein" recipes cannot offer a good ratio with nutrients and are therefore rated C or D. 
            But, with a "low cholesterol" recipe, the rating is now A. 
            This study shows you how healthy these recipes are.</p>
        </div>
        """, unsafe_allow_html=True)

def display_tagscloud():
    current_dir = os.path.dirname(__file__)
    img_path = os.path.join(current_dir, "..", "tagscloud.png")
    #img = Image.open(img_path)
    st.image(img_path, caption='Word cloud of tags', use_column_width=True)

def display_select_tools():
    """
    Display the select tools for the user to choose the tags
    """
    # get the tags from the user
    options = ['low carb', 'low protein', 'course', 'vegetarian', 'main ingredient', 'other']
    st.markdown(
        "<p style='font-size:12px;'>"
        "<i>Select one or many options. Choose 'other' if you want to entry manually</i></p>",
        unsafe_allow_html=True
    )
    selected_options = st.multiselect(
        '', options, default=['low carb']
    )
    if not selected_options:
        st.warning('Please select at least one option')
        st.stop()

    if ('other' in selected_options):
        custom_input = st.text_input('Entry your tags here (using only comma to separate tags):')
        st.write(f'_You entered_: {custom_input}')
        tags_input = custom_input
    else:
        tags_input = ', '.join(selected_options)
        st.write(f'There are your {len(selected_options)} tags: {tags_input}')  

    
    return tags_input

def display_boxplot(all_recipes, tags_input):
    """
    Display the boxplot of the nutriscore & label of all recipes having the tags
    """
    fig = px.box(all_recipes, x='label', y='nutriscore', 
            title=f"<i>Distribution of nutriscore of all recipes having <span style='background-color:purple';>{tags_input}</span> and their labels associated</i>",
            category_orders={'label': ['A', 'B', 'C', 'D', 'E']},
            width=500, height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"""<div style="text-align: right; font-size:12px"><i>
        {all_recipes.shape[0]} recipes in total
        </i></div>
        """, 
                    unsafe_allow_html=True)


def main():
    """
    Main function to display the tags
    """
    # at beginning of the page
    st.set_page_config(layout="centered")
    

    # setup introduction of page : header, tags cloud, select tools
    # display_header_intro(position='center')
    display_header()
    "---"
    left, right = st.columns([0.4, 0.6])
    with right:
        display_tagscloud()
    with left:
        tags_input = display_select_tools()
    "----"

    # processing when tags are selected
    all_recipes, all_recipes_proccessed, highest_recipes = tags_nutriscore_correlation.main(tags_input)
    st.markdown(
        f"<h2 style='text-align: center;'>Visualisation of the recipes with <span class='highlight :purple;'>{tags_input}</span></h2>",
        unsafe_allow_html=True
    )
    select_to_process(all_recipes, all_recipes_proccessed, highest_recipes, tags_input)
    # display_anova_test(all_recipes_proccessed)
    display_conclusion()

if __name__ == "__main__":
    main()
