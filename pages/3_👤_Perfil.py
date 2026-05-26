import streamlit as st
from utils.api import make_xano_request
from datetime import datetime

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Perfil - EduTrack AI", page_icon="👤", layout="wide")
# ── Auth Guard ──────────────────────────────────────────────────────────────
if 'auth_token' not in st.session_state or not st.session_state.get('auth_token'):
    st.warning("⚠️ Você precisa fazer o login para acessar esta página.")
    st.stop()

# ── Estilo Premium ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700&display=swap');
.main { font-family: 'Inter', sans-serif; }
.page-header { font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.25rem; }
.page-sub { color: #6B7280; font-size: 0.95rem; margin-bottom: 1.5rem; }
.profile-name { font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 700; color: #111827; }
.profile-email { color: #6B7280; font-size: 0.95rem; }
.info-card {
    background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
    border-left: 4px solid #3B82F6;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.progress-card {
    background: linear-gradient(135deg, #F0FDF4, #D1FAE5);
    border-left: 4px solid #10B981;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.divider { border: none; border-top: 1px solid #F3F4F6; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.markdown('<h1 class="page-header">👤 Meu Perfil</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-sub">Gerencie suas informações pessoais e acompanhe seu progresso</p>', unsafe_allow_html=True)

# ── Buscar dados do usuário ──────────────────────────────────────────────────
user_data = make_xano_request('/auth/me')

if not user_data:
    st.error("❌ Erro ao carregar dados do perfil. Verifique sua conexão.")
    st.stop()

# ── Buscar dados de disciplinas e tarefas ────────────────────────────────────
subjects = make_xano_request('/subjects') or []
tasks = make_xano_request('/academic_tasks') or []

# ── Calcular estatísticas ────────────────────────────────────────────────────
total_subjects = len(subjects)
total_tasks = len(tasks)
completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
pending_tasks = len([t for t in tasks if t.get('status') == 'pending'])
in_progress_tasks = len([t for t in tasks if t.get('status') == 'in_progress'])
completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

def safe_due_parser(date_str):
    if not date_str: return None
    try:
        return datetime.fromisoformat(date_str.split('T')[0])
    except (ValueError, TypeError):
        return None

now = datetime.now()
overdue_tasks = [
    t for t in tasks
    if t.get('status') != 'completed'
    and safe_due_parser(t.get('due_date')) and safe_due_parser(t.get('due_date')) < now
]

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: INFORMAÇÕES PESSOAIS
# ══════════════════════════════════════════════════════════════════════════════
col_avatar, col_info = st.columns([1, 4])

with col_avatar:
    # Avatar com iniciais
    name = user_data.get('name', 'Usuário')
    initials = ''.join([w[0].upper() for w in name.split()[:2]])
    st.markdown(
        f"""<div style="
            width:80px; height:80px; border-radius:50%;
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            display:flex; align-items:center; justify-content:center;
            font-size:2rem; font-weight:700; color:white;
            margin-top:0.5rem;
        ">{initials}</div>""",
        unsafe_allow_html=True
    )

with col_info:
    st.markdown(f'<p class="profile-name">{user_data.get("name", "N/A")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="profile-email">✉️ {user_data.get("email", "N/A")}</p>', unsafe_allow_html=True)
    status_txt = "🟢 Ativa" if user_data.get('active', True) else "🔴 Inativa"
    st.markdown(f'<p class="profile-email">Status: {status_txt}</p>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: EDITAR PERFIL
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("✏️ Editar Informações do Perfil", expanded=False):
    with st.form("edit_profile_form"):
        ep1, ep2 = st.columns(2)
        with ep1:
            new_name = st.text_input("Nome Completo", value=user_data.get('name', ''))
        with ep2:
            new_email = st.text_input("E-mail", value=user_data.get('email', ''))

        save_profile = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)

        if save_profile:
            if not new_name or not new_email:
                st.error("⚠️ Nome e e-mail são obrigatórios.")
            else:
                profile_data = {"name": new_name, "email": new_email}
                result = make_xano_request('/user/edit_profile', method='PATCH', data=profile_data)
                if result:
                    st.success("✅ Perfil atualizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Falha ao atualizar o perfil.")

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO: ESTATÍSTICAS ACADÊMICAS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📊 Estatísticas Acadêmicas")

mc1, mc2, mc3, mc4, mc5 = st.columns(5)
mc1.metric("📚 Disciplinas", total_subjects)
mc2.metric("📋 Total Tarefas", total_tasks)
mc3.metric("✅ Concluídas", completed_tasks)
mc4.metric("⏳ Pendentes", pending_tasks)
mc5.metric("⚠️ Atrasadas", len(overdue_tasks))

# ── Barra de progresso ───────────────────────────────────────────────────────
if total_tasks > 0:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.subheader("📈 Progresso Geral")
    st.progress(completion_rate / 100)
    st.markdown(f"**{completion_rate:.1f}%** das tarefas concluídas")

    # ── Progresso por disciplina ─────────────────────────────────────────────
    if subjects:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.subheader("📚 Progresso por Disciplina")

        for subject in subjects:
            subject_id = subject.get('id')
            subject_tasks = [t for t in tasks if t.get('subject_id') == subject_id]
            if not subject_tasks:
                continue

            s_done = len([t for t in subject_tasks if t.get('status') == 'completed'])
            s_total = len(subject_tasks)
            s_rate = (s_done / s_total) if s_total > 0 else 0
            s_overdue = [
                t for t in subject_tasks
                if t.get('status') != 'completed'
                and safe_due_parser(t.get('due_date')) and safe_due_parser(t.get('due_date')) < now
            ]

            col_name, col_bar = st.columns([2, 4])
            with col_name:
                overdue_badge = " ⚠️" if s_overdue else ""
                st.markdown(f"**{subject.get('name', 'N/A')}{overdue_badge}**")
                st.caption(f"👨‍🏫 {subject.get('professor', 'N/A')}")
                st.caption(f"{s_done}/{s_total} tarefas")
            with col_bar:
                st.markdown("<br>", unsafe_allow_html=True)
                st.progress(s_rate)
                st.caption(f"{s_rate*100:.0f}% concluído")

# ── Tarefas em Atraso ─────────────────────────────────────────────────────────
if overdue_tasks:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.subheader("🚨 Tarefas em Atraso")
    subjects_map = {s['id']: s['name'] for s in subjects}
    for ot in overdue_tasks:
        due_dt = safe_due_parser(ot.get('due_date'))
        due_str = due_dt.strftime('%d/%m/%Y') if due_dt else 'Data inválida'
        subj_name = subjects_map.get(ot.get('subject_id'), 'N/A')
        st.error(f"🔴 **{ot.get('title')}** — {subj_name} — Prazo: {due_str}")
