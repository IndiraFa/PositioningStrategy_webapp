import pandas as pd
import psycopg2
import toml
import logging

# Configuration du journal (logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Lire les informations de connexion depuis secrets.toml
    secrets = toml.load('secrets.toml')
    postgresql_config = secrets['connections']['postgresql']

    # Extraire les informations de connexion
    db_host = postgresql_config['host']
    db_name = postgresql_config['database']
    db_user = postgresql_config['username']
    db_password = postgresql_config['password']
    db_port = postgresql_config['port']

    # Connexion à la base de données
    logger.info("Connexion à la base de données PostgreSQL...")
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    cur = conn.cursor()

    # Supprimer la table NS_noOutliers si elle existe
    query_drop_table = 'DROP TABLE IF EXISTS "NS_noOutliers";'
    logger.info("Suppression de la table 'NS_noOutliers' si elle existe...")
    cur.execute(query_drop_table)

    # Créer la table NS_noOutliers
    query_create_table = '''
    CREATE TABLE "NS_noOutliers" AS
    SELECT 
        NS.id, 
        NS."dv_calories_%",
        NS."dv_total_fat_%",
        NS."dv_sugar_%",
        NS."dv_sodium_%",
        NS."dv_protein_%",
        NS."dv_sat_fat_%",
        NS."dv_carbs_%",
        NS.nutriscore,
        NS.label
    FROM 
        "NS_withOutliers" AS NS
    INNER JOIN 
        "nutrition_noOutliers" AS NO
    ON 
        NS.id = NO.id;
    '''
    logger.info("Création de la table 'NS_noOutliers'...")
    cur.execute(query_create_table)

    # Commit pour appliquer les changements
    conn.commit()

    # Lire les données de la table dans un DataFrame
    query_select = 'SELECT * FROM "NS_noOutliers";'
    logger.info("Lecture des données de la table 'NS_noOutliers'...")
    df_nutriscore_no_outliers = pd.read_sql_query(query_select, conn)

    # Afficher un aperçu des données
    logger.info(f"Table 'NS_noOutliers' chargée avec {df_nutriscore_no_outliers.shape[0]} lignes.")
    print(df_nutriscore_no_outliers.head())

    # Afficher des informations sur le DataFrame
    logger.info("Affichage des informations sur le DataFrame :")
    print(df_nutriscore_no_outliers.info())
    print(df_nutriscore_no_outliers.describe())

except Exception as e:
    logger.error(f"Une erreur s'est produite : {e}")
finally:
    # Fermeture de la connexion à la base de données
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
    logger.info("Connexion à la base de données fermée.")
