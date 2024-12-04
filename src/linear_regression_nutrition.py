import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample
from sklearn.metrics import mean_squared_error, r2_score
from preprocess import Preprocessing, configs

logger = logging.getLogger("linear_regression_nutrition")

class DataPreprocessing:
    """
    This class is used to preprocess the raw recipes data and merge it with the
    nutriscore data.

    Attributes:
    - path_recipes_data: str, the path to the raw recipes data.
    - path_nutriscore_data: str, the path to the nutriscore data.

    Methods:
    - load_and_preprocess_recipes_data: Preprocesses the raw recipes data and
    return the formatted nutrition data.
    - merge_data: Merge the raw data with the nutriscore data on the 'id'
    column.
    - filter_columns: Filter the merged data to keep only the specified 
    columns.
    """
    def __init__(self, path_recipes_data=None, path_nutriscore_data=None, data=None):
        self.path_recipes_data = path_recipes_data
        self.path_nutriscore_data = path_nutriscore_data
        self.data = data

    def load_and_preprocess_recipes_data(self):
        """
        Preprocesses the raw recipes data and return the formatted 
        nutrition data.

        Parameters:
        - path_recipes_data: str, the path to the raw recipes data.
        - configs: dict, the configurations for the preprocessing.

        Returns:
        - recipes_data: DataFrame, the formatted nutrition data.
        """
        if self.data is not None:
            return self.data
        else:
            recipes_data = Preprocessing(self.path_recipes_data, configs)
            return recipes_data.get_formatted_nutrition()

    def merge_data(self, raw_data, nutriscore_data):
        """
        Merge the raw data with the nutriscore data on the 'id' column.

        Parameters:
        - raw_data: DataFrame, the raw data to merge.
        - nutriscore_data: DataFrame, the nutriscore data to merge.

        Returns:
        - merged_data: DataFrame, the merged data.
        """
        return pd.merge(raw_data, nutriscore_data, on='id')


    def filter_columns(self, merged_data, columns_to_keep):
        """
        Filter the merged data to keep only the specified columns.

        Parameters:
        - merged_data: DataFrame, the data to filter.
        - columns_to_keep: list, the columns to keep.

        Returns:
        - filtered_data: DataFrame, the filtered data.    
        """
        return merged_data[columns_to_keep]


class LinearRegressionNutrition:
    """
    This class is used to perform a linear regression on the nutrition data.

    Attributes:
    - data: DataFrame, the data to fit the model.
    - target: str, the target column for the regression.
    - features: list, the feature columns for the regression.

    Methods:
    - linear_regression: Uses a linear regression model to predict the target
    variable based on the features.
    - plot_linear_regression: Plots the actual vs predicted values of the
    target variable.
    - bootstrap_confidence_interval: Calculates bootstrap confidence intervals
    for the coefficients of a linear regression.
    """
    def __init__(self, data, target, features):
        self.data = data
        self.target = target
        self.features = features

    def linear_regression(self):
        """
        Uses a linear regression model to predict the target variable based 
        on the features.

        Parameters:
        - data: DataFrame, the data to fit the model.
        - target: str, the target column for the regression.
        - features: list, the feature columns for the regression.

        Returns:
        - mse: float, the mean squared error of the model.
        - r2: float, the R-squared score of the model.
        - intercept: float, the intercept of the model.
        - coefficients: DataFrame, the coefficients of the model.
        - y_test: Series, the true values of the target.
        - y_pred: Series, the predicted values of the target.
        """
        X = self.data[self.features]
        y = self.data[self.target]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
            )
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        coefficients = pd.DataFrame(
            model.coef_,
            index=self.features,
            columns=['Coefficient']
        )
        intercept = model.intercept_
        return mse, r2, intercept, coefficients, y_test, y_pred

      
    def plot_linear_regression(self, y_test, y_pred):
        """
        Plots the actual vs predicted values of the target variable.

        Parameters:
        - y_test: Series, the true values of the target.
        - y_pred: Series, the predicted values of the target

        Returns:
        - None
        """
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, color='blue', label='Predicted vs Actual')
        plt.plot(
            [y_test.min(), y_test.max()],
            [y_test.min(), y_test.max()],
            color='red',
            linewidth=2,
            label='Ideal Fit'
            )
        plt.xlabel('Actual Calories per Portion')
        plt.ylabel('Predicted Calories per Portion')
        plt.title('Actual vs Predicted Calories per Portion')
        plt.legend()
        plt.grid(True)
        return plt.show(block=False)

      
    def bootstrap_confidence_interval(
            self,
            num_bootstrap_samples=1000,
            confidence_level=0.95
    ):
        """
        Calculates bootstrap confidence intervals for the coefficients of a
        linear regression.

        Parameters:
        - data: DataFrame, the data to resample.
        - target: str, the target column for the regression.
        - features: list, the feature columns for the regression.
        - num_bootstrap_samples: int, the number of bootstrap samples to 
        generate.
        - confidence_level: float, the confidence level for the confidence
        interval.

        Returns:
        - intervals: dict, the confidence intervals for each coefficient.
        """
        coefficients = []

        for _ in range(num_bootstrap_samples):
            # Rééchantillonner les données avec remplacement
            bootstrap_sample = resample(self.data)

            # Séparer les features et la variable cible
            X_bootstrap = bootstrap_sample[self.features]
            y_bootstrap = bootstrap_sample[self.target]

            # Créer et entraîner le modèle de régression linéaire
            model = LinearRegression()
            model.fit(X_bootstrap, y_bootstrap)

            # Stocker les coefficients
            coefficients.append(model.coef_)

        # Convertir les coefficients en DataFrame
        coefficients_df = pd.DataFrame(coefficients, columns=self.features)

        # Calculer les intervalles de confiance
        intervals = {}
        for feature in self.features:
            lower_bound = np.percentile(
                coefficients_df[feature], (1 - confidence_level) / 2 * 100
            )
            upper_bound = np.percentile(
                coefficients_df[feature], (1 + confidence_level) / 2 * 100
            )
            intervals[feature] = (lower_bound, upper_bound)

        return intervals


