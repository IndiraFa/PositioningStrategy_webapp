import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging
from linear_regression_nutrition import DataPreprocessing

logger = logging.getLogger("recipe_correlation_analysis")

class CorrelationAnalysis(DataPreprocessing):
    def __init__(
            self, columns_to_keep, columns_of_interest,
            path_recipes_data=None, path_nutriscore_data=None, data=None
    ):
        if data is not None:
            super().__init__(data=data)
            self.data = data
        else:    
            super().__init__(path_recipes_data, path_nutriscore_data)
            self.recipes_data = pd.read_csv(self.path_recipes_data)
            self.nutriscore_data = pd.read_csv(self.path_nutriscore_data)
            self.data = self.merge_data(
                self.recipes_data, self.nutriscore_data
            )

        self.columns_to_keep = columns_to_keep
        self.columns_of_interest = columns_of_interest
        self.filtered_data = self.filter_columns(self.data, columns_to_keep)
        
    def correlation_matrix(self):
        """
        Calculate the correlation matrix of a DataFrame, for chosen columns.

        Parameters:
        - data: DataFrame, the data to calculate the correlation matrix.
        - columns_of_interest: list, the columns to include in the correlation
        matrix.

        Returns:
        - correlation_matrix: DataFrame, the correlation matrix of the data.
        """
        filtered_data_corr = self.filtered_data[self.columns_of_interest]
        correlation_matrix_value = filtered_data_corr.corr()
        return correlation_matrix_value
    
    def plot_correlation_matrix(self):
        """
        Plot the correlation matrix of the data.
        Arguments:
        - None
        Returns:
        - None
        """
        corr_matrix = self.correlation_matrix()
        plt.figure(figsize=(12, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
        plt.title('Correlation Matrix')
        plt.show()



def main():
    path_recipes_data = './datasets/RAW_recipes.csv'
    path_nutriscore_data = './datasets/nutrition_table_nutriscore_no_outliers.csv'
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

if __name__ == '__main__':
    main()
