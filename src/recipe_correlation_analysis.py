import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from linear_regression_nutrition import DataPreprocessing

logger = logging.getLogger("recipe_correlation_analysis")


class CorrelationAnalysis(DataPreprocessing):
    """
    Class to analyze the correlation between the recipes and the nutriscore
    data.

    Parameters
    ----------
    columns_to_keep: list
        The columns to keep in the data.
    columns_of_interest: list
        The columns to include in the correlation matrix.

    path_recipes_data: str
        The path to the recipes data file.
    path_nutriscore_data: str
        The path to the nutriscore data file.
    data: pd.DataFrame
        The data to analyze.

    Methods
    -------
    correlation_matrix()
        Calculate the correlation matrix of a DataFrame, for chosen columns.
    plot_correlation_matrix()
        Plot the correlation matrix of the data.
    """
    def __init__(
            self, columns_to_keep, columns_of_interest,
            path_recipes_data=None, path_nutriscore_data=None, data=None
    ):
        """
        Method to initialize the class. If the data is not provided, it will
        load the data from the paths.

        Parameters
        ----------
        columns_to_keep: list
            The columns to keep in the data.
        columns_of_interest: list
            The columns to include in the correlation matrix.

        path_recipes_data: str
            The path to the recipes data file.
        path_nutriscore_data: str
            The path to the nutriscore data file.
        data: pd.DataFrame
            The data to analyze.

        Returns
        -------
        None
        """
        if data is not None:
            super().__init__(data=data)
            self.data = data
            logger.info("Data provided directly.")
        else:
            super().__init__(path_recipes_data, path_nutriscore_data)
            self.recipes_data = pd.read_csv(self.path_recipes_data)
            self.nutriscore_data = pd.read_csv(self.path_nutriscore_data)
            self.data = self.merge_data(
                self.recipes_data, self.nutriscore_data
            )
            logger.info(f"Data loaded from {path_recipes_data} and \
                        {path_nutriscore_data}.")

        self.columns_to_keep = columns_to_keep
        self.columns_of_interest = columns_of_interest
        self.filtered_data = self.filter_columns(self.data, columns_to_keep)

    def correlation_matrix(self):
        """
        Calculate the correlation matrix of a DataFrame, for chosen columns.

        Parameters
        ----------
        data: DataFrame
            The data to calculate the correlation matrix.
        columns_of_interest: list
            The columns to include in the correlation matrix.

        Returns
        -------
        correlation_matrix: DataFrame
            The correlation matrix of the data.
        """
        logger.debug("Calculating the correlation matrix.")
        filtered_data_corr = self.filtered_data[self.columns_of_interest]
        correlation_matrix_value = filtered_data_corr.corr()
        logger.debug(
            f"Correlation matrix calculated: {correlation_matrix_value}."
        )
        logger.info("Correlation matrix calculated.")
        return correlation_matrix_value

    def plot_correlation_matrix(self):
        """
        Plot the correlation matrix of the data.

        Arguments
        ---------
        None

        Returns
        -------
        None
        """
        logger.debug("Plotting the correlation matrix.")
        corr_matrix = self.correlation_matrix()
        plt.figure(figsize=(12, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation Matrix')
        plt.show()
        logger.info("Correlation matrix plot displayed.")


def main():
    """
    Main function to run the correlation analysis.

    Arguments
    ---------
    None

    Returns
    -------
    None
    """
    logger.info("Starting the correlation analysis.")
    path_recipes_data = './datasets/RAW_recipes.csv'
    path_nutriscore_data = (
        './datasets/nutrition_table_nutriscore_no_outliers.csv'
    )
    columns_to_keep = [
        'id',
        'dv_calories_%',
        'dv_total_fat_%',
        'dv_sugar_%',
        'dv_sodium_%',
        'dv_protein_%',
        'dv_sat_fat_%',
        'dv_carbs_%',
        'nutriscore',
        'minutes',
        'n_steps',
        'n_ingredients'
    ]
    columns_of_interest = [
        'dv_calories_%',
        'dv_total_fat_%',
        'dv_sugar_%',
        'dv_sodium_%',
        'dv_protein_%',
        'dv_sat_fat_%',
        'dv_carbs_%',
        'nutriscore',
        'minutes',
        'n_steps',
        'n_ingredients'
    ]
    correlation_analysis = CorrelationAnalysis(
        columns_to_keep, columns_of_interest,
        path_recipes_data=path_recipes_data,
        path_nutriscore_data=path_nutriscore_data
    )
    correlation_analysis.plot_correlation_matrix()
    logger.info("Correlation analysis completed.")


if __name__ == '__main__':
    main()
