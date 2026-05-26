import streamlit as st
import requests
from datetime import datetime, timedelta
from utils.config import XANO_WORKSPACE_URL, XANO_WORKSPACE_URL_IS_DEFAULT, XANO_WORKSPACE_URL_WARNING

if XANO_WORKSPACE_URL_WARNING:
    st.warning(XANO_WORKSPACE_URL_WARNING)

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Dashboard - EduTrack AI", page_icon="🏠", layout="wide")

# ── Auth Guard ──────────────────────────────────────────────────────────────
if 'auth_token' not in st.session_state or not st.session_state.get('auth_token'):
    st.warning("⚠️ Você precisa fazer o login para acessar esta página.")
    st.page_link("pages/0_🔐_Login.py", label="Ir para Login", icon="🔐")
    st.stop()

# ── Estilo Premium ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700&display=swap');

.main { font-family: 'Inter', sans-serif; }
.page-header {
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #1E3A8A;
    margin-bottom: 0.25rem;
}
.page-sub {
    color: #6B7280;
    font-size: 1rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(135deg, #F9FAFB, #F3F4F6);
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
}
.metric-card .label {
    font-size: 0.9rem;
    color: #4B5563;
    margin-bottom: 0.5rem;
}
.metric-card .value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1E3A8A;
}
.section-header {
    font-family: 'Outfit', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1D4ED8;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
.task-item {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.task-item .due-date {
    font-weight: 600;
}
.due-soon { color: #D97706; }
.due-today { color: #DC2626; }
</style>
""", unsafe_allow_html=True)

# ── Função helper para API ──────────────────────────────────────────────────
def make_xano_request(endpoint, method='GET', data=None):
    """Faz uma requisição para a API Xano com tratamento de 401 automático."""
    url = f"{XANO_WORKSPACE_URL}{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.session_state.get("auth_token", "")}'
    }
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        else:
            return None # Dashboard é somente leitura

        if response.status_code == 401:
            st.session_state.pop('auth_token', None)
            st.error("⏱️ Sessão expirada. Por favor, faça login novamente.")
            st.rerun()

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão: {e}")
        return None

# ── Cabeçalho e Boas-vindas ──────────────────────────────────────────────────
user_name = st.session_state.get('user', {}).get('name', 'Estudante')
st.markdown(f'<h1 class="page-header">Bem-vindo(a) de volta, {user_name}!</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Aqui está um resumo da sua jornada acadêmica.</p>', unsafe_allow_html=True)

# ── Carregar Dados ──────────────────────────────────────────────────────────
with st.spinner("Carregando seu progresso..."):
    subjects = make_xano_request('/subjects') or []
    tasks = make_xano_request('/academic_tasks') or []
    subjects_map = {s['id']: s['name'] for s in subjects}

# ── Calcular Métricas ───────────────────────────────────────────────────────
total_subjects = len(subjects)
total_tasks = len(tasks)
completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
pending_tasks = total_tasks - completed_tasks
progress_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

now = datetime.now()
overdue_tasks = 0
upcoming_tasks = []
for t in tasks:
    if t.get('status') != 'completed' and t.get('due_date'):
        try:
            due = datetime.fromisoformat(t['due_date'].split('T')[0])
            days_left = (due.date() - now.date()).days
            if days_left < 0:
                overdue_tasks += 1
            if 0 <= days_left <= 7: # Próximos 7 dias
                upcoming_tasks.append({**t, 'days_left': days_left})
        except (ValueError, TypeError):
            st.warning(f"A data da tarefa '{t.get('title', 'N/A')}' está em um formato inválido e não pôde ser processada.", icon="⚠️")

# Ordenar tarefas por proximidade
upcoming_tasks.sort(key=lambda x: x['days_left'])


# ── Exibir Métricas ─────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Disciplinas Ativas</div>
        <div class="value">{total_subjects}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Tarefas Pendentes</div>
        <div class="value">{pending_tasks}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Tarefas Atrasadas</div>
        <div class="value">{overdue_tasks}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Progresso Geral</div>
        <div class="value">{progress_percent:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)


# ── Próximas Tarefas ────────────────────────────────────────────────────────
st.markdown('<h2 class="section-header">🗓️ Próximas Tarefas (7 dias)</h2>', unsafe_allow_html=True)

if not upcoming_tasks:
    st.info("🎉 Nenhuma tarefa com prazo para os próximos 7 dias. Bom trabalho!")
else:
    for task in upcoming_tasks[:5]: # Limitar a 5 para não poluir
        days = task['days_left']
        due_text = ""
        css_class = ""
        if days == 0:
            due_text = "Vence Hoje"
            css_class = "due-today"
        elif days == 1:
            due_text = "Vence Amanhã"
            css_class = "due-soon"
        else:
            due_text = f"Vence em {days} dias"
            css_class = "due-soon"

        subject_name = subjects_map.get(task.get('subject_id'), 'N/A')

        st.markdown(f"""
        <div class="task-item">
            <div>
                <strong>{task.get('title', 'N/A')}</strong><br>
                <small>📚 {subject_name}</small>
            </div>
            <div class="due-date {css_class}">{due_text}</div>
        </div>
        """, unsafe_allow_html=True)

    if len(upcoming_tasks) > 5:
        st.page_link("pages/2_📝_Tarefas.py", label="Ver todas as tarefas →", icon="➡️")

st.markdown("---")
st.page_link("pages/1_📚_Disciplinas.py", label="Gerenciar Disciplinas", icon="📚")
st.page_link("pages/2_📝_Tarefas.py", label="Gerenciar Tarefas", icon="📝")