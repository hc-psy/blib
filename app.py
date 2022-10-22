import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.write("# NTU Buddhist Library")
st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut lorem neque, congue sit amet finibus nec, blandit in arcu. Donec semper turpis at turpis sollicitudin commodo. Aliquam non placerat purus. Nulla maximus et magna quis accumsan. Morbi at interdum tortor. Nam lacinia sapien ac nisi ultrices faucibus. Proin suscipit imperdiet nibh a aliquet. Cras eleifend semper lacus vitae porttitor. Fusce eu risus non libero molestie aliquam. Phasellus laoreet, elit euismod varius ultricies, nisl arcu cursus metus, et condimentum neque elit sed augue.")


df = pd.read_csv('cache/ip2geo.csv')
df.drop_duplicates(inplace=True)

countries_list = df["country"].tolist()
countries_set = sorted(set(countries_list))
countries = ['World'] + list(countries_set) 

option = st.sidebar.selectbox('What country would you like to see?', countries)
st.write(f'## {option}')
st.map(df if option == 'World' else df[df['country'] == option])


col1, col2 = st.columns(2)
metric_text1 = f"{len(df) if option == 'World' else len(df[df['country'] == option])} users"
col1.metric("Unique Individual", metric_text1)
metric_text2 = f"{len(df)/len(df)*100 if option == 'World' else np.around(len(df[df['country'] == option])/len(df), 5)*100:.2f}%"
col2.metric("Percentage", metric_text2)

df2 = df if option == 'World' else df[df['country'] == option]
if option == 'World':
    df2 = df2.groupby(['country'])['country'].count().reset_index(name='count')
    df2.loc[df2['count'] < df2['count'].sum()/100, 'country'] = 'Other countries'
    fig = px.pie(df2, values='count', names='country', hole=.3, color_discrete_sequence=px.colors.cyclical.Twilight)
else:
    df2 = df2.groupby(['city'])['city'].count().reset_index(name='count')
    df2.loc[df2['count'] < df2['count'].sum()/100, 'city'] = 'Other cities'
    fig = px.pie(df2, values='count', names='city', hole=.3, color_discrete_sequence=px.colors.cyclical.Twilight)

fig.update_traces(textposition='inside')
st.plotly_chart(fig, use_container_width=True)