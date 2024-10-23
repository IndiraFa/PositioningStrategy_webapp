import streamlit as st
import pandas as pd
import os
os.chdir('/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/scripts')
from calcul_nutriscore import get_data

# 1st test pour créer un site streamlit qui permet affichier 2 tableaux de nutrition 

st.write("Voici les deux tableaux de nutrition, le 1er est origin, le 2e est normalisé:")

# arguments 
path = '/Users/phuongnguyen/Documents/cours_BGD_Telecom_Paris_2024/Kit_Big_Data/dataset/RAW_recipes.csv'

configs = {
    'nutritioncolname':['calories', 'total_fat_%', 'sugar_%', 'sodium_%', 'protein_%', 'sat_fat_%', 'carbs_%'],
    'dv_calories' : 2000
}

# 1er tableau de nutrition
table1, table2 = get_data(path, configs)
st.table(table1.head())
# st.table(table2.head())

if st.checkbox('Show dataframe'): 
    table1