from email.policy import default
import streamlit as st
import pandas as pd
import numpy as np

st.write("# NTU Buddhist Library")

df = pd.read_csv('cache/ip2geo.csv')
df.drop_duplicates(inplace=True)

countries_list = df["country"].tolist()
countries_set = sorted(set(countries_list))
countries = ['World'] + list(countries_set) 

option = st.selectbox('What country would you like to see?', countries)
st.write('You selected:', option)
st.map(df if option == 'World' else df[df['country'] == option])


col1, col2 = st.columns(2)
metric_text1 = f"{len(df) if option == 'World' else len(df[df['country'] == option])} users"
col1.metric("Unique Individual", metric_text1)
metric_text2 = f"{len(df)/len(df)*100 if option == 'World' else np.around(len(df[df['country'] == option])/len(df), 5)*100:.3f}%"
col2.metric("Percentage", metric_text2)