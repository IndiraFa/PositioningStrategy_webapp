import pandas as pd
# import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample
from sklearn.metrics import mean_squared_error, r2_score
from preprocess import Preprocessing
from preprocess import configs


path_recipes_data = 'src/datasets/RAW_recipes.csv'
path_nutriscore_data = 'src/datasets/nutrition_table_nutriscore_no_outliers.csv'

recipes_data = Preprocessing(path_recipes_data, configs)
raw_data = recipes_data.get_formatted_nutrition()

nutriscore_data = pd.read_csv(path_nutriscore_data)

merged_data = pd.merge(raw_data, nutriscore_data, on='id')
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

filtered_data = merged_data[columns_to_keep]
features = ['total_fat_%', 'protein_%', 'carbs_%']
target = 'calories'

daily_g_proteins = 50
daily_g_fat = 70
daily_g_carbs = 260


def linear_regression(data, target, features):
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
    X = data[features]
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
        )
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    coefficients = pd.DataFrame(model.coef_, features, columns=['Coefficient'])
    intercept = model.intercept_
    return mse, r2, intercept, coefficients, y_test, y_pred


def plot_linear_regression(y_test, y_pred):
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
    return plt.show()


def calories_per_gram(coefficients):
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
        'calories per g of proteins': [cal_per_g_proteins],
        'cal per g of fat': [cal_per_g_fat],
        'cal per g of carbs': [cal_per_g_carbs]
    }
    return pd.DataFrame(calories_per_gram, index=['Value'])


def bootstrap_confidence_interval(
        data,
        target,
        features,
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
    - num_bootstrap_samples: int, the number of bootstrap samples to generate.
    - confidence_level: float, the confidence level for the confidence
    interval.

    Returns:
    - intervals: dict, the confidence intervals for each coefficient.
    """
    coefficients = []

    for _ in range(num_bootstrap_samples):
        # Rééchantillonner les données avec remplacement
        bootstrap_sample = resample(data)
        
        # Séparer les features et la variable cible
        X_bootstrap = bootstrap_sample[features]
        y_bootstrap = bootstrap_sample[target]
        
        # Créer et entraîner le modèle de régression linéaire
        model = LinearRegression()
        model.fit(X_bootstrap, y_bootstrap)
        
        # Stocker les coefficients
        coefficients.append(model.coef_)
    
    # Convertir les coefficients en DataFrame
    coefficients_df = pd.DataFrame(coefficients, columns=features)
    
    # Calculer les intervalles de confiance
    intervals = {}
    for feature in features:
        lower_bound = np.percentile(
            coefficients_df[feature], (1 - confidence_level) / 2 * 100
        )
        upper_bound = np.percentile(
            coefficients_df[feature], (1 + confidence_level) / 2 * 100
        )
        intervals[feature] = (lower_bound, upper_bound)

    return intervals


def main():
    mse, r2, coefficients, y_test, y_pred = linear_regression(
        filtered_data,
        target,
        features
    )
    print(linear_regression(filtered_data, target, features))
    plot_linear_regression(y_test, y_pred)
    print(calories_per_gram(coefficients))

    intervals = bootstrap_confidence_interval(filtered_data, target, features)
    for feature, interval in intervals.items():
        print(f"Bootstrap confidence interval for {feature}: {interval}")
    return None


if __name__ == '__main__':
    main()