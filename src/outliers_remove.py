#Step 1: Importer les bibliothèques nécessaires et lire le fichier CSV
import pandas as pd
from tabulate import tabulate

# Chemin correct vers le fichier CSV
file_path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/dataset_kitBigData/RAW_recipes.csv'

# Lire le fichier CSV
df = pd.read_csv(file_path, sep=',')

# Afficher les 10 premières lignes du DataFrame sous forme de tableau formaté
print(tabulate(df.head(10), headers='keys', tablefmt='psql'))





#Step 2: Sélectionner les colonnes pertinentes et afficher les 10 premières lignes

# Séparer les valeurs de la colonne 'nutrition' en colonnes distinctes
nutrition_df = df['nutrition'].apply(lambda x: pd.Series(eval(x), index=['kcal', 'total_fat(PDV)', 'sugar(PDV)', 'sodium(PDV)', 'protein(PDV)', 'sat_fat(PDV)', 'carbs(PDV)']))

# Ajouter les nouvelles colonnes au DataFrame original
df = pd.concat([df, nutrition_df], axis=1)

# Afficher les colonnes 'name', 'id', 'kcal', 'total_fat', 'sugar', 'sodium', 'protein', 'sat_fat'
print(df[['name', 'id', 'kcal', 'total_fat(PDV)', 'sugar(PDV)', 'sodium(PDV)', 'protein(PDV)', 'sat_fat(PDV)', 'carbs(PDV)', 'n_ingredients']])

# Créer une nouvelle table avec les colonnes sélectionnées
new_df = df[['name', 'id', 'kcal', 'total_fat(PDV)', 'sugar(PDV)', 'sodium(PDV)', 'protein(PDV)', 'sat_fat(PDV)', 'carbs(PDV)', 'n_ingredients']]

# Afficher les 10 premières lignes de la nouvelle table
print(tabulate(new_df.head(10), headers='keys', tablefmt='psql'))

# Compter les lignes du DataFrame original
row_count_original = len(new_df)
print(f"Nombre de recettes: {row_count_original}")




#Step 3: Créer des box plots pour les colonnes sélectionnées et filtrer les outliers
import matplotlib.pyplot as plt

# Liste des colonnes pour lesquelles nous voulons créer des box plots
columns = ['total_fat(PDV)', 'sugar(PDV)', 'sodium(PDV)', 'protein(PDV)', 'sat_fat(PDV)', 'carbs(PDV)']

# Dictionnaire pour stocker les outliers et les limites pour chaque colonne
outliers_dict = {}
limits_dict = {}

# Créer des box plots pour chaque colonne
for column in columns:
    # Calculer Q1 et Q3 
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    # Définir les limites pour détecter les outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Stocker les limites dans le dictionnaire
    limits_dict[column] = (lower_bound, upper_bound)
    
    # Filtrer les outliers
    filtered_df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    
    # Stocker les outliers dans le dictionnaire
    outliers_dict[column] = outliers[column].tolist()
    
    # Afficher les valeurs de Q1, Q3, min et max
    print(f"{column}:")
    print(f"Q1: {Q1}")
    print(f"Q3: {Q3}")
    print(f"Min: {filtered_df[column].min()}")
    print(f"Max: {filtered_df[column].max()}")
    print("\n")
    
    # Créer le box plot
    plt.figure()
    filtered_df.boxplot(column=[column])
    plt.title(f'Box plot for {column}')
    plt.show()

# Afficher les outliers pour chaque colonne
for column, outliers in outliers_dict.items():
    print(f"Outliers for {column}: {outliers}")





#Step 4: Filtrer les outliers et afficher les 10 premières lignes du nouveau DataFrame

# Créer une copie du DataFrame original pour le filtrage
filtered_df_no_outliers = new_df.copy()

# Filtrer les outliers pour chaque colonne en utilisant les limites calculées à l'étape 3
for column in columns:
    lower_bound, upper_bound = limits_dict[column]
    
    # Filtrer les lignes qui contiennent des outliers
    filtered_df_no_outliers = filtered_df_no_outliers[
        (filtered_df_no_outliers[column] >= lower_bound) & 
        (filtered_df_no_outliers[column] <= upper_bound)
    ]

# Afficher les 10 premières lignes du nouveau DataFrame sans outliers
print(tabulate(filtered_df_no_outliers.head(10), headers='keys', tablefmt='psql'))

# Compter les lignes du DataFrame sans outliers
row_count_new = len(filtered_df_no_outliers)
row_count_original = len(new_df)
outliers_count = row_count_original - row_count_new
print(f"Nombre de recettes: {row_count_new}")
print(f"Outiliers retirés: {outliers_count}")




#Step 5: Créer des graphiques avec outliers
# Liste des colonnes pour lesquelles nous voulons créer des graphiques
columns_to_plot = ['total_fat(PDV)', 'sugar(PDV)', 'sodium(PDV)', 'protein(PDV)', 'sat_fat(PDV)', 'carbs(PDV)']

# Créer des graphiques pour chaque colonne
for column in columns_to_plot:
    plt.figure()
    plt.plot(new_df.index, new_df[column], 'o', markersize=2)
    plt.title(f'{column} en fonction de l\'index')
    plt.xlabel('Index')
    plt.ylabel(column)
    plt.grid(True)
    plt.show()




#Step 6: Créer des graphiques sans outliers

# Créer des graphiques pour chaque colonne
for column in columns_to_plot:
    plt.figure()
    plt.plot(filtered_df_no_outliers.index, filtered_df_no_outliers[column], 'o', markersize=2)
    
    # Trouver la valeur maximale et son index
    max_value = filtered_df_no_outliers[column].max()
    max_index = filtered_df_no_outliers[column].idxmax()
    
    # Annoter la valeur maximale sur le graphique
    plt.annotate(f'Max: {max_value}', xy=(max_index, max_value), xytext=(max_index, max_value + 0.05 * max_value),
                 arrowprops=dict(facecolor='red', shrink=0.05), fontsize=9, color='red')
    
    plt.title(f'{column} en fonction de l\'index')
    plt.xlabel('Index')
    plt.ylabel(column)
    plt.grid(True)
    plt.show()