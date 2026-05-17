import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Xano
XANO_WORKSPACE_URL = os.getenv('XANO_WORKSPACE_URL', 'https://x8ki-letl-twmt.xano.io/api')

st.title("🔐 Login - EduTrack AI")

# Formulário de Login
with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    submitted = st.form_submit_button("Entrar")

    if submitted:
        if email and password:
            # Fazer chamada para API de login
            login_data = {"email": email, "password": password}
            response = requests.post(f"{XANO_WORKSPACE_URL}/auth/login", json=login_data)

            if response.status_code == 200:
                data = response.json()
                st.session_state['auth_token'] = data.get('authToken')
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas. Tente novamente.")
        else:
            st.error("Preencha todos os campos.")

# Link para cadastro
st.markdown("---")
st.write("Não tem conta? [Cadastre-se](#)")  # Temporário