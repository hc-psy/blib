import streamlit as st 
 
def make_dropdown_list(df, col_name, begin_with=[], cond_col_name=-1, cond_col_value=-1):
    if cond_col_name != -1 and cond_col_value != -1:
        col_list = (df[df[cond_col_name] == cond_col_value])[col_name].tolist()
    else:
        col_list = df[col_name].tolist()
    
    col_set = sorted(set(col_list))
    return begin_with + list(col_set)


def side_bar(df):
    with st.sidebar:
        
        st.write("### Select Region")
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