import logging
from functools import reduce
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


logger = logging.getLogger("interaction_correlation_analysis")


class InteractionData:
    """
    Class to analyze the interaction data.

    Parameters
    ----------
    data: pd.DataFrame
        The interaction data.

    Methods
    -------
    interactions_df()
        Compute the number of interactions, reviews, ratings and average rating
        for each recipe.
    merge_interaction_nutriscore()
        Merge the interaction data and the nutriscore data.
    interaction_correlation_matrix()
        Calculate the correlation matrix of a DataFrame, for chosen columns.
    plot_interaction_correlation_matrix()
        Plot the correlation matrix of the data.
    """
    def __init__(self, path=None, data=None):
        """
        Method to initialize the class.

        Parameters
        ----------
        path: str
            The path to the data file.
        data: pd.DataFrame
            The data to analyze.

        Returns
        -------
        None
        """
        if path is not None:
            self.data = pd.read_csv(path, sep=',')
            logger.info(f"Data loaded from {path}.")
        else:
            self.data = data
            logger.info("Data provided directly.")

    def interactions_df(self):
        """
        Compute the number of interactions, reviews, ratings and average rating
        for each recipe.

        Parameters
        ----------
        data: DataFrame
            The interaction data.

        Returns
        -------
        result: DataFrame
            The result of the computation.
        """
        logger.debug("Starting interactions_df computation.")
        data_filtered = self.data.dropna(subset=['rating', 'review'])
        interaction_count = (
            data_filtered
            .groupby('recipe_id')
            .size()
            .reset_index(name='interaction_count')
        )
        logger.debug(f"Interaction count computed: {interaction_count.head()}")

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
        logger.debug(f"Merging dataframes: {[df.shape for df in dfs]}")

        result = reduce(
            lambda left,
            right: pd.merge(left, right, on='recipe_id'),
            dfs
        )
        logger.info("Interactions dataframe created successfully.")
        return result

    def merge_interaction_nutriscore(self, nutriscore_data, columns_to_keep):
        """
        Merge the interaction data and the nutriscore data.

        Parameters
        ----------
        nutriscore_data: DataFrame
            The nutriscore data.
        columns_to_keep: list
            The columns to keep in the merged data.

        Returns
        ------
        filtered_data: DataFrame
            The merged data.
        """
        try:
            logger.debug("Merging interaction data with nutriscore data.")
            interaction_data = self.interactions_df()
            merged_data = pd.merge(
                interaction_data,
                nutriscore_data,
                left_on='recipe_id',
                right_on='id'
            )
            logger.debug(f"Merged data shape: {merged_data.shape}")

            filtered_data = merged_data[columns_to_keep]
            logger.info(f"Filtered data with columns: {columns_to_keep}.")
            return filtered_data
        except KeyError as e:
            logger.error(f"Missing key in data: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while merging data: {e}")
            raise

    def interaction_correlation_matrix(self, merged_data, columns_of_interest):
        """
        Calculate the correlation matrix of a DataFrame, for chosen columns.

        Parameters
        ----------
        merged_data: DataFrame
            The data to calculate the correlation matrix.
        columns_of_interest: list
            The columns to include in the correlation matrix.

        Returns
        -------
        correlation_matrix: DataFrame
            The correlation matrix of the data.
        """
        logger.debug("Calculating correlation matrix.")
        matrix = merged_data[columns_of_interest].corr()
        logger.debug(f"Correlation matrix calculated: {matrix.head()}")
        return matrix

    def plot_interaction_correlation_matrix(
            self,
            merged_data,
            columns_of_interest
    ):
        """
        Plot the correlation matrix of the data.

        Parameters
        ----------
        merged_data: DataFrame
            The data to plot.
        columns_of_interest: list
            The columns to include in the correlation matrix.

        Returns
        -------
        None
        """
        logger.debug("Plotting interaction correlation matrix.")
        plt.figure(figsize=(12, 8))
        corr_matrix = self.interaction_correlation_matrix(
            merged_data,
            columns_of_interest
        )
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation matrix')
        plt.show()
        logger.info("Correlation matrix plot displayed.")


class LabelAnalysis:
    """
    Class to analyze the labels.

    Methods
    ------
    label_analysis(data)
        Compute the average rating, the number of interactions,
    the number of recipes and the interaction/recipe ratio for each label.
    """
    @staticmethod
    def label_analysis(data):
        """
        Compute the average rating, the number of interactions, the number of
        recipes and the interaction/recipe ratio for each label.

        Parameters
        ----------
        data: DataFrame
            The data to analyze.

        Returns
        -------
        merged_counts: DataFrame
            The result of the computation.
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
    """
    Main function to analyze the interaction data.

    Returns
    -------
    None
    """
    logger.info("Starting main function")
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

    logger.debug(result.head())
    logger.debug(merged_data.head())
    logger.debug(label_analysis_result)
    logger.debug(corr_mat)

    interaction_data.plot_interaction_correlation_matrix(
        merged_data,
        columns_of_interest
    )
    logger.info("Finished main function")


if __name__ == '__main__':
    main()
