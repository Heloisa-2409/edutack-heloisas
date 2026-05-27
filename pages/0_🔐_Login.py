import streamlit as st
import requests
from utils.config import XANO_AUTH_URL as XANO_WORKSPACE_URL
from utils.styles import apply_global_styles

st.set_page_config(page_title="EduTrack AI - Acesso", page_icon="🎓", layout="centered")
apply_global_styles()

# Design & Estilo Customizado
st.markdown("""
    <style>
    .main {
        background-color: #f9fbfd;
    }
    .auth-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 5px;
    }
    .auth-subtitle {
        font-family: 'Inter', sans-serif;
        color: #4B5563;
        text-align: center;
        margin-bottom: 25px;
        font-size: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="auth-title">🎓 EduTrack AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="auth-subtitle">Seu assistente de gestão acadêmica inteligente</p>', unsafe_allow_html=True)

tab_login, tab_cadastro = st.tabs(["🔐 Entrar", "📝 Criar Conta"])

# ── ABA LOGIN ─────────────────────────────────────────────────────────────────
with tab_login:
    with st.form("login_form"):
        email = st.text_input("E-mail", placeholder="seu-email@exemplo.com")
        password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        submitted = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")

        if submitted:
            if email and password:
                login_data = {"email": email, "password": password}
                try:
                    response = requests.post(f"{XANO_WORKSPACE_URL}/auth/login", json=login_data)
                    if response.status_code == 200:
                        data = response.json()
                        token = data.get('authToken')
                        st.session_state['auth_token'] = token
                        headers = {'Authorization': f'Bearer {token}'}
                        user_response = requests.get(f"{XANO_WORKSPACE_URL}/auth/me", headers=headers)
                        if user_response.status_code == 200:
                            st.session_state['user'] = user_response.json()
                        st.success("🎉 Login realizado com sucesso!")
                        st.switch_page("pages/3_📊_Relatórios.py")
                    else:
                        st.error("❌ Credenciais inválidas. Verifique seu e-mail e senha.")
                except Exception as e:
                    st.error(f"❌ Erro ao conectar ao servidor: {e}")
            else:
                st.error("⚠️ Por favor, preencha todos os campos.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔑 Esqueceu sua senha?"):
        st.write("Insira seu e-mail para receber um link de redefinição.")
        reset_email = st.text_input("E-mail cadastrado", key="reset_email_input", placeholder="seu-email@exemplo.com")
        if st.button("Solicitar Redefinição", key="btn_send_reset"):
            if reset_email:
                try:
                    response = requests.get(f"{XANO_WORKSPACE_URL}/reset/request-reset-link", params={"email": reset_email})
                    if response.status_code == 200:
                        st.success("✉️ Link de redefinição enviado para o seu e-mail!")
                    else:
                        st.error("❌ Verifique se o e-mail está correto e cadastrado.")
                except Exception as e:
                    st.error(f"❌ Erro ao conectar ao servidor: {e}")
            else:
                st.error("⚠️ Por favor, digite o seu e-mail.")

# ── ABA CADASTRO ──────────────────────────────────────────────────────────────
with tab_cadastro:
    with st.form("signup_form"):
        name = st.text_input("Nome Completo", placeholder="Ex: Maria Souza")
        email = st.text_input("E-mail", placeholder="seu-email@exemplo.com")
        password = st.text_input("Senha", type="password", placeholder="Mínimo de 8 caracteres")
        submitted = st.form_submit_button("Criar Conta Acadêmica", use_container_width=True, type="primary")

        if submitted:
            if name and email and password:
                if len(password) < 8:
                    st.error("⚠️ A senha deve ter pelo menos 8 caracteres.")
                else:
                    signup_data = {"name": name, "email": email, "password": password}
                    try:
                        response = requests.post(f"{XANO_WORKSPACE_URL}/auth/signup", json=signup_data)
                        if response.status_code == 200:
                            data = response.json()
                            token = data.get('authToken')
                            st.session_state['auth_token'] = token
                            st.session_state['user'] = {"name": name, "email": email}
                            st.success("🎉 Conta criada com sucesso! Você está autenticado.")
                            st.switch_page("pages/3_📊_Relatórios.py")
                        else:
                            try:
                                error_details = response.json()
                                msg = error_details.get('message') or str(error_details)
                                st.error(f"❌ Erro ao cadastrar (código {response.status_code}): {msg}")
                            except Exception:
                                st.error(f"❌ Falha ao cadastrar (código {response.status_code}): {response.text}")
                    except Exception as e:
                        st.error(f"❌ Erro ao conectar ao servidor: {e}")
            else:
                st.error("⚠️ Por favor, preencha todos os campos.")