import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# from preprocess import Preprocessing

path_recipes_data = './datasets/RAW_recipes.csv'
path_nutriscore_data = './datasets/nutrition_table_nutriscore_no_outliers.csv'
recipes_data = pd.read_csv(path_recipes_data)
nutriscore_data = pd.read_csv(path_nutriscore_data)

# Fusionner les DataFrames sur la colonne 'id'
merged_data = pd.merge(recipes_data, nutriscore_data, on='id')

# changer le 2000 avec valeur du paramètre dv_calories
# Sélectionner les colonnes d'intérêt
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
filtered_data = merged_data[columns_to_keep]


def correlation_matrix(data, columns_of_interest):
    """
    Calculate the correlation matrix of a DataFrame, for chosen columns.
    
    Parameters:
    - data: DataFrame, the data to calculate the correlation matrix.
    - columns_of_interest: list, the columns to include in the correlation
    matrix.
    
    Returns:
    - correlation_matrix: DataFrame, the correlation matrix of the data.
    """
    filtered_data_corr = data[columns_of_interest]
    correlation_matrix_value = filtered_data_corr.corr()
    return correlation_matrix_value


corr_matrix = correlation_matrix(filtered_data, columns_to_keep)

# Afficher la heatmap de la matrice de corrélation
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix')
plt.show()
