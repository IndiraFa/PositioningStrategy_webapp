import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

st.markdown("<h1 style='color:purple;'>Positioning strategy for Mangetamain</h1>", unsafe_allow_html=True)
st.header("We built a Nutriscore to explore for Mangetamain the opportuniy to position itself as a healthy food brand.") 
st.write("We built a Nutrition Score based on daily value intaked recommandations.")

st.subheader("Nutri-Score based on the full data set")

nutriscore_data = pd.read_csv('./nutrition_table_nutriscore.csv') 
# Drop NaN values
nutriscore_data = nutriscore_data['nutriscore'].dropna()
# Create a histogram using Plotly
fig = px.histogram(
    nutriscore_data, 
    x='nutriscore', 
    nbins=28,
    title='Nutri-Score Distribution',
    color_discrete_sequence=['#636EFA']
)

# Update layout for better appearance
fig.update_layout(
    xaxis_title='Nutri-Score',
    yaxis_title='Frequency',
    template='plotly_white',
    bargap=0.1,
    xaxis=dict(range=[0, 14]),
    yaxis=dict(range=[0, 45000])
)

# Display the plot in Streamlit
st.plotly_chart(fig)

st.subheader("Nutri-Score based on the data set without outliers")
nutriscore_data_no_outliers = pd.read_csv('./nutrition_table_nutriscore_no_outliers.csv') 
# Drop NaN values
nutriscore_data_no_outliers = nutriscore_data_no_outliers['nutriscore'].dropna()
# Create a histogram using Plotly
fig = px.histogram(
    nutriscore_data_no_outliers, 
    x='nutriscore', 
    nbins=28,
    title='Nutri-Score Distribution',
    color_discrete_sequence=['#636EFA']
)

# Update layout for better appearance
fig.update_layout(
    xaxis_title='Nutri-Score',
    yaxis_title='Frequency',
    template='plotly_white',
    bargap=0.1,
    xaxis=dict(range=[0, 14]),
    yaxis=dict(range=[0, 45000])
)

# Display the plot in Streamlit
st.plotly_chart(fig)