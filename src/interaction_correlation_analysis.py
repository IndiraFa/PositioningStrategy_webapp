from functools import reduce
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger("interaction_correlation_analysis")


class InteractionData:
    """
    Class to analyze the interaction data.

    Attributes:
    - data: DataFrame, the interaction data.

    Methods:
    - interactions_df: Compute the number of interactions, reviews, ratings and
    average rating for each recipe.
    - merge_interaction_nutriscore: Merge the interaction data and the
    nutriscore data.
    - interaction_correlation_matrix: Calculate the correlation matrix of a
    DataFrame, for chosen columns.
    - plot_interaction_correlation_matrix: Plot the correlation matrix of the
    data.
    """
    def __init__(self, path=None, data=None):
        if path is not None:
            self.data = pd.read_csv(path, sep=',')
        else:
            self.data = data
        # self.interactions_df = self.interactions_df()

    def interactions_df(self):
        """
        Compute the number of interactions, reviews, ratings and average rating
        for each recipe.

        Parameters:
        - data: DataFrame, the interaction data.

        Returns:
        - result: DataFrame, the result of the computation.
        """
        data_filtered = self.data.dropna(subset=['rating', 'review'])
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

    def merge_interaction_nutriscore(self, nutriscore_data, columns_to_keep):
        """
        Merge the interaction data and the nutriscore data.

        Parameters:
        - interaction_data: DataFrame, the interaction data.
        - nutriscore_data: DataFrame, the nutriscore data.

        Returns:
        - merged_data: DataFrame, the merged data.
        """
        interaction_data = self.interactions_df()
        merged_data = pd.merge(
            interaction_data,
            nutriscore_data,
            left_on='recipe_id',
            right_on='id'
        )

        filtered_data = merged_data[columns_to_keep]
        return filtered_data

    def interaction_correlation_matrix(self, merged_data, columns_of_interest):
        """
        Calculate the correlation matrix of a DataFrame, for chosen columns.

        Parameters:
        - data: DataFrame, the data to calculate the correlation matrix.
        - columns_of_interest: list, the columns to include in the correlation
        matrix.

        Returns:
        - correlation_matrix: DataFrame, the correlation matrix of the data.
        """
        matrix = merged_data[columns_of_interest].corr()
        return matrix

    def plot_interaction_correlation_matrix(
            self,
            merged_data,
            columns_of_interest
    ):
        """
        Plot the correlation matrix of the data.
        """
        plt.figure(figsize=(12, 8))
        corr_matrix = self.interaction_correlation_matrix(
            merged_data,
            columns_of_interest
        )
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation matrix')
        plt.show()


class LabelAnalysis:
    """
    Class to analyze the labels.

    Methods:
    - label_analysis: Compute the average rating, the number of interactions,
    the number of recipes and the interaction/recipe ratio for each label.
    """
    @staticmethod
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
    path_interaction = './datasets/RAW_interactions.csv'
    path_nutriscore = './datasets/nutrition_table_nutriscore_no_outliers.csv'
    nutriscore_data = pd.read_csv(path_nutriscore, sep=',')
    columns_to_keep = [
        'id',
        'interaction_count',
        'review_count',
        'rating_count',
        'average_rating',
        'nutriscore',
        'label'
    ]
    columns_of_interest = ['interaction_count', 'average_rating', 'nutriscore']
    interaction_data = InteractionData(path=path_interaction)
    result = interaction_data.data
    merged_data = interaction_data.merge_interaction_nutriscore(
        nutriscore_data,
        columns_to_keep
    )
    label_analysis_result = LabelAnalysis.label_analysis(merged_data)
    corr_mat = interaction_data.interaction_correlation_matrix(
        merged_data,
        columns_of_interest
    )

    print(result.head())
    print(merged_data.head())
    print(label_analysis_result)
    print(corr_mat)

    interaction_data.plot_interaction_correlation_matrix(
        merged_data,
        columns_of_interest
    )


if __name__ == '__main__':
    main()
