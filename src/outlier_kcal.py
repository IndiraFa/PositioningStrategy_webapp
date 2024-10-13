#step 1
import pandas as pd
from tabulate import tabulate

# Chemin correct vers le fichier CSV
file_path = '/Users/darryld/Desktop/Télécom_Paris/BGDIA700-Kit_Big_Data/Projet_kitBigData/dataset_kitBigData/RAW_recipes.csv'

# Lire le fichier CSV
df = pd.read_csv(file_path, sep=',')

# Afficher les 10 premières lignes du DataFrame sous forme de tableau formaté
print(tabulate(df.head(10), headers='keys', tablefmt='psql'))



#Step 2
# Séparer les valeurs de la colonne 'nutrition' en colonnes distinctes
nutrition_df = df['nutrition'].apply(lambda x: pd.Series(eval(x), index=['kcal', 'total_fat(g)', 'sugar(g)', 'sodium(mg)', 'protein(g)', 'sat_fat(g)', 'carbs(g)']))

# Ajouter les nouvelles colonnes au DataFrame original
df = pd.concat([df, nutrition_df], axis=1)

# Afficher les colonnes 'name', 'id', 'kcal', 'total_fat', 'sugar', 'sodium', 'protein', 'sat_fat'
print(df[['name', 'id', 'kcal', 'total_fat(g)', 'sugar(g)', 'sodium(mg)', 'protein(g)', 'sat_fat(g)', 'carbs(g)', 'n_ingredients']])

# Créer une nouvelle table avec les colonnes sélectionnées
new_df = df[['name', 'id', 'kcal', 'total_fat(g)', 'sugar(g)', 'sodium(mg)', 'protein(g)', 'sat_fat(g)', 'carbs(g)', 'n_ingredients']]

# Afficher les 10 premières lignes de la nouvelle table
print(tabulate(new_df.head(10), headers='keys', tablefmt='psql'))



#Step 3
import matplotlib.pyplot as plt

# Tracer les données
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['kcal'], label='kcal')
plt.xlabel('Index')
plt.ylabel('kcal')
plt.title('kcal en fonction de l\'index')
plt.legend()
plt.show()



#Step 4
import matplotlib.pyplot as plt
# Filtrer les données pour ne conserver que les lignes où 'kcal' est inférieur à 10 et 'n_ingredients' est supérieur à 1, et 'kcal' est inférieur à 4500
filtered_df = df[(df['kcal'] < 10) & (df['n_ingredients'] > 1) & (df['kcal'] < 4500)]

# Tracer les données filtrées
plt.figure(figsize=(10, 6))
plt.plot(filtered_df.index, filtered_df['kcal'], label='kcal')
plt.xlabel('Index')
plt.ylabel('kcal')
plt.title('kcal en fonction de l\'index (données filtrées)')
plt.legend()
plt.show()