def calories_per_gram(
        coefficients,
        daily_g_proteins=50,
        daily_g_fat=70,
        daily_g_carbs=260
):
    """
    Calculates the number of calories per gram of proteins, fat, and
    carbohydrates, based on the recommended daily amount of nutrients in grams.

    Parameters:
    - coefficients: DataFrame, the coefficients of the linear regression model.

    Returns:
    - calories_per_gram: DataFrame, the number of calories per gram of
    proteins, fat, and carbohydrates.
    """
    cal_per_g_proteins = (
        coefficients.loc['protein_%', 'Coefficient'] * 100 / daily_g_proteins
    )
    cal_per_g_fat = (
        coefficients.loc['total_fat_%', 'Coefficient']*100/daily_g_fat
    )
    cal_per_g_carbs = (
        coefficients.loc['carbs_%', 'Coefficient']*100/daily_g_carbs
    )
    calories_per_gram = {
        'Calories per gram of Protein': [cal_per_g_proteins],
        'Calories per gram of Fat': [cal_per_g_fat],
        'Calories per gram of Carbohydrates': [cal_per_g_carbs]
    }
    return pd.DataFrame(calories_per_gram, index=['Value'])


def main():
    path_recipes_data = './datasets/RAW_recipes.csv'
    path_nutriscore_data = (
        './datasets/nutrition_table_nutriscore_no_outliers.csv'
    )
    
    data_preprocessing = DataPreprocessing(
        path_recipes_data,
        path_nutriscore_data
    )

    raw_data = data_preprocessing.load_and_preprocess_recipes_data()
    nutriscore_data = pd.read_csv(path_nutriscore_data)
    merged_data = data_preprocessing.merge_data(raw_data, nutriscore_data)

    columns_to_keep = [
        'id',
        'calories',
        'total_fat_%',
        'sugar_%',
        'sodium_%',
        'protein_%',
        'sat_fat_%',
        'carbs_%'
    ]

    filtered_data = data_preprocessing.filter_columns(
        merged_data,
        columns_to_keep
    )
    features = ['total_fat_%', 'protein_%', 'carbs_%']
    target = 'calories'

    linear_regression_nutrition = LinearRegressionNutrition(
        filtered_data,
        target,
        features
    )

    mse, r2, intercept, coefficients, y_test, y_pred = (
        linear_regression_nutrition.linear_regression()
    )
    
    linear_regression_nutrition.plot_linear_regression(y_test, y_pred)

    print(calories_per_gram(coefficients))

    intervals = linear_regression_nutrition.bootstrap_confidence_interval()
    for feature, interval in intervals.items():
        print(f"Bootstrap confidence interval for {feature}: {interval}")
    return None


if __name__ == '__main__':
    main()
