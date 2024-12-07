import logging
import streamlit as st
import plotly.express as px
import tags_nutriscore_correlation
from core.asset_manager import get_asset_path


logger = logging.getLogger("pages.recipes")


def display_datatable(all_recipes, label_choice='A'):
    """
    Display the datatable of the recipes with the selected label

    Args:
        all_recipes (pd.DataFrame): DataFrame of all recipes
        label_choice (str): The selected label to display the recipes

    Returns:
        None
    """
    df_choix = all_recipes[all_recipes['label'] == label_choice].iloc[:10, :]
    if not df_choix.empty:
        st.dataframe(df_choix[['name', 'nutriscore', 'label', 'tags']],
                     hide_index=True)


def display_choosing_labels(all_recipes_proccessed, all_recipes):
    """
    Display the choosing labels section

    Args:
        all_recipes_proccessed (pd.DataFrame): DataFrame of all recipes
        processed have only the nutrient columns
        all_recipes (pd.DataFrame): DataFrame of all recipes

    Returns:
        None
    """
    st.markdown(
        """
        <div style="text-align: justify;">
        This section is used to study the statistical description of
        the recipes with the selected label.\n
        You can choose one label to study and see the 10 random recipes
        having this label.
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
        if choix:
            with col1:
                display_datatable(all_recipes, choix)
                st.markdown(
                    """
                    We continue to see below the label chosen how the recipes
                    are distributed in terms of nutrition. Statistical table
                    shows the mean, standard deviation, min and max values of
                    each nutrition.
                    And the bar chart represents the distribution of the
                    nutrition, compared to the reference values.
                    """, unsafe_allow_html=True
                )

    st.warning(
        f'Statistical description of the recipes with the {choix} label'
    )

    df_choix = all_recipes_proccessed[all_recipes_proccessed['label'] == choix]
    dfsort_stats = display_statistical_description(df_choix, choix)

    display_bar_chart(dfsort_stats)


def display_statistical_description(all_recipes_proccessed, choix):
    """
    Display the statistical description of the recipes with the selected label

    Args:
        all_recipes_proccessed (pd.DataFrame): DataFrame of all recipes
        processed have only the nutrient columns
        choix (str): The selected label to display the recipes

    Returns:
        pd.DataFrame: DataFrame of the statistical description of the recipes
        of the selected label
    """
    df_choix = all_recipes_proccessed[
        all_recipes_proccessed['label'] == choix
    ]

    dfsort_stats = df_choix.drop(
        columns=['id', 'name', 'label']
    ).describe().T[['mean', 'std', 'min', 'max']]

    st.table(dfsort_stats.round(2))

    return dfsort_stats


def display_bar_chart(dfsort_stats):
    """
    Display the bar chart of the nutrition of the recipes with
    the selected label

    Args:
        dfsort_stats (pd.DataFrame): DataFrame of the statistical description
        of the recipes of the selected label

    Returns:
        None
    """
    dfsort_stats = dfsort_stats.drop('nutriscore', axis=0)
    fig = px.bar(dfsort_stats, x=dfsort_stats.index, y='mean',
                 title="""Nutrition of the recipes on bar chart
                 with the selected label""",
                 labels={'mean': 'mean values', 'index': 'Nutrition'})
    logger.debug("Add reference line plot for each nutrition ")
    shapes = []
    thresholds = [37, None, 84, 76, 91, 95, None]
    for i, threshold in enumerate(thresholds):
        if threshold is not None:
            shapes.append(
                dict(
                    type="line",
                    x0=i - 0.4,
                    x1=i + 0.4,
                    y0=threshold,
                    y1=threshold,
                    line=dict(
                        color="Red",
                        width=2,
                    ),
                )
            )

    fig.update_layout(shapes=shapes)

    st.plotly_chart(fig)


def select_to_process(all_recipes,
                      all_recipes_proccessed,
                      highest_recipes,
                      tags_input):
    """
    Processing after the tags are selected

    Args:
        all_recipes (pd.DataFrame): DataFrame of all recipes, including
        the reicpes names
        all_recipes_proccessed (pd.DataFrame): DataFrame of all recipes
        processed have only the nutrient columns
        highest_recipes (pd.DataFrame): DataFrame of the recipes that have
        the highest nutriscore
        tags_input (str): The selected tags to process

    Returns:
        None"""
    if tags_input:
        try:
            display_boxplot(all_recipes, tags_input)
            st.write(
                """
                The boxplot above represents the main distribution of recipes
                according to the labels. The X axis of the plot is the labels
                and the Y axis is the range of the nutriscores.
                """
            )

            st.subheader('Learning more with label study')

            display_choosing_labels(all_recipes_proccessed, all_recipes)

            st.write(
                """
                The bar chart above shows the distribution of the nutrition
                of the recipes with the selected label.
                The red line represents the reference values of the nutrition.
                For calories, sugar, satured fat and sodium, if the bar is
                above the red line, it means all these recipes have more
                nutrients than the reference values.
                But for protein, a good recipe must have the bar
                above the red line.
                """
            )

        except Exception as e:
            st.write("An error occurred: ", e)


def display_header():
    """
    Display the header of the page

    Returns:
        None
    """
    st.markdown(
        "<h1 style='color:purple;'>Tag analysis</h1>",
        unsafe_allow_html=True
    )

    st.write(
        """
        Filled in by users, the labels describe the nature, type or
        main cooking method of the recipes, e.g 'vegetarian', 'dinner',
        'course' (see the word cloud below).\n
        We plan to explore the information from these labels that is
        considered useful for health. We have associated each recipe with
        a rating and a label, the study will sort the recipes with the
        selected labels, study the distribution of nutriscores, the highest
        nutriscores and then focus on the distribution of nutrients according
        to the label.

        Next to the dietary keywords, there are also typical cooking labels
        like 'preparation', 'main ingredient', 'main dish'. Try to find your
        'dinner' or 'beginner cook' if you want to cook with your children
        and choose one with a high rating.
        """, unsafe_allow_html=True
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
            <p>The labels are clearly consistent with our nutriscore
            calculated on page 2. "Low protein" recipes cannot offer a good
            ratio with nutrients and are therefore rated C or D. But, with a
            "low cholesterol" recipe, the rating is now A. This study shows
            you how healthy these recipes are.</p>
        </div>
        """, unsafe_allow_html=True)


