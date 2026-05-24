import streamlit as st
import os
from dotenv import load_dotenv
from utils.api import make_xano_request

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Xano
XANO_API_KEY = os.getenv('XANO_API_KEY')

# Configuração da Página (Título na aba do navegador)
st.set_page_config(page_title="EduTrack AI", page_icon="🎓")

def is_authenticated():
    """Verifica se o usuário está autenticado"""
    return 'auth_token' in st.session_state and st.session_state['auth_token']

# Verificar autenticação
if not is_authenticated():
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
                response_data = make_xano_request('/auth/login', method='POST', data=login_data)

                if response_data and response_data.get('authToken'):
                    st.session_state['auth_token'] = response_data.get('authToken')
                    st.success("Login realizado com sucesso!")
                    st.rerun()
            else:
                st.error("Preencha todos os campos.")

    st.stop()  # Para a execução se não estiver logado

# Título Principal
st.title("🎓 EduTrack AI")

# Botão de Logout
if st.sidebar.button("Logout"):
    if 'auth_token' in st.session_state:
        del st.session_state['auth_token']
    st.rerun()

# Conteúdo da Página Principal (Dashboard)
st.write("Bem-vindo ao seu assistente acadêmico!")

# Buscar dados reais das APIs
subjects = make_xano_request('/subjects')
tasks = make_xano_request('/academic_tasks')

# Calcular métricas
subjects_count = len(subjects) if subjects else 0
tasks_count = len(tasks) if tasks else 0
completed_tasks = len([t for t in (tasks or []) if t.get('status') == 'completed'])
pending_tasks = len([t for t in (tasks or []) if t.get('status') == 'pending'])

# Exemplo de Métrica Visual
col1, col2, col3 = st.columns(3)
col1.metric("Disciplinas Ativas", subjects_count)
col2.metric("Tarefas Pendentes", pending_tasks)
col3.metric("Tarefas Concluídas", completed_tasks)