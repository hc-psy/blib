import pydeck as pdk
from pydeck.data_utils import compute_view

import streamlit as st
from streamlit.elements.map import _get_zoom_level

import pandas as pd
import numpy as np

import database.appdata as db

import plotly.express as px
import plotly.graph_objects as go

from utilities.initial import app_init

app_init()

def sec_view_handler():
    st.session_state.sec_view = not st.session_state.sec_view

@st.cache(allow_output_mutation=True)
def fetch_data_ip(data_path1, data_path2, merge_on='ip'):
    df1 = pd.read_csv(data_path1)
    df2 = pd.read_csv(data_path2)
    df = df1.merge(df2, on=merge_on)
    return df

def add_cnt():
    st.session_state.click_cnt += 1

def make_dropdown_list(df, col_name, begin_with=[], cond_col_name=-1, cond_col_value=-1):
    if cond_col_name != -1 and cond_col_value != -1:
        col_list = (df[df[cond_col_name] == cond_col_value])[col_name].tolist()
    else:
        col_list = df[col_name].tolist()
    
    col_set = sorted(set(col_list))
    return begin_with + list(col_set)

def filter_df_by_region(df, state_opt: list, base_col_idx = 5):
    level, condition = state_opt
    level = base_col_idx - level
    
    if condition in ['World | Continent', 'World | Contry']:
        return df
    
    return df[df.iloc[:, level] == condition]

def plot_region_piechart(df, state_opt: list, base_col_idx = 5):
    level, condition = state_opt
    level = base_col_idx - level
    
    tgt_col = df.columns[level] if condition == 'World | Continent' else df.columns[level - 1]

    tmp_df = df.groupby([tgt_col])[tgt_col].count().reset_index(name='Users')
    tmp_df.loc[tmp_df['Users'] < tmp_df['Users'].sum()/100, tgt_col] = f'Other {tgt_col.lower()}'
    
    fig = px.pie(tmp_df, values='Users', names=tgt_col, hole=.3, color_discrete_sequence=px.colors.diverging.Geyser)
    fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True)
    

def plot_region_hist(df):
    
    fig = go.Figure([go.Histogram(x=df["count"], cumulative_enabled=False)])
    fig.update_yaxes(type="log")
    fig.update_layout(xaxis_title="Click Times", yaxis_title="Frequency")
    
    fig.data[0].on_click(add_cnt)
    
    st.plotly_chart(fig, use_container_width=True)

def get_zoom_value(df, lat, lon):
    
    min_lat = df[lat].min()
    max_lat = df[lat].max()
    min_lon = df[lon].min()
    max_lon = df[lon].max()
    range_lon = abs(max_lon - min_lon)
    range_lat = abs(max_lat - min_lat)

    if range_lon > range_lat:
        longitude_distance = range_lon
    else:
        longitude_distance = range_lat
    zoom = _get_zoom_level(longitude_distance)
    
    return zoom

st.write(db.TITLE)
st.write(db.DESCRIPTION)

df = fetch_data_ip('cache/ip_geo.csv', 'cache/ip_book_count.csv')

with st.sidebar:
    with st.expander("View I", expanded=True):

        contn = make_dropdown_list(df, "continent", begin_with=['World | Continent', 'World | Contry'])
        opt1 = st.selectbox('Continent', contn, key="contn1")
        contr = make_dropdown_list(df, "country", begin_with=['- Select -'], cond_col_name="continent", cond_col_value=opt1)
        opt2 = st.selectbox('Country', contr, key="contr1")
        city = make_dropdown_list(df, "city", begin_with=['- Select -'], cond_col_name="country", cond_col_value=opt2)
        opt3 = st.selectbox('City', city, key="city1")
        
        try:
            opts = [opt1, opt2, opt3]
            last_val_idx = opts.index('- Select -') - 1
            st.session_state.fst_opt = [last_val_idx, opts[last_val_idx]]
        except:
            st.session_state.fst_opt = [2, opt3]
    
    if not st.session_state.sec_view:
        _, button, _ = st.columns(3)
        with button:
            st.button("New View", on_click=sec_view_handler)
    else:
        with st.expander("View II"):
            
            contn = make_dropdown_list(df, "continent", begin_with=['World | Continent', 'World | Contry'])
            opt1 = st.selectbox('Continent', contn)
            contr = make_dropdown_list(df, "country", begin_with=['- Select -'], cond_col_name="continent", cond_col_value=opt1)
            opt2 = st.selectbox('Country', contr)
            city = make_dropdown_list(df, "city", begin_with=['- Select -'], cond_col_name="country", cond_col_value=opt2)
            opt3 = st.selectbox('City', city)
            
            try:
                opts = [opt1, opt2, opt3]
                last_val_idx = opts.index('- Select -') - 1
                st.session_state.sec_opt = [last_val_idx, opts[last_val_idx]]
            except:
                st.session_state.sec_opt = [2, opt3]
            
            _, button, _ = st.columns([3,5,3])
            with button:
                st.button("Delete View II", on_click=sec_view_handler)


region_df = filter_df_by_region(df, st.session_state.fst_opt)
st.write(f'## {st.session_state.fst_opt[1]}')


col1, col2 = st.columns(2, gap="medium")

with col1:
    st.write(f"### {st.session_state.fst_opt[1]} Pie Chart")
    st.map(region_df)
    
with col2:
    st.empty()
    if st.session_state.fst_opt[0] != 2:
        plot_region_piechart(region_df, st.session_state.fst_opt)


cc1, cc2, _, _ = st.columns(4)

metric_text1 = f"{len(region_df)} users"
cc1.metric("Unique Individual", metric_text1)

metric_text2 = f"{np.around(len(region_df)/len(df), 5)*100:.2f}%"
cc2.metric("Percentage", metric_text2)

plot_region_hist(region_df)


    
# layer = pdk.Layer(
#     'ColumnLayer',  # `type` positional argument is here
#     region_df,
#     get_position=['lon', 'lat'],
#     get_evaluation='count',
#     radius=100,
#     auto_highlight=True,
#     on_click=add_cnt,
#     elevation_scale=5,
#     pickable=True,
#     elevation_range=[0, 1000],
#     extruded=True,
#     coverage=1)

layer = pdk.Layer(
    'HeatmapLayer',  # `type` positional argument is here
    region_df,
    get_position=['lon', 'lat'],
    get_weight='count',
    radius=100,
    auto_highlight=True,
    on_click=add_cnt,
    elevation_scale=5,
    pickable=True,
    elevation_range=[0, 1000],
    extruded=True,
    coverage=1)


view_state = compute_view(region_df[['lon', 'lat']])
# view_state.pitch = 50
view_state.zoom = get_zoom_value(region_df, 'lat', 'lon')

# Combined all of it and render a viewport
r = pdk.Deck(map_style=None, layers=[layer], initial_view_state=view_state, tooltip={
        'html': '<b>Users:</b> {count}'
    })



# r.deck_widget.on_click(add_cnt)
st.pydeck_chart(r)

st.write(f"{st.session_state.click_cnt}")




# region_df = filter_df_by_region(df, st.session_state.sec_opt)
# st.write(f'## {st.session_state.sec_opt[1]}')
# st.map(region_df)

# col1, col2 = st.columns(2)
# metric_text1 = f"{len(region_df)} users"
# col1.metric("Unique Individual", metric_text1)
# metric_text2 = f"{np.around(len(region_df)/len(df), 5)*100:.2f}%"
# col2.metric("Percentage", metric_text2)

# if st.session_state.sec_opt[0] != 2:
#     plot_region_piechart(region_df, st.session_state.sec_opt)