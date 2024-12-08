import logging
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

    Parameters
    ----------
    path_recipes_data: str
        The path to the raw recipes data.
    path_nutriscore_data: str
        The path to the nutriscore data.
    data: pd.DataFrame
        The data to use directly.

    Methods
    -------
    load_and_preprocess_recipes_data
        Preprocesses the raw recipes data and return the formatted nutrition
        data.
    merge_data
        Merge the raw data with the nutriscore data on the 'id' column.
    filter_columns
        Filter the merged data to keep only the specified columns.
    """
    def __init__(
            self,
            path_recipes_data=None,
            path_nutriscore_data=None,
            data=None
    ):
        """
        Initialize the class.

        Parameters
        ----------
        path_recipes_data: str
            The path to the raw recipes data.
        path_nutriscore_data: str
            The path to the nutriscore data.
        data: pd.DataFrame
            The data to use directly.

        Returns
        -------
        None
        """
        self.path_recipes_data = path_recipes_data
        self.path_nutriscore_data = path_nutriscore_data
        self.data = data

    def load_and_preprocess_recipes_data(self):
        """
        Preprocesses the raw recipes data and return the formatted
        nutrition data.

        Parameters
        ----------
        path_recipes_data: str
            The path to the raw recipes data.
        configs: dict
            The configurations for the preprocessing.

        Returns
        -------
        recipes_data: DataFrame
            The formatted nutrition data.
        """
        if self.data is not None:
            logger.debug("Data provided directly.")
            return self.data

        else:
            logger.debug(f"Data loaded from {self.path_recipes_data}.")
            recipes_data = Preprocessing(self.path_recipes_data, configs)
            return recipes_data.get_formatted_nutrition()

    def merge_data(self, raw_data, nutriscore_data):
        """
        Merge the raw data with the nutriscore data on the 'id' column.

        Parameters
        ----------
        raw_data: DataFrame
            The raw data to merge.
        nutriscore_data: DataFrame
            The nutriscore data to merge.

        Returns
        -------
        merged_data: DataFrame
            The merged data.
        """
        logger.info("Merging the raw data with the nutriscore data.")
        return pd.merge(raw_data, nutriscore_data, on='id')

    def filter_columns(self, merged_data, columns_to_keep):
        """
        Filter the merged data to keep only the specified columns.

        Parameters
        ----------
        merged_data: DataFrame
            The data to filter.
        columns_to_keep: list
            The columns to keep.

        Returns
        -------
        filtered_data: DataFrame
            The filtered data.
        """
        logger.info("Filtering the merged data.")
        return merged_data[columns_to_keep]


class LinearRegressionNutrition:
    """
    This class is used to perform a linear regression on the nutrition data.

    Parameters
    ----------
    data: DataFrame
        The data to fit the model.
    target: str
        The target column for the regression.
    features: list
        The feature columns for the regression.

    Methods
    -------
    linear_regression
        Uses a linear regression model to predict the target variable based on
        the features.
    plot_linear_regression
        Plots the actual vs predicted values of the target variable.
    bootstrap_confidence_interval
        Calculates bootstrap confidence intervals for the coefficients of a
        linear regression.
    """
    def __init__(self, data, target, features):
        """
        Initialize the class.

        Parameters
        ----------
        data: DataFrame
            The data to fit the model.
        target: str
            The target column for the regression.
        features: list
            The feature columns for the regression.

        Returns
        -------
        None
        """
        self.data = data
        self.target = target
        self.features = features

    def linear_regression(self):
        """
        Uses a linear regression model to predict the target variable based
        on the features.

        Parameters
        ----------
        data: DataFrame
            The data to fit the model.
        target: str
            The target column for the regression.
        features: list
            The feature columns for the regression.

        Returns
        -------
        mse: float
            The mean squared error of the model.
        r2: float
            The R-squared score of the model.
        intercept: float
            The intercept of the model.
        coefficients: DataFrame
            The coefficients of the model.
        y_test: Series
            The true values of the target.
        y_pred: Series
            The predicted values of the target.
        """
        X = self.data[self.features]
        logger.debug(f"Features: {self.features}")
        y = self.data[self.target]
        logger.debug(f"Target: {self.target}")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
            )
        logger.info("Fitting the linear regression model.")
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
        logger.debug(f"Mean Squared Error: {mse}")
        logger.debug(f"R-squared Score: {r2}")
        logger.debug(f"Intercept: {intercept}")
        logger.debug(f"Coefficients: {coefficients}")
        return mse, r2, intercept, coefficients, y_test, y_pred

    def plot_linear_regression(self, y_test, y_pred):
        """
        Plots the actual vs predicted values of the target variable.

        Parameters
        ----------
        y_test: Series
            The true values of the target.
        y_pred: Series
            The predicted values of the target.

        Returns
        -------
        None
        """
        logger.debug("Plotting the linear regression.")
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
        logger.info("Linear regression plot displayed.")
        return plt.show(block=False)

    def bootstrap_confidence_interval(
            self,
            num_bootstrap_samples=1000,
            confidence_level=0.95
    ):
        """
        Calculates bootstrap confidence intervals for the coefficients of a
        linear regression.

        Parameters
        ----------
        data: DataFrame
            The data to resample.
        target: str
            The target column for the regression.
        features: list
            The feature columns for the regression.
        num_bootstrap_samples: int
            The number of bootstrap samples to generate.
        confidence_level: float
            The confidence level for the confidence interval.

        Returns
        -------
        intervals: dict
            The confidence intervals for each coefficient.
        """
        logger.debug("Calculating bootstrap confidence intervals.")
        coefficients = []

        for _ in range(num_bootstrap_samples):
            bootstrap_sample = resample(self.data)

            X_bootstrap = bootstrap_sample[self.features]
            y_bootstrap = bootstrap_sample[self.target]

            model = LinearRegression()
            model.fit(X_bootstrap, y_bootstrap)

            coefficients.append(model.coef_)

        coefficients_df = pd.DataFrame(coefficients, columns=self.features)
        logger.debug(f"Coefficients DataFrame: {coefficients_df.head()}")

        intervals = {}
        for feature in self.features:
            lower_bound = np.percentile(
                coefficients_df[feature], (1 - confidence_level) / 2 * 100
            )
            upper_bound = np.percentile(
                coefficients_df[feature], (1 + confidence_level) / 2 * 100
            )
            intervals[feature] = (lower_bound, upper_bound)
        logger.debug(f"Confidence intervals: {intervals}")
        logger.info("Bootstrap confidence intervals calculated.")
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

    Parameters
    ----------
    coefficients: DataFrame
        The coefficients of the linear regression model.

    Returns
    -------
    calories_per_gram: DataFrame
        The number of calories per gram of proteins, fat, and carbohydrates.
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
    logger.debug(f"Calories per gram: {calories_per_gram}")
    logger.info("Calories per gram calculated.")
    return pd.DataFrame(calories_per_gram, index=['Value'])


def main():
    """
    Perform a linear regression on the nutrition data to predict the calories
    per portion based on the percentage of fat, sugar, sodium, protein,
    saturated fat, and carbohydrates.

    Returns
    -------
    None
    """
    logger.info("Starting linear regression on nutrition data.")
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
    logger.debug(f"Merged data: {merged_data.head()}")
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
    logger.debug(f"Mean Squared Error: {mse}")
    logger.debug(f"R-squared Score: {r2}")
    logger.debug(f"Intercept: {intercept}")
    logger.debug(f"Coefficients: {coefficients}")

    linear_regression_nutrition.plot_linear_regression(y_test, y_pred)

    logger.info(calories_per_gram(coefficients))

    intervals = linear_regression_nutrition.bootstrap_confidence_interval()
    for feature, interval in intervals.items():
        logger.info(f"Bootstrap confidence interval for {feature}: {interval}")
    return None


if __name__ == '__main__':
    main()
