import pandas as pd
from sqlalchemy import create_engine, text
import toml

# Lire les informations de connexion depuis secrets.toml
secrets = toml.load('secrets.toml')
postgresql_config = secrets['connections']['postgresql']

# Informations de connexion à la base de données PostgreSQL
db_host = postgresql_config['host']
db_name = postgresql_config['database']
db_user = postgresql_config['username']
db_password = postgresql_config['password']
db_port = postgresql_config['port']

# Connexion à la base de données PostgreSQL
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
conn = engine.connect()

# Supprimer la table NS_noOutliers si elle existe déjà
query_drop_table = text('DROP TABLE IF EXISTS NS_noOutliers;')
conn.execute(query_drop_table)  # Utiliser text() pour les requêtes SQL

# Créer la nouvelle table NS_noOutliers
query_create_table = text('''
CREATE TABLE NS_noOutliers AS
SELECT *
FROM "NS_withOutliers"
WHERE id NOT IN (SELECT id FROM outliers);
''')

# Exécuter la requête pour créer la table
conn.execute(query_create_table)

# Lire la table nouvellement créée dans un DataFrame
df_nutriscore_no_outliers = pd.read_sql_query('SELECT * FROM "NS_noOutliers";', conn)

# Fermeture de la connexion
conn.close()

# Affichage du DataFrame
print(df_nutriscore_no_outliers.head())

# Afficher des informations sur le DataFrame
print(df_nutriscore_no_outliers)
print(df_nutriscore_no_outliers.shape)
df_nutriscore_no_outliers.info()
print(df_nutriscore_no_outliers.describe())
