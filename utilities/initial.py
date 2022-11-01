import streamlit as st
import numpy as np

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def app_init():
    st.set_page_config(
        page_title="NTU Buddist Library User Study",
        page_icon="⚱️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    local_css("/home/ryvn/desktop/blib/utilities/style.css")
        
    if 'fst_opt' not in st.session_state:
        st.session_state.fst_opt = [-1, ""]

    if 'last_fst_opt' not in st.session_state:
        st.session_state.last_fst_opt = ""
    
    if 'col_h' not in st.session_state:
        st.session_state.col_h = 4
    
    if 'col_r' not in st.session_state:
        st.session_state.col_r = 1
    
    if 'tb1_deltas' not in st.session_state:
        st.session_state.tb1_deltas = np.array([None, None, None, None])
    
    if 'tb1_last_vals' not in st.session_state:
        st.session_state.tb1_last_vals = np.array([None, None, None, None])
    
    if 'tb2_deltas' not in st.session_state:
        st.session_state.tb2_deltas = np.array([None, None, None, None])
    
    if 'tb2_last_vals' not in st.session_state:
        st.session_state.tb2_last_vals = np.array([None, None, None, None])