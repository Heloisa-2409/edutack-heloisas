import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Xano
XANO_WORKSPACE_URL = os.getenv('XANO_WORKSPACE_URL', 'https://x8ki-letl-twmt.xano.io/api')

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
.divider { border: none; border-top: 1px solid #F3F4F6; margin: 1rem 0; }
.section-header { font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.75rem; margin-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Função helper para API ──────────────────────────────────────────────────
def make_xano_request(endpoint, method='GET', data=None):
    url = f"{XANO_WORKSPACE_URL}{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.session_state.get("auth_token", "")}'
    }
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        else:
            return None

        if response.status_code == 401:
            st.session_state.pop('auth_token', None)
            st.error("⏱️ Sessão expirada. Por favor, faça login novamente.")
            st.rerun()

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro de conexão: {e}")
        return None

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-header">📊 Relatórios de Desempenho</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Analise seu progresso acadêmico ao longo do tempo.</p>', unsafe_allow_html=True)

# ── Carregar dados ──────────────────────────────────────────────────────────
with st.spinner("Carregando dados..."):
    tasks = make_xano_request('/academic_tasks') or []
    subjects = make_xano_request('/subjects') or []

if not tasks or not subjects:
    st.info("📊 Não há dados suficientes para gerar relatórios. Cadastre disciplinas e tarefas para começar.")
    st.stop()

subjects_map = {s['id']: s['name'] for s in subjects}

# ── Filtros de Período ──────────────────────────────────────────────────────
st.markdown('<p class="section-header">🗓️ Filtro de Período</p>', unsafe_allow_html=True)
today = datetime.now().date()
col1, col2 = st.columns(2)
start_date = col1.date_input("Data de Início", today - timedelta(days=30))
end_date = col2.date_input("Data de Fim", today)

if start_date > end_date:
    st.error("A data de início não pode ser posterior à data de fim.")
    st.stop()

# ── Processamento e Filtragem dos Dados ─────────────────────────────────────
df_tasks = pd.DataFrame(tasks)
df_tasks['due_date'] = pd.to_datetime(df_tasks['due_date'], errors='coerce').dt.date
df_tasks['completed'] = df_tasks['status'] == 'completed'
df_tasks['disciplina'] = df_tasks['subject_id'].map(subjects_map)

filtered_df = df_tasks[
    (df_tasks['due_date'] >= start_date) &
    (df_tasks['due_date'] <= end_date)
].copy()

st.markdown('<hr class="divider">', unsafe_allow_html=True)

if filtered_df.empty:
    st.info(f"Nenhuma tarefa com prazo entre **{start_date.strftime('%d/%m/%Y')}** e **{end_date.strftime('%d/%m/%Y')}**.")
else:
    # ── Métricas Gerais do Período ───────────────────────────────────────────
    st.markdown('<p class="section-header">Resumo do Período</p>', unsafe_allow_html=True)
    total_tasks_period = len(filtered_df)
    completed_tasks_period = filtered_df['completed'].sum()
    completion_rate_period = (completed_tasks_period / total_tasks_period * 100) if total_tasks_period > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Tarefas no Período", total_tasks_period)
    m2.metric("Tarefas Concluídas", f"{completed_tasks_period}")
    m3.metric("Taxa de Conclusão", f"{completion_rate_period:.1f}%")

    # ── Gráfico de Tarefas por Dia ───────────────────────────────────────────
    st.markdown('<p class="section-header">Tarefas Concluídas por Dia</p>', unsafe_allow_html=True)
    tasks_by_day = filtered_df[filtered_df['completed']].groupby('due_date').size().rename("Tarefas Concluídas")
    
    if not tasks_by_day.empty:
        st.bar_chart(tasks_by_day)
    else:
        st.write("Nenhuma tarefa concluída neste período para exibir no gráfico.")

    # ── Progresso por Disciplina no Período ──────────────────────────────────
    st.markdown('<p class="section-header">Progresso por Disciplina no Período</p>', unsafe_allow_html=True)
    
    progress_by_subject = filtered_df.groupby('disciplina').agg(
        total=('id', 'count'),
        concluidas=('completed', 'sum')
    ).reset_index()

    if progress_by_subject.empty:
        st.write("Nenhum progresso para exibir.")
    else:
        for _, row in progress_by_subject.iterrows():
            subject_name = row['disciplina']
            total = row['total']
            concluidas = row['concluidas']
            rate = (concluidas / total) if total > 0 else 0

            st.markdown(f"**{subject_name}**")
            st.progress(rate, text=f"{concluidas} de {total} tarefas concluídas ({rate:.0%})")
            st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)