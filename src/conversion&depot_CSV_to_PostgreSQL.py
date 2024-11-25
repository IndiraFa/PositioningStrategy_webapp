import pandas as pd
from sqlalchemy import create_engine
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

# Créer une connexion à la base de données PostgreSQL
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Fonction pour lire un fichier CSV et l'importer dans PostgreSQL
def import_csv_to_postgresql(csv_file_path, table_name):
    df = pd.read_csv(csv_file_path)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Les données du fichier CSV '{csv_file_path}' ont été importées dans la table '{table_name}' de la base de données PostgreSQL.")

# Chemins des fichiers CSV
csv_files = {
    'raw_recipes': 'RAW_recipes.csv',  
    'RAW_interactions': 'RAW_interactions.csv',  
    'nutrient_table': 'nutrient_table.csv'  
}

# Importer chaque fichier CSV dans PostgreSQL
for table_name, csv_file_path in csv_files.items():
    import_csv_to_postgresql(csv_file_path, table_name)