import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from functools import reduce


class InteractionCorrelationAnalysis:
    def __init__(self, interaction_data, nutriscore_data):
        self.interaction_data = interaction_data
        self.nutriscore_data = nutriscore_data
        self.result = self.interactions_df()
        self.merged_data = self.interactions_and_nutriscore_df()
        self.columns_of_interest = [
            'interaction_count', 'average_rating', 'nutriscore'
        ]
        self.matrix = self.correlation_matrix(
            self.merged_data, self.columns_of_interest
        )
        self.label_analysis_result = self.label_analysis(self.merged_data)

        self.heatmap(self.matrix)

    def interactions_df(self):
        """
        Calculate the number of interactions, reviews, ratings and average
        rating per recipe.

        Parameters:
        - data: DataFrame, the interaction data.

        Returns:
        - result: DataFrame, the result of the calculation.
        """
        data_filtered = self.interaction_data.dropna(
            subset=['rating', 'review']
        )
        interaction_count = (
            data_filtered.groupby('recipe_id')
            .size()
            .reset_index(name='interaction_count')
        )
        review_count = (
            data_filtered.groupby('recipe_id')['rating']
            .count()
            .reset_index(name='review_count')
        )
        rating_count = (
            data_filtered.groupby('recipe_id')['rating']
            .count().
            reset_index(name='rating_count')
        )
        average_rating = (
            data_filtered.groupby('recipe_id')['rating']
            .mean().
            reset_index(name='average_rating')
        )
        dfs = [interaction_count, review_count, rating_count, average_rating]
        result = reduce(
            lambda left, right: pd.merge(left, right, on='recipe_id'),
            dfs
        )
        return result

    def interactions_and_nutriscore_df(self):
        """
        Merge the interaction data and the nutriscore data.

        Parameters:
        - interaction_data: DataFrame, the interaction data.
        - nutriscore_data: DataFrame, the nutriscore data.

        Returns:
        - merged_data: DataFrame, the merged data.
        """
        merged_data = pd.merge(
            self.result,
            self.nutriscore_data,
            left_on='recipe_id',
            right_on='id'
        )
        columns_to_keep = [
            'id', 'interaction_count', 'review_count',
            'rating_count', 'average_rating', 'nutriscore', 'label'
        ]
        filtered_data = merged_data[columns_to_keep]
        return filtered_data

    def label_analysis(self, data):
        """
        Calculate the average rating, interaction count, recipe count
        and interaction/recipe ratio per label.

        Parameters:
        - data: DataFrame, the data containing the labels.

        Returns:
        - merged_counts: DataFrame, the result of the calculation.
        """
        averate_rating_per_label = (
            data.groupby('label')['average_rating']
            .mean()
            .reset_index(name='average_rating')
        )
        interaction_count_per_label = (
            data.groupby('label')['interaction_count']
            .sum()
            .reset_index(name='interaction_count')
        )
        recipe_count_per_label = (
            data.groupby('label')['id']
            .nunique()
            .reset_index(name='recipe_count')
        )
        dfs = [
            averate_rating_per_label,
            interaction_count_per_label,
            recipe_count_per_label
        ]
        merged_counts = reduce(
            lambda left, right: pd.merge(left, right, on='label'), dfs
        )
        merged_counts['interaction_recipe_ratio'] = (
            merged_counts['interaction_count'] / merged_counts['recipe_count']
        )
        return merged_counts

    def correlation_matrix(self, data, columns):
        matrix = data[columns].corr()
        return matrix

    def heatmap(self, data):
        plt.figure(figsize=(12, 8))
        sns.heatmap(data, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation matrix')
        plt.show()
        return


def main():
    path = (
        '/Users/fabreindira/Library/CloudStorage/'
        'OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/'
        'Projet_kitbigdata/data_base/RAW_interactions.csv'
    )
    interaction_data = pd.read_csv(path, sep=',')

    path2 = 'nutrition_table_nutriscore_no_outliers.csv'
    nutriscore_data = pd.read_csv(path2, sep=',')

    analysis = InteractionCorrelationAnalysis(
        interaction_data, nutriscore_data
    )
    print(analysis.result.head())
    print(analysis.merged_data.head())
    print(analysis.label_analysis_result)
    analysis.heatmap(analysis.matrix)

    return (
        analysis.result,
        analysis.merged_data,
        analysis.label_analysis_result,
        analysis.matrix
    )


if __name__ == '__main__':
    main()
