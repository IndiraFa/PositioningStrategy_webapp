import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
from preprocess import Preprocessing

# Generic function to plot distributions
def plot_distribution(data, plot_type='dot', title_prefix="Distribution de"):
    for col in data.columns:
        plt.figure(figsize=(10, 6))
        if plot_type == 'dot':
            # Plot a scatter plot for the column
            plt.scatter(data.index, data[col], alpha=0.7)
        elif plot_type == 'bar':
            # Plot a histogram for the column
            plt.hist(data[col], bins=250, edgecolor='k', alpha=0.7)
        plt.title(f'{title_prefix} {col}')
        plt.xlabel('Index' if plot_type == 'dot' else col)
        plt.ylabel(col if plot_type == 'dot' else 'Frequency')
        plt.grid(True)
        plt.show()

# Function to display tables
def display_table(data, title):
    print(f"Displaying the {title}")
    print(tabulate(data.head(10), headers='keys', tablefmt='psql'))
    print("\n")

# Constants for file paths
PATH_RAW_RECIPES = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/RAW_recipes.csv'
PATH_NUTRIENT_TABLE = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/nutrient_table.csv'

# Load the data
path = PATH_RAW_RECIPES
path_grille = PATH_NUTRIENT_TABLE

# Read the nutrient table data
grille_data = pd.read_csv(path_grille)

# Ensure the paths are correct and the files exist
configs = {
    'nutritioncolname': ['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
    'grillecolname': ['dv_calories_%', 'dv_sat_fat_%', 'dv_sugar_%', 'dv_sodium_%', 'dv_protein_%'],
    'dv_calories': 2000
}

# Call the preprocessing method
preprocessing_instance = Preprocessing(path, configs)
print("Calling the gaussian_normalisation method")

# Drop the 'id' column if it exists
if 'id' in preprocessing_instance.gaussiandata.columns:
    normalized_data = preprocessing_instance.gaussiandata.drop(columns=['id'])
    print("Gaussian normalization completed")
else:
    print("The 'id' column does not exist in gaussiandata")
    normalized_data = preprocessing_instance.gaussiandata

print("\n")

# Perform denormalization
denormalizedata, denormalized_outliers = preprocessing_instance.denormalizedata, preprocessing_instance.denormalized_outliers
print("Denormalization completed")

# Display all tables
display_table(preprocessing_instance.formatdata, "raw data table")
display_table(preprocessing_instance.normaldata, "formatted raw data table")
display_table(grille_data, "nutrient table data")
display_table(normalized_data, "normalized data table no Outliers")
display_table(denormalizedata, "denormalized data table")
display_table(denormalized_outliers, "denormalized outliers table")

# Plot the distributions
#plot_distribution(preprocessing_instance.formatdata.drop(columns=['id']), plot_type='dot', title_prefix="Distribution of formatted raw data")
#plot_distribution(preprocessing_instance.prefiltredata.drop(columns=['id']), plot_type='dot', title_prefix="Distribution of pre-filtered formatted data")
#plot_distribution(normalized_data, plot_type='bar', title_prefix="Distribution of normalized data")