def display_tagscloud():
    """
    Display the tags cloud image for the user to see

    Returns:
        None
    """
    TAGSCLOUD = "images/tagscloud.png"
    st.image(
        get_asset_path(TAGSCLOUD),
        caption='Word cloud of tags',
        use_column_width=True
    )


def display_select_tools():
    """
    Display the select tools for the user to choose the tags

    Returns:
        str: The selected tags
    """
    logger.debug("Get the tags from the user")

    options = ['low carb', 'low protein', 'course', 'vegetarian',
               'main ingredient', 'other']

    st.markdown(
        """
        <p style='font-size:12px;'>
        <i>Select one or many options.
        Choose 'other' if you want to entry manually</i></p>
        """,
        unsafe_allow_html=True
    )

    selected_options = st.multiselect(
        '', options, default=['low carb']
    )
    if not selected_options:
        st.warning('Please select at least one option')
        st.stop()

    if 'other' in selected_options:
        custom_input = st.text_input(
            'Entry your tags here (using only comma to separate tags):'
        )
        st.write(f'_You entered_: {custom_input}')
        tags_input = custom_input
    else:
        tags_input = ','.join(selected_options)
        st.write(f'There are your {len(selected_options)} tags: {tags_input}')

    return tags_input


def display_boxplot(all_recipes, tags_input):
    """
    Display the boxplot of the nutriscore & label of recipes having the tags

    Args:
        all_recipes (pd.DataFrame): DataFrame of all recipes
        tags_input (str): The selected tags to display the recipes

    Returns:
        None
    """
    fig = px.box(all_recipes, x='label', y='nutriscore',
                 title=f"""
                 <i>Distribution of nutriscore of all recipes having
                 <span style='background-color: #FFFF00'>{tags_input}</span>
                 and their labels associated</i>""",
                 category_orders={'label': ['A', 'B', 'C', 'D', 'E']},
                 width=500, height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f"""<div style="text-align: right; font-size:12px"><i>
        {all_recipes.shape[0]} recipes in total
        </i></div>
        """, unsafe_allow_html=True)


def main():
    """
    Main function to display the tags

    Returns:
        None
    """

    st.set_page_config(layout="centered")

    display_header()
    "---"
    left, right = st.columns([0.4, 0.6])
    with right:
        display_tagscloud()
    with left:
        tags_input = display_select_tools()
    "----"

    all_recipes, all_recipes_proccessed, highest_recipes = (
        tags_nutriscore_correlation.main(tags_input)
    )
    st.markdown(
        f"""<h2 style='text-align: center;'>Visualisation of the recipes with
        <span style='background-color: #FFFF00'>{tags_input}</span></h2>""",
        unsafe_allow_html=True
    )
    select_to_process(all_recipes,
                      all_recipes_proccessed,
                      highest_recipes,
                      tags_input)


if __name__ == "__main__":
    main()
