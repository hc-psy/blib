import streamlit as st

import pandas as pd
import numpy as np

import database.appdata as db

from utilities.initial import app_init
from utilities.showplot import plot_column_map, plot_region_hist, plot_region_piechart, plot_region_user_time, plot_region_click_time

from components.sidebar import side_bar

app_init()


def correct_metrics(val):
    if val < 1:
        return "< 1"

    return f"{np.around(val, 0):.0f}"


def make_metrics(texts: np.array, metrics: np.array, deltas: np.array, last_vals: np.array):
    cc1, cc2, cc3, cc4 = st.columns(4)
    
    t_metrics = [metrics[0], metrics[1], correct_metrics(metrics[2]), correct_metrics(metrics[3])]
    
    if (deltas == np.array([None, None, None, None])).any():
        cc1.metric(texts[0], f"{t_metrics[0]:.0f}")
        cc2.metric(texts[1], f"{t_metrics[1]:.2f}%")
        cc3.metric(texts[2], t_metrics[2])
        cc4.metric(texts[3], t_metrics[3])
        
        return (metrics, metrics)
    else:
        deltas = metrics - last_vals
        
        cc1.metric(texts[0], f"{t_metrics[0]:.0f}", delta=f"{deltas[0]:.0f} (cf. {st.session_state.last_fst_opt})")
        cc2.metric(texts[1], f"{t_metrics[1]:.2f}%", delta=f"{deltas[1]:.2f}% (cf. {st.session_state.last_fst_opt})")
        cc3.metric(texts[2], t_metrics[2], delta=f"{deltas[2]:.0f} (cf. {st.session_state.last_fst_opt})")
        cc4.metric(texts[3], t_metrics[3], delta=f"{deltas[3]:.0f} (cf. {st.session_state.last_fst_opt})")
        
        return (deltas, metrics)


@st.cache(allow_output_mutation=True)
def fetch_data_ip(data_path1, data_path2, merge_on='ip', sorted_by=""):
    df1 = pd.read_csv(data_path1)
    
    if sorted_by:
        df1 = df1.sort_values(by=[sorted_by])
        df1.reset_index(drop=True)
    
    df2 = pd.read_csv(data_path2)
    df = df1.merge(df2, on=merge_on)
    return df

def filter_df_by_region(df, state_opt: list, base_col_idx = 5):
    level, condition = state_opt
    level = base_col_idx - level
    
    if condition in ['World | Continent', 'World | Contry']:
        return df
    
    return df[df.iloc[:, level] == condition]

st.write(db.TITLE)
st.write(db.DESCRIPTION)

df = fetch_data_ip('cache/ip_geo.csv', 'cache/ip_book_count.csv')
df_day = fetch_data_ip('cache/ip_book_day.csv', 'cache/ip_geo.csv', sorted_by="clickdate")

side_bar(df)

region_df = filter_df_by_region(df, st.session_state.fst_opt)
region_df_day = filter_df_by_region(df_day, st.session_state.fst_opt, 7)


st.write(f'## {st.session_state.fst_opt[1]}')
tb1, tb2, tb3 = st.tabs(["User Analysis 🌿", "Browse Analysis 🍁", "Latent Similarity 🌸"])

with tb1:
    c1, c2 = st.columns(2)
    with c1:
        st.map(region_df)
    with c2:
        st.markdown("# ")
        plot_region_piechart(region_df, st.session_state.fst_opt)


    metric_text1 = f"{len(region_df)}"
    
    metric_text2 = f"{np.around(len(region_df)/len(df), 5)*100:.2f}%"
    
    visitors_per_month = len(region_df)/7
    if visitors_per_month < 1:
        visitors_per_month = "< 1"
        metric_text3 = visitors_per_month
    else:
        visitors_per_month = np.around(visitors_per_month, 0)
        metric_text3 = f"{visitors_per_month:.0f}"
    
    visitors_per_day = len(region_df)/214
    if visitors_per_day < 1:
        visitors_per_day = "< 1"
        metric_text4 = visitors_per_day
    else:
        visitors_per_day = np.around(visitors_per_day, 0)
        metric_text4 = f"{visitors_per_day:.0f}"
    
    
    st.write("#### ")
    tb1_metric_texts = np.array(["Total Visitors",
                                 "Ratio (To All Visitors)",
                                 "Visitors (Monthly Avg.)",
                                 "Visitors (Daily Avg.)"])
    
    tb1_metric_vals = np.array([int(len(region_df)),
                                np.around(len(region_df)/len(df), 5)*100,
                                len(region_df)/7,
                                len(region_df)/214])
    
    # session state is call by value
    metrics_pkg1 = make_metrics(tb1_metric_texts, tb1_metric_vals, st.session_state.tb1_deltas, st.session_state.tb1_last_vals)
    st.session_state.tb1_deltas = metrics_pkg1[0]
    st.session_state.tb1_last_vals = metrics_pkg1[1]
    
    plot_region_user_time(region_df_day)

        
with tb2:
    c1, c2 = st.columns(2)
    
    with c1:
        with st.expander("Control Board", expanded=False):
            st.session_state.col_h = st.select_slider('Height',
                                                      options=[i for i in range(2, 13)],
                                                      value=4)
            st.session_state.col_r = st.select_slider('Radius',
                                                      options=[i/2 for i in range(1, 13)],
                                                      value=1)
        plot_column_map(region_df, 
                        cur_elevation_scale=st.session_state.col_h*2000,
                        cur_radius=st.session_state.col_r*2000)
    with c2:
        st.markdown("# ")
        st.markdown("# ")
        plot_region_piechart(region_df,
                             st.session_state.fst_opt,
                             is_click=True)
        
    st.write("#### ")
                
    tb2_metric_texts = np.array(["Total Browse",
                   "Ratio (To All Browses)",
                   "Browses (Monthly Avg.)",
                   "Browses (Daily Avg.)"])
    
    tb2_metric_vals = np.array([region_df["count"].sum(),
                     np.around(region_df["count"].sum() / df["count"].sum(), 5)*100,
                     region_df["count"].sum() / 7,
                     region_df["count"].sum() / 214])
    
    metrics_pkg2 = make_metrics(tb2_metric_texts, tb2_metric_vals, st.session_state.tb2_deltas, st.session_state.tb2_last_vals)
    st.session_state.tb2_deltas = metrics_pkg2[0]
    st.session_state.tb2_last_vals = metrics_pkg2[1]
    
    plot_region_click_time(region_df_day)
    plot_region_hist(region_df)




# update last first option
st.session_state.last_fst_opt = st.session_state.fst_opt[1]