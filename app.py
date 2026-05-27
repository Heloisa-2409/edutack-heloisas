import streamlit as st

st.set_page_config(page_title="EduTrack AI", page_icon="🎓", layout="wide")

if 'auth_token' not in st.session_state or not st.session_state.get('auth_token'):
    st.switch_page("pages/0_🔐_Login.py")
else:
    st.switch_page("pages/3_📊_Relatórios.py")
