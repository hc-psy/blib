import streamlit as st


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

    if 'sec_view' not in st.session_state:
        st.session_state.sec_view = False

    if 'sec_opt' not in st.session_state:
        st.session_state.sec_opt = [-1, ""]

    if 'fst_opt' not in st.session_state:
        st.session_state.fst_opt = [-1, ""]
    
    if 'click_cnt' not in st.session_state:
        st.session_state.click_cnt = 0