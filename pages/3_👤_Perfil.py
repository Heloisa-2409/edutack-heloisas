import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Xano
XANO_WORKSPACE_URL = os.getenv('XANO_WORKSPACE_URL', 'https://x8ki-letl-twmt.xano.io/api')

# Função helper para API
def make_xano_request(endpoint, method='GET', data=None, headers=None):
    """Faz uma requisição para a API Xano"""
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
            return None

        return response.json() if response.status_code == 200 else None
    except:
        return None

st.title("👤 Meu Perfil")

# Buscar dados do usuário
user_data = make_xano_request('/auth/me')

if user_data:
    # Informações básicas do usuário
    st.subheader("Informações Pessoais")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Email:** {user_data.get('email', 'N/A')}")
        st.write(f"**Nome:** {user_data.get('name', 'N/A')}")

    with col2:
        st.write(f"**ID:** {user_data.get('id', 'N/A')}")
        st.write(f"**Status:** {'Ativo' if user_data.get('active') else 'Inativo'}")

    # Estatísticas acadêmicas
    st.markdown("---")
    st.subheader("📊 Estatísticas Acadêmicas")

    # Buscar dados para estatísticas
    subjects = make_xano_request('/subjects') or []
    tasks = make_xano_request('/academic_tasks') or []

    # Calcular estatísticas
    total_subjects = len(subjects)
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
    pending_tasks = len([t for t in tasks if t.get('status') == 'pending'])

    # Métricas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Disciplinas", total_subjects)

    with col2:
        st.metric("Total de Tarefas", total_tasks)

    with col3:
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric("Tarefas Concluídas", f"{completed_tasks} ({completion_rate:.1f}%)")

    with col4:
        st.metric("Tarefas Pendentes", pending_tasks)

    # Gráfico de progresso (simples)
    if total_tasks > 0:
        st.markdown("---")
        st.subheader("📈 Progresso Geral")

        progress_bar = st.progress(completion_rate / 100)
        st.write(f"Progresso: {completion_rate:.1f}% das tarefas concluídas")

    # Disciplinas recentes
    if subjects:
        st.markdown("---")
        st.subheader("📚 Minhas Disciplinas")

        for subject in subjects[:5]:  # Mostrar até 5 disciplinas
            with st.expander(f"📖 {subject.get('name', 'Sem nome')}", expanded=False):
                st.write(f"**Professor:** {subject.get('professor', 'N/A')}")
                st.write(f"**Dia da Aula:** {subject.get('day_of_week', 'N/A')}")

                # Contar tarefas desta disciplina
                subject_tasks = [t for t in tasks if t.get('subject_id') == subject.get('id')]
                completed_subject_tasks = len([t for t in subject_tasks if t.get('status') == 'completed'])

                if subject_tasks:
                    st.write(f"**Tarefas:** {len(subject_tasks)} total, {completed_subject_tasks} concluídas")

    # Configurações
    st.markdown("---")
    st.subheader("⚙️ Configurações")

    with st.expander("🔒 Segurança", expanded=False):
        st.write("**Último login:** Dados não disponíveis na API atual")
        st.write("**Status da conta:** Ativa")

        if st.button("Alterar Senha"):
            st.info("Funcionalidade será implementada em breve")

    with st.expander("🔔 Notificações", expanded=False):
        email_notifications = st.checkbox("Receber notificações por email", value=True)
        task_reminders = st.checkbox("Lembretes de tarefas pendentes", value=True)

        if st.button("Salvar Preferências"):
            st.success("Preferências salvas! (Simulação)")

else:
    st.error("Erro ao carregar dados do perfil. Verifique sua conexão.")