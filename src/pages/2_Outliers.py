import sys
import os
import pandas as pd
import plotly.express as px
import streamlit as st
import psycopg2
from sqlalchemy import create_engine
import plotly.graph_objects as go
import gdown
import toml

# Add the directory containing preprocess.py to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocess import Preprocessing
from calcul_nutriscore import NutriScore


def main():
    st.title('Analyse des Outliers')

    # Informations de connexion à la base de données PostgreSQL
    postgresql_config = {
        'host': '62.169.24.75',
        'database': 'streamlit',
        'username': 'streamlit_user',
        'password': '123456789', 
        'port': 5432
    }

    db_host = postgresql_config['host']
    db_name = postgresql_config['database']
    db_user = postgresql_config['username']
    db_password = postgresql_config['password']
    db_port = postgresql_config['port']

    # Créer une connexion à la base de données PostgreSQL
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    conn = engine.connect()

    # Lire les données depuis la base de données
    formatted_data_query = 'SELECT * FROM "Formatted_data"'
    raw_data_query = 'SELECT * FROM "raw_recipes"'
    normalized_data_query = 'SELECT * FROM "nutrition_withOutliers"'
    outliers_data_query = 'SELECT * FROM "outliers"'
    nutrition_noOutliers_query = 'SELECT * FROM "nutrition_noOutliers"'
    gaussian_norm_data_query = 'SELECT * FROM "gaussian_norm_data"'
    prefiltre_data_query = 'SELECT * FROM "prefiltre_data"'

    formatted_data = pd.read_sql_query(formatted_data_query, conn)
    raw_data = pd.read_sql_query(raw_data_query, conn)
    normalized_data = pd.read_sql_query(normalized_data_query, conn)
    outliers_data = pd.read_sql_query(outliers_data_query, conn)
    nutrition_noOutliers = pd.read_sql_query(nutrition_noOutliers_query, conn)
    gaussian_norm_data = pd.read_sql_query(gaussian_norm_data_query, conn)
    prefiltre_data = pd.read_sql_query(prefiltre_data_query, conn)

    conn.close()

    st.write('Voici un aperçu des données :')
    st.write(raw_data.head())

    st.write('''
    Les données de la colonne nutrition sont d'abord extraites de la table selon le schema suivant : \n
             [calories, total_fat, sugar, sodium, protein, saturated_fat, carbohydrates] 
             ''')
    st.markdown('''
    Remarque : \n
    Mise à part les calories, les autres valeurs sont exprimées en pourcentage. \n
                ''')
    
    st.write('Données formatées :')
    st.write(formatted_data.head())

    st.markdown('''
    Nos données font référence à une portion et nous les avons ramené, en pourcentage, à des valeurs journalières de 2000 calories pour un adulte.
                ''')
    st.latex(r'''
    \text{daily value} = \frac{\text{portion value}}{2000} \times 100
             ''')

    st.write('Données ajustées :')
    st.write(normalized_data.head())

    st.write('''
    Si nous regardons les données ajustées, nous pouvons identifier à première vue des valeurs abérrantes.
    Nous avons donc procédé à un nettoyage des données en supprimant les valeurs abérrantes en 2 étapes : \n
    - Étape 1 : Filtrage manuel par application de seuils au-delà desquels nous identifions nos outliers. \n   
    ''')
    
    # Afficher le tableau des seuils de filtrage
    thresholds = {
        'dv_calories_%': 5000,
        'dv_total_fat_%': 5000,
        'dv_sugar_%': 5000,
        'dv_sodium_%': 5000,
        'dv_protein_%': 2000,
        'dv_sat_fat_%': 2000,
        'dv_carbs_%': 5000
    }
    thresholds_df = pd.DataFrame(list(thresholds.items()), columns=['Nutrient', 'Threshold'])
    
    # Convertir le DataFrame en HTML et l'intégrer avec du CSS pour le centrer
    table_html = thresholds_df.to_html(index=False)

    # Utiliser st.markdown pour afficher le tableau centré
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            {table_html}
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)


    # Menu déroulant pour sélectionner la colonne
    options = {
        'Distribution des calories': 'dv_calories_%',
        'Distribution des total_fat': 'dv_total_fat_%',
        'Distribution des sugar': 'dv_sugar_%',
        'Distribution des sodium': 'dv_sodium_%',
        'Distribution des protein': 'dv_protein_%',
        'Distribution des saturated_fat': 'dv_sat_fat_%',
        'Distribution des carbohydrates': 'dv_carbs_%'
    }
    selected_option = st.selectbox('Visualisation des données :', list(options.keys()))

    # Afficher les graphiques correspondants
    y_column = options[selected_option]

    # Utiliser des colonnes pour afficher les graphiques côte-à-côte
    col1, col2 = st.columns(2)

    # Ajouter une option pour sélectionner les données de référence
    data_option = st.radio(
        "Choisissez les données de référence",
        ('Données non filtrées', 'Données préfiltrées', 'Données filtrées')
    )

    # Sélectionner les données en fonction de l'option choisie
    if data_option == 'Données non filtrées':
        data = normalized_data
    elif data_option == 'Données préfiltrées':
        data = prefiltre_data
    else:
        data = nutrition_noOutliers

    # Ajouter une échelle des x avec un curseur
    x_min, x_max = st.slider(
        'Sélectionnez la plage des valeurs de x',
        min_value=float(data[y_column].min()),
        max_value=float(data[y_column].max()),
        value=(float(data[y_column].min()), float(data[y_column].max()))
    )

    # Filtrer les données en fonction de la plage sélectionnée
    filtered_data = data[(data[y_column] >= x_min) & (data[y_column] <= x_max)]

    # Histogramme
    with col1:
        fig_histogram = px.histogram(filtered_data, x=y_column, title=f'Histogramme - {selected_option}')
        st.plotly_chart(fig_histogram)

    # Box plot
    with col2:
        fig_box = px.box(filtered_data, y=y_column, title=f'Box Plot - {selected_option}')
        st.plotly_chart(fig_box)

if __name__ == "__main__":
    main()