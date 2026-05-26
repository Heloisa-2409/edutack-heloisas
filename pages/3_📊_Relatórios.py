import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.api import make_xano_request

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Relatórios - EduTrack AI", page_icon="📊", layout="wide")

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
.page-header { font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.25rem; }
.page-sub { color: #6B7280; font-size: 0.95rem; margin-bottom: 1.5rem; }
.section-header { font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: #1D4ED8; margin-top: 2rem; margin-bottom: 1rem; }
.progress-container {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-header">📊 Relatórios e Progresso</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Analise seu desempenho acadêmico e o progresso em cada disciplina.</p>', unsafe_allow_html=True)

# ── Carregar Dados ──────────────────────────────────────────────────────────
with st.spinner("Analisando seus dados..."):
    subjects = make_xano_request('/subjects') or []
    tasks = make_xano_request('/academic_tasks') or []
    subjects_map = {s['id']: s['name'] for s in subjects}

if not subjects and not tasks:
    st.info("📊 Não há dados suficientes para gerar relatórios. Comece cadastrando disciplinas e tarefas.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: PROGRESSO POR DISCIPLINA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h2 class="section-header">🚀 Progresso por Disciplina</h2>', unsafe_allow_html=True)

if not subjects:
    st.warning("Nenhuma disciplina cadastrada para exibir o progresso.")
else:
    progress_data = []
    for subject in subjects:
        subject_id = subject['id']
        subject_tasks = [t for t in tasks if t.get('subject_id') == subject_id]
        total_count = len(subject_tasks)
        completed_count = len([t for t in subject_tasks if t.get('status') == 'completed'])
        progress = (completed_count / total_count) if total_count > 0 else 0
        
        progress_data.append({
            "name": subject.get('name', 'N/A'),
            "total": total_count,
            "completed": completed_count,
            "progress": progress
        })

    for data in sorted(progress_data, key=lambda x: x['name']):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{data['name']}**")
                st.progress(data['progress'])
            with col2:
                st.metric(label="Tarefas Concluídas", value=f"{data['completed']}/{data['total']}")

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: HISTÓRICO DE TAREFAS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h2 class="section-header">🗓️ Histórico de Tarefas por Período</h2>', unsafe_allow_html=True)

if not tasks:
    st.warning("Nenhuma tarefa cadastrada para exibir o histórico.")
else:
    # Filtros de período
    today = date.today()
    try:
        last_month_start = today.replace(day=1) - timedelta(days=1)
        start_default = last_month_start.replace(day=1)
    except ValueError: # Lida com meses de diferentes tamanhos
        start_default = today.replace(day=1) - timedelta(days=30)

    f_col1, f_col2 = st.columns(2)
    start_date = f_col1.date_input("Data de Início", value=start_default)
    end_date = f_col2.date_input("Data de Fim", value=today)

    if start_date > end_date:
        st.error("A data de início não pode ser posterior à data de fim.")
    else:
        # Filtrar tarefas pelo prazo (due_date)
        filtered_tasks = []
        for task in tasks:
            if task.get('due_date'):
                try:
                    task_due_date = datetime.fromisoformat(task['due_date'].split('T')[0]).date()
                    if start_date <= task_due_date <= end_date:
                        filtered_tasks.append(task)
                except (ValueError, TypeError):
                    continue
        
        if not filtered_tasks:
            st.info("Nenhuma tarefa encontrada no período selecionado.")
        else:
            # Preparar DataFrame para exibição
            df_tasks = pd.DataFrame(filtered_tasks)
            
            # Mapeamentos para leitura humana
            STATUS_LABELS = { "pending": "Pendente", "in_progress": "Em Andamento", "completed": "Concluída" }
            
            df_tasks['disciplina'] = df_tasks['subject_id'].map(subjects_map).fillna('N/A')
            df_tasks['prazo'] = pd.to_datetime(df_tasks['due_date'], errors='coerce').dt.strftime('%d/%m/%Y')
            df_tasks['status_label'] = df_tasks['status'].map(STATUS_LABELS).fillna(df_tasks['status'])

            # Selecionar e renomear colunas
            df_display = df_tasks[['title', 'disciplina', 'prazo', 'status_label']]
            df_display.columns = ['Título', 'Disciplina', 'Prazo', 'Status']
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)