import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from preprocess import Preprocessing

# Charger les données
path_recipes_data = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Projet_kitbigdata/data_base/RAW_recipes.csv'
path_nutriscore_data = '/Users/fabreindira/Library/CloudStorage/OneDrive-telecom-paristech.fr/MS_BGD/KitBigData/Webapp_git/src/nutrition_table_nutriscore_no_outliers.csv'
recipes_data = pd.read_csv(path_recipes_data)
nutriscore_data = pd.read_csv(path_nutriscore_data) 

# Fusionner les DataFrames sur la colonne 'id'
merged_data = pd.merge(recipes_data, nutriscore_data, on='id')

#changer le 2000 avec valeur du paramètre dv_calories
# Sélectionner les colonnes d'intérêt
columns_to_keep = ['id', 'dv_calories_%', 'dv_total_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%', 'dv_sat_fat_%', 'dv_carbs_%', 'nutriscore', 'minutes', 'n_steps', 'n_ingredients'] 
filtered_data = merged_data[columns_to_keep]
#filtered_data ['calories_per_portion'] = filtered_data['dv_calories_%'] * 2000 / 100

# Calculer la matrice de corrélation
#correlation_matrix = filtered_data.corr()


def correlation_matrix(data, columns_of_interest):
    """
    Calculate the correlation matrix of a DataFrame, for chosen columns.
    
    Parameters:
    - data: DataFrame, the data to calculate the correlation matrix.
    - columns_of_interest: list, the columns to include in the correlation matrix.
    
    Returns:
    - correlation_matrix: DataFrame, the correlation matrix of the data.
    """
    filtered_data = data[columns_of_interest]
    correlation_matrix = filtered_data.corr()
    return correlation_matrix


corr_matrix = correlation_matrix(filtered_data, columns_to_keep)

#Afficher la heatmap de la matrice de corrélation
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix')
plt.show()

# Sélectionner les colonnes d'intérêt
#columns_of_interest = ['calories_per_portion', 'dv_calories_%', 'dv_total_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%', 'dv_sat_fat_%', 'dv_carbs_%', 'nutriscore', 'minutes', 'n_steps', 'n_ingredients'] 

# Créer des scatter plots pour visualiser la relation entre le Nutri-Score et les autres colonnes
# for column in columns_of_interest:
#     if column != 'nutriscore':
#         plt.figure(figsize=(8, 6))
#         sns.scatterplot(x=merged_data['nutriscore'], y=merged_data[column])
#         plt.title(f'Corrélation entre Nutri-Score et {column}')
#         plt.xlabel('Nutri-Score')
#         plt.ylabel(column)
#         plt.show()

#regression linéaire

#instance de la classe preprocessing
# configs = {
#         'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
#         'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
#         'dv_calories': 2000
# }
# recipes_data_2 = Preprocessing(path_recipes_data, configs)

# raw_data = recipes_data_2.get_formatted_nutrition()
# merged_data_2 = pd.merge(raw_data, nutriscore_data, on='id')
# columns_to_keep_2 = ['id', 'calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'] 
# filtered_data_2 = merged_data_2[columns_to_keep_2]


# features = ['total_fat_%', 'protein_%', 'carbs_%']
# target = 'calories'

# X = filtered_data_2[features]
# y = filtered_data_2[target]

# # Diviser les données en ensembles d'entraînement et de test
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Créer et entraîner le modèle de régression linéaire
# model = LinearRegression()
# model.fit(X_train, y_train)

# # Faire des prédictions sur les données de test
# y_pred = model.predict(X_test)

# # Évaluer le modèle
# mse = mean_squared_error(y_test, y_pred)
# r2 = r2_score(y_test, y_pred)

# print(f"Mean Squared Error: {mse}")
# print(f"R^2 Score: {r2}")

# # Afficher les coefficients du modèle
# coefficients = pd.DataFrame(model.coef_, features, columns=['Coefficient'])
# print(coefficients)

# # Tracer les données réelles et les prédictions
# plt.figure(figsize=(10, 6))
# plt.scatter(y_test, y_pred, color='blue', label='Predicted vs Actual')
# plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linewidth=2, label='Ideal Fit')
# plt.xlabel('Actual Calories per Portion')
# plt.ylabel('Predicted Calories per Portion')
# plt.title('Actual vs Predicted Calories per Portion')
# plt.legend()
# plt.grid(True)
# plt.show()