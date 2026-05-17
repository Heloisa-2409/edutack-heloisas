import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Xano
XANO_API_KEY = os.getenv('XANO_API_KEY')
XANO_WORKSPACE_URL = os.getenv('XANO_WORKSPACE_URL', 'https://x8ki-letl-twmt.xano.io/api')

# Configuração da Página (Título na aba do navegador)
st.set_page_config(page_title="EduTrack AI", page_icon="🎓")

# Funções Helper para API
def make_xano_request(endpoint, method='GET', data=None, headers=None):
    """Faz uma requisição para a API Xano com tratamento de erro aprimorado."""
    url = f"{XANO_WORKSPACE_URL}{endpoint}"
    default_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.session_state.get("auth_token", "")}'
    }
    if headers:
        default_headers.update(headers)

    try:
        if method == 'GET':
            response = requests.get(url, headers=default_headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=default_headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, headers=default_headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=default_headers)
        else:
            st.error(f"Método HTTP desconhecido: {method}")
            return None

        # Lança uma exceção para códigos de erro (4xx ou 5xx)
        response.raise_for_status()

        # Para respostas bem-sucedidas que não têm conteúdo (ex: DELETE)
        if response.status_code == 204:
            return {"status": "success"}
        
        return response.json()

    except requests.exceptions.HTTPError as err:
        try:
            error_details = err.response.json()
            st.error(f"Erro da API: {error_details.get('message', 'Resposta de erro sem mensagem.')}")
        except ValueError:
            st.error(f"Erro na API (código {err.response.status_code}). A resposta não pôde ser decodificada.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {e}")
        return None

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