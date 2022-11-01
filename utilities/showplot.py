import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pydeck as pdk
from pydeck.data_utils import compute_view

import streamlit as st
from streamlit.elements.map import _get_zoom_level

import numpy as np

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


def plot_region_piechart(df, state_opt: list, base_col_idx = 5, is_click=False):
    level, condition = state_opt
    level = base_col_idx - level
    
    tgt_col = df.columns[level] if (condition == 'World | Continent' or state_opt[0] == 2) else df.columns[level - 1]

    if is_click:
        tmp_df = df.groupby(tgt_col)["count"].sum().reset_index(name='Clicks')
        tmp_df.loc[tmp_df['Clicks'] < tmp_df['Clicks'].sum()/100, tgt_col] = f'Other {tgt_col.lower()}'
        val = 'Clicks'
    else:
        tmp_df = df.groupby([tgt_col])[tgt_col].count().reset_index(name='Users')
        tmp_df.loc[tmp_df['Users'] < tmp_df['Users'].sum()/100, tgt_col] = f'Other {tgt_col.lower()}'
        val = 'Users'
    
    fig = px.pie(tmp_df, values=val, names=tgt_col, hole=.3, color_discrete_sequence=px.colors.diverging.Geyser)
    fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True)
    
    
def plot_region_hist(df):
    
    fig = go.Figure([go.Histogram(x=df["count"], cumulative_enabled=False)])
    fig.update_yaxes(type="log")
    fig.update_layout(xaxis_title="Click Times", yaxis_title="Frequency")
    
    st.plotly_chart(fig, use_container_width=True)


def plot_region_user_time(df):
    tgt_col = "clickdate"
    
    tmp1_df = df.groupby([tgt_col])[tgt_col].count().reset_index(name='Users')
    
    tmp2_df = df.drop_duplicates("ip")
    tmp2_df = tmp2_df.groupby([tgt_col])[tgt_col].count().reset_index(name='Users')
    tmp2_df['Cumsum'] = tmp2_df["Users"].cumsum()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=tmp1_df["clickdate"], y=tmp1_df["Users"], name="Visitors Per Day"),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=tmp2_df["clickdate"], y=tmp2_df["Cumsum"], name="Cumulative New Visitors"),
        secondary_y=True,
    )

    # Add figure title
    # fig.update_layout(
    #     title_text="Double Y Axis Example",
    # )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(rangemode='tozero')
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Visitors Per Day",
                     secondary_y=False,
                     showgrid=True, 
                     gridwidth=0.1)
    
    fig.update_yaxes(title_text="Cumulative New Visitors",
                     secondary_y=True,
                     showgrid=False,
                     gridwidth=0.1)
    
    st.plotly_chart(fig, use_container_width=True)


def plot_region_click_time(df):
    tgt_col = "clickdate"
    
    tmp1_df = df.groupby([tgt_col])["count"].sum().reset_index(name='Browses')
    
    tmp1_df['Cumsum'] =  tmp1_df['Browses'].cumsum()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=tmp1_df["clickdate"], y=tmp1_df["Browses"], name="Browses Per Day"),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=tmp1_df["clickdate"], y=tmp1_df["Cumsum"], name="Cumulative Browses"),
        secondary_y=True,
    )

    # Add figure title
    # fig.update_layout(
    #     title_text="Double Y Axis Example",
    # )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(rangemode='tozero')
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Browses Per Day",
                     secondary_y=False,
                     showgrid=True, 
                     gridwidth=0.1)
    
    fig.update_yaxes(title_text="Cumulative Browses",
                     secondary_y=True,
                     showgrid=False,
                     gridwidth=0.1)
    
    st.plotly_chart(fig, use_container_width=True)






def plot_column_map(df_in, cur_elevation_scale=8000, cur_radius=2000):
    
    df = df_in.copy()
    df.loc[:, 'ln_count'] = list(df.apply(lambda x: np.log(x['count'])+1, axis=1))

    layer = pdk.Layer(
        'ColumnLayer',  # `type` positional argument is here
        df,
        get_position=['lon', 'lat'],
        get_elevation='ln_count',
        radius=cur_radius,
        auto_highlight=True,
        elevation_scale=cur_elevation_scale,
        pickable=True,
        get_fill_color='[180, ln_count*25, 200+ln_count*5, 120]',
    )
    
    view_state = compute_view(df[['lon', 'lat']])
    view_state.pitch = 35
    view_state.bearing = -10
    view_state.latitude = view_state.latitude
    view_state.longitude = view_state.longitude
    view_state.zoom = get_zoom_value(df, 'lat', 'lon')

    # Combined all of it and render a viewport
    r = pdk.Deck(map_style=None, layers=[layer], initial_view_state=view_state, tooltip={
            'html': '<b>Click Times:</b> {count}',
            'style': {
                'color': 'white'
            }
        })

    st.pydeck_chart(r)