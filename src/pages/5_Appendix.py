import streamlit as st
import pandas as pd
import os

# Titre de la page
st.markdown("<h1 style='color:purple;'>Appendix</h1>", unsafe_allow_html=True)

# Texte de description
st.write("""
## Nutriscore calculation
We built a Nutrition Score based on **daily value intake recommandations** (ref) and on available data from the recipes.<br>
Starting from the **maximum value of 14**, the Nutri-Score decreases as the nutritional quality of the recipe decreases.<br>
The **% of calories** that represents a recipe is based on the declared number of calories **per portion**. 
The **other nutrients** were **normalized by the daily intake recommandations** (as if the recipe represented the full 2000 kcal per day).    
In order to have a good Nutriscore, the recipe should have the following characteristics:<br>
         &nbsp;&nbsp;&nbsp;&nbsp;- a reasonable amount of calories per portion (a portion should not exceed 37% of the daily intake of 2000 calories)<br>
         &nbsp;&nbsp;&nbsp;&nbsp;- a low amount of sugar<br>
         &nbsp;&nbsp;&nbsp;&nbsp;- a low amount of saturated fat<br>
         &nbsp;&nbsp;&nbsp;&nbsp;- a low amount of sodium<br>
         &nbsp;&nbsp;&nbsp;&nbsp;- enough protein<br>
         """, unsafe_allow_html=True)

# Chemin vers le fichier CSV
current_dir = os.path.dirname(__file__)
csv_file_path = os.path.join(current_dir, '..', 'nutrient_table.csv')

# Lire le fichier CSV
df = pd.read_csv(csv_file_path)

# Afficher le tableau
st.write("### Nutriscore calculation grid")
st.write("The Nutriscore is calculated as follows based on the grid below:<br>"+
        "for each nutrient category, if the value is below the first line, no point is substracted. "+
        "If the value is between the first and the second line, 1 point is substracted. "+ 
        "If the value is between the second and the third line, 1.25 points are substracted, etc. "+ 
        "For each nutrient category, there is a maximum value after which no extra point is substracted. "+ 
        "For proteins, we look at minus the value.", unsafe_allow_html=True)
st.dataframe(df)
st.write("For a  easier interpretation, the Nutriscore is then converted into a letter grade from A to E, with A being the best grade and E the worst grade.")
st.image(os.path.join(current_dir, '..', 'scale.png'))

st.write("### Example of Nutriscore calculation")
st.write("This is an example of the calculation of the Nutriscore for the recipe of the Creamy chicken curry with the following nutritional values:")

# Afficher une ligne spécifique du DataFrame en utilisant l'ID
csv_file_path2 = os.path.join(current_dir, '..', 'nutrition_table_nutriscore.csv')
df2 = pd.read_csv(csv_file_path2)
recipe_id = 137434  # Remplacez par l'ID de la ligne que vous souhaitez afficher
specific_row = df2.loc[df2['id'] == recipe_id]
st.dataframe(specific_row)
st.write("**Calculation**: Nutriscore = 14 - 0 (calories) - 0 (saturated fat) - 2 (sugar) - 1 (sodium) - 0 (protein) = **11**<br>"+
         "**The label of the Nutriscore is B.**", unsafe_allow_html=True)

st.write("""
### References

[1] Method for calculating the official Nutriscore in France : https://docs.becpg.fr/fr/utilization/score5C.html<br>
[2] Daily recommendations for the main nutrients : https://eur-lex.europa.eu/legal-content/FR/TXT/PDF/?uri=CELEX:02011R1169-20180101<br>
""", unsafe_allow_html=True)

