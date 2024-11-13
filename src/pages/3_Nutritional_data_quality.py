import streamlit as st
import pandas as pd
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from linear_regression_nutrition import filtered_data, features, target, daily_g_proteins, daily_g_fat, daily_g_carbs
from linear_regression_nutrition import linear_regression, plot_linear_regression, calories_per_gram, bootstrap_confidence_interval

st.set_page_config(layout="centered")
#allows to import packages from the parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@st.cache_data
def get_data():
    return filtered_data

# Titre de la page
st.markdown("<h1 style='color:purple;'>Correlation analysis</h1>", unsafe_allow_html=True)
#ajouter la conclusion de l'analyse de corrélation : pour améliorer la crédibilité du site, mettre en place un système de vérification des données nutritionnelles ou de calcul automatisé. 
st.write("""
## Quality of nutritional data
Nutritional data is essential for the calculation of the Nutri-Score. Values are filled in by the users and can be incorrect.
We performed a linear regression to estimate the quality of the nutritional data we worked with.
The linear regression model was trained on the nutritional values of the recipes (amount of protein, total amount of fat and carbohydrates) and the calories per portion because the linear relationship between them is known. [1] 
We used the data set without outliers to include the first preprocessing steps.
""", unsafe_allow_html=True)

st.write("#### Linear regression")

st.write("The linear regression allows to estimate the parameters b0, b1, b2, b3 of the model where calories = b0 + b1*total_fat_% + b2*protein_% + b3*carbs_% :")
mse, r2, intercept, coefficients, y_test, y_pred = linear_regression(filtered_data, target, features)
linear_regression(filtered_data, target, features)
st.write(coefficients)
st.write(f"Intercept: {intercept:.2f}")
st.write(f"Mean Squared Error: {mse:.2f}")
st.write(f"R^2 Score: {r2:.2f}")


plot_linear_regression(y_test, y_pred)
st.pyplot(plt)

st.write("With the linear regression we can calculate the amount of calories per gram of each nutrient **obtained from the data and the model.**", unsafe_allow_html=True)
coefficients_per_g = calories_per_gram(coefficients)
st.write(coefficients_per_g)

st.write("""
         #### Confidence interval tests
         So, how good is the data ? We performed confidence interval tests, with a parametrable confidence level, using the bootstrap method on the obtained coefficients to check if they are significantly different from the reference values.""")

conf_level = st.slider("Select the confidence level", 0.6, 0.99, 0.9, key = 1)

confidence_intervals = bootstrap_confidence_interval(filtered_data, target, features, num_bootstrap_samples=1000, confidence_level=conf_level)
intervals_df = pd.DataFrame(confidence_intervals, index=['Lower Bound', 'Upper Bound']).T
#cal_per_g_proteins_interval = confidence_intervals['protein_%']*100/50

intervals_per_g_df = intervals_df.copy()
intervals_per_g_df.loc['Calories per gram of Protein'] = intervals_df.loc['protein_%']*100/daily_g_proteins
intervals_per_g_df.loc['Calories per gram of Fat'] = intervals_df.loc['total_fat_%']*100/daily_g_fat
intervals_per_g_df.loc['Calories per gram of Carbohydrates'] = intervals_df.loc['carbs_%']*100/daily_g_carbs

st.table(intervals_per_g_df)

references = {
    'Calories per gram of Protein': [4.06],
    'Calories per gram of Carbohydrates': [4.06],
    'Calories per gram of Fat': [8.84],
}
df = pd.DataFrame(references, index=['Value'])

values_ref = [df.loc['Value', 'Calories per gram of Protein'], df.loc['Value', 'Calories per gram of Carbohydrates'], df.loc['Value', 'Calories per gram of Fat']]
values = [coefficients_per_g.loc['Value', 'calories per g of proteins'], coefficients_per_g.loc['Value', 'cal per g of carbs'], coefficients_per_g.loc['Value', 'cal per g of fat']]
errors = [
    [values[0] - intervals_per_g_df.loc['Calories per gram of Protein', 'Lower Bound'], intervals_per_g_df.loc['Calories per gram of Protein', 'Upper Bound'] - values[0]],
    [values[1] - intervals_per_g_df.loc['Calories per gram of Carbohydrates', 'Lower Bound'], intervals_per_g_df.loc['Calories per gram of Carbohydrates', 'Upper Bound']- values[1]],
    [values[2] - intervals_per_g_df.loc['Calories per gram of Fat', 'Lower Bound'], intervals_per_g_df.loc['Calories per gram of Fat', 'Upper Bound'] - values[2]]
]


errors = np.array(errors).T


fig1, ax1 = plt.subplots()
ax1.scatter(['Protein'], values_ref[0], color='black', label='Reference Values')
ax1.errorbar(['Protein'], values[0], yerr=[[errors[0][0]], [errors[1][0]]], fmt='o', capsize=5, capthick=2, ecolor='red', color='blue', label='Calculated Values')
ax1.set_xlabel('Nutrient')
ax1.set_ylabel('Calories per Gram')
ax1.set_title('Protein Calories per Gram with Confidence Intervals calculated from the data')
ax1.legend()
st.pyplot(fig1)


fig2, ax2 = plt.subplots()
ax2.scatter(['Carbohydrates'], values_ref[1], color='black', label='Reference Values')
ax2.errorbar(['Carbohydrates'], values[1], yerr=[[errors[0][1]], [errors[1][1]]], fmt='o', capsize=5, capthick=2, ecolor='red', color='blue', label='Calculated Values')
ax2.set_xlabel('Nutrient')
ax2.set_ylabel('Calories per Gram')
ax2.set_title('Carbohydrates Calories per Gram with Confidence Intervals calculated from the data')
ax2.legend()
st.pyplot(fig2)


fig3, ax3 = plt.subplots()
ax3.scatter(['Fat'], values_ref[2], color='black', label='Reference Values')
ax3.errorbar(['Fat'], values[2], yerr=[[errors[0][2]], [errors[1][2]]], fmt='o', capsize=5, capthick=2, ecolor='red', color='blue', label='Calculated Values')
ax3.set_xlabel('Nutrient')
ax3.set_ylabel('Calories per Gram')
ax3.set_title('Fat Calories per Gram with Confidence Intervals calculated from the data')
ax3.legend()
st.pyplot(fig3)


st.write("The confidence intervals show that the coefficients are significantly different from the reference values, even with lower confidence level.", unsafe_allow_html=True)

st.write("#### Reference values")

st.write("""[1] Amount of calories per gram of fat, carbohydrate and protein :  https://www.nal.usda.gov/programs/fnic#:~:text=Frequently%20Asked%20Questions%20(FAQs),provides%209%20calories%20per%20gram.""")

st.table(df)