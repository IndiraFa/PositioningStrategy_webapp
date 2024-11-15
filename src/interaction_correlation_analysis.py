import pandas as pd
# import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# from pathlib import Path
from functools import reduce

path = 'src/datasets/RAW_interactions.csv'
interaction_data = pd.read_csv(path, sep=',')

path2 = 'src/datasets/nutrition_table_nutriscore_no_outliers.csv'
nutriscore_data = pd.read_csv(path2, sep=',')


def interactions_df(data):
    """
    Compute the number of interactions, reviews, ratings and average rating
    for each recipe.

    Parameters:
    - data: DataFrame, the interaction data.

    Returns:
    - result: DataFrame, the result of the computation.
    """
    data_filtered = data.dropna(subset=['rating', 'review'])
    interaction_count = (
        data_filtered
        .groupby('recipe_id')
        .size()
        .reset_index(name='interaction_count')
    )
    review_count = (
        data_filtered
        .groupby('recipe_id')['rating']
        .count()
        .reset_index(name='review_count')
    )
    rating_count = (
        data_filtered
        .groupby('recipe_id')['rating']
        .count()
        .reset_index(name='rating_count')
    )
    average_rating = (
        data_filtered
        .groupby('recipe_id')['rating']
        .mean()
        .reset_index(name='average_rating')
    )

    dfs = [interaction_count, review_count, rating_count, average_rating]

    result = reduce(
        lambda left,
        right: pd.merge(left, right, on='recipe_id'),
        dfs
    )
    return result


def interactions_and_nutriscore_df(interaction_data, nutriscore_data):
    """
    Merge the interaction data and the nutriscore data.

    Parameters:
    - interaction_data: DataFrame, the interaction data.
    - nutriscore_data: DataFrame, the nutriscore data.

    Returns:
    - merged_data: DataFrame, the merged data.
    """
    merged_data = pd.merge(
        interaction_data,
        nutriscore_data,
        left_on='recipe_id',
        right_on='id'
    )
    columns_to_keep = [
        'id',
        'interaction_count',
        'review_count',
        'rating_count',
        'average_rating',
        'nutriscore',
        'label'
    ]
    filtered_data = merged_data[columns_to_keep]
    return filtered_data


def label_analysis(data):
    """
    Compute the average rating, the number of interactions, the number of
    recipes and the interaction/recipe ratio for each label.

    Parameters:
    - data: DataFrame, the merged data.

    Returns:
    - merged_counts: DataFrame, the result of the computation
    """
    averate_rating_per_label = (
        data
        .groupby('label')['average_rating']
        .mean()
        .reset_index(name='average_rating')
    )
    interaction_count_per_label = (
        data
        .groupby('label')['interaction_count']
        .sum()
        .reset_index(name='interaction_count')
    )
    recipe_count_per_label = (
        data
        .groupby('label')['id']
        .nunique()
        .reset_index(name='recipe_count')
    )

    dfs = [
        averate_rating_per_label,
        interaction_count_per_label,
        recipe_count_per_label
    ]

    merged_counts = reduce(
        lambda left,
        right: pd.merge(left, right, on='label'),
        dfs
    )

    merged_counts['interaction_recipe_ratio'] = (
        merged_counts['interaction_count'] / merged_counts['recipe_count']
    )
    return merged_counts


def main():
    result = interactions_df(interaction_data)
    print(result.head())
    merged_data = interactions_and_nutriscore_df(result, nutriscore_data)
    print(merged_data.head())
    label_analysis_result = label_analysis(merged_data)
    print(label_analysis_result)


if __name__ == '__main__':
    main()

result = interactions_df(interaction_data)
merged_data = interactions_and_nutriscore_df(result, nutriscore_data)

# matrice de correlation pour les colonnes de merged_data
columns_of_interest = ['interaction_count', 'average_rating', 'nutriscore']
matrix = merged_data[columns_of_interest].corr()

label_analysis_result = label_analysis(merged_data)

plt.figure(figsize=(12, 8))
sns.heatmap(matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation matrix')

plt.show